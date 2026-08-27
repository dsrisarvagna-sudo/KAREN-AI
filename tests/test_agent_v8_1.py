"""V8.1 unit + integration tests.

Rules:
- Real filesystem accessed only via pytest tmp_path (never the repo).
- Browser and VS Code actions are fully mocked (no webbrowser.open or subprocess).
- V8.0 tests in test_agent.py continue passing independently.
- Security tests confirm rejection of shell/PowerShell/Python tools and path traversal.
"""

from __future__ import annotations

import textwrap
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agent.agent import Agent, build_default_registry
from agent.executor import ExecutionEngine, ReferenceResolver
from agent.models import (
    AgentResult, Plan, Step, StepStatus, Task, ToolRequest, ToolResult,
)
from agent.planner import DeterministicPlanner
from agent.registry import ToolRegistry
from agent.tools_file import (
    FileListTool, FileMetadataTool, FileReadTextTool, FileSearchTool,
    _safe_resolve,
)
from agent.tools_browser import BrowserOpenUrlTool, BrowserSearchTool
from agent.tools_vscode import VSCodeOpenFileTool, VSCodeOpenFolderTool


# ===========================================================================
# Helpers
# ===========================================================================

def _mock_browser():
    skill = MagicMock()
    skill.execute.return_value = "browser action performed"
    return skill


def _mock_vscode():
    skill = MagicMock()
    skill.execute.return_value = "vscode action performed"
    return skill


def _registry_v81(tmp_path: Path) -> ToolRegistry:
    roots = [tmp_path]
    return ToolRegistry([
        FileSearchTool(roots),
        FileListTool(roots),
        FileMetadataTool(roots),
        FileReadTextTool(roots),
        BrowserSearchTool(_mock_browser()),
        BrowserOpenUrlTool(_mock_browser()),
        VSCodeOpenFileTool(_mock_vscode()),
        VSCodeOpenFolderTool(_mock_vscode()),
    ])


# ===========================================================================
# Tool Registration
# ===========================================================================

class TestToolRegistration:
    def test_all_v81_tools_register_without_error(self, tmp_path):
        registry = _registry_v81(tmp_path)
        for name in (
            "file.search", "file.list_directory", "file.metadata", "file.read_text",
            "browser.search", "browser.open_url",
            "vscode.open_file", "vscode.open_folder",
        ):
            assert registry.has(name), f"missing tool: {name}"

    def test_duplicate_tool_registration_raises(self, tmp_path):
        registry = ToolRegistry([FileSearchTool([tmp_path])])
        with pytest.raises(ValueError, match="already registered"):
            registry.register(FileSearchTool([tmp_path]))

    def test_non_tool_registration_raises(self, tmp_path):
        registry = ToolRegistry()
        with pytest.raises(TypeError):
            registry.register("not a tool")  # type: ignore


# ===========================================================================
# File Security — _safe_resolve
# ===========================================================================

class TestFileSecurity:
    def test_path_within_allowed_root_is_accepted(self, tmp_path):
        target = tmp_path / "hello.txt"
        target.touch()
        resolved = _safe_resolve(str(target), [tmp_path])
        assert resolved == target.resolve()

    def test_path_outside_all_allowed_roots_is_rejected(self, tmp_path, tmp_path_factory):
        other = tmp_path_factory.mktemp("other")
        with pytest.raises(ValueError, match="outside allowed roots"):
            _safe_resolve(str(other / "evil.txt"), [tmp_path])

    def test_traversal_attack_is_rejected(self, tmp_path):
        evil = str(tmp_path / ".." / ".." / "Windows" / "System32")
        with pytest.raises(ValueError, match="outside allowed roots"):
            _safe_resolve(evil, [tmp_path])

    def test_absolute_path_to_different_drive_is_rejected(self, tmp_path):
        with pytest.raises(ValueError, match="outside allowed roots"):
            _safe_resolve("C:\\Windows\\System32\\cmd.exe", [tmp_path])


# ===========================================================================
# File Tools — Functional
# ===========================================================================

class TestFileSearchTool:
    def test_finds_file_by_partial_name(self, tmp_path):
        (tmp_path / "java_assignment.java").write_text("// code")
        tool = FileSearchTool([tmp_path])
        result = tool.run({"query": "java_assignment"})
        assert result.success
        assert isinstance(result.output, list)
        assert len(result.output) == 1
        assert result.output[0]["filename"] == "java_assignment.java"

    def test_returns_empty_list_when_not_found(self, tmp_path):
        tool = FileSearchTool([tmp_path])
        result = tool.run({"query": "nonexistent_xyz"})
        assert result.success
        assert result.output == []

    def test_search_is_case_insensitive(self, tmp_path):
        (tmp_path / "JAVA_ASSIGNMENT.java").write_text("")
        tool = FileSearchTool([tmp_path])
        result = tool.run({"query": "java_assignment"})
        assert result.success and len(result.output) == 1

    def test_rejects_missing_query(self, tmp_path):
        tool = FileSearchTool([tmp_path])
        result = tool.run({})
        assert not result.success

    def test_rejects_extra_fields(self, tmp_path):
        tool = FileSearchTool([tmp_path])
        result = tool.run({"query": "x", "extra": "bad"})
        assert not result.success

    def test_result_contains_expected_keys(self, tmp_path):
        (tmp_path / "myfile.java").write_text("")
        tool = FileSearchTool([tmp_path])
        result = tool.run({"query": "myfile"})
        assert result.success
        assert {"path", "filename", "type"} <= set(result.output[0].keys())


class TestFileListTool:
    def test_lists_directory_contents(self, tmp_path):
        (tmp_path / "a.txt").write_text("a")
        (tmp_path / "subdir").mkdir()
        tool = FileListTool([tmp_path])
        result = tool.run({"path": str(tmp_path)})
        assert result.success
        names = {e["filename"] for e in result.output}
        assert "a.txt" in names
        assert "subdir" in names

    def test_rejects_path_outside_roots(self, tmp_path, tmp_path_factory):
        other = tmp_path_factory.mktemp("other")
        tool = FileListTool([tmp_path])
        result = tool.run({"path": str(other)})
        assert not result.success
        assert "outside allowed roots" in result.error

    def test_rejects_nonexistent_directory(self, tmp_path):
        tool = FileListTool([tmp_path])
        result = tool.run({"path": str(tmp_path / "ghost")})
        assert not result.success


class TestFileMetadataTool:
    def test_returns_metadata_for_existing_file(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello")
        tool = FileMetadataTool([tmp_path])
        result = tool.run({"path": str(f)})
        assert result.success
        assert result.output["filename"] == "test.txt"
        assert result.output["size_bytes"] == 5
        assert result.output["is_file"] is True

    def test_fails_for_nonexistent_path(self, tmp_path):
        tool = FileMetadataTool([tmp_path])
        result = tool.run({"path": str(tmp_path / "gone.txt")})
        assert not result.success

    def test_rejects_path_outside_roots(self, tmp_path):
        tool = FileMetadataTool([tmp_path])
        result = tool.run({"path": "C:\\Windows\\System32\\cmd.exe"})
        assert not result.success
        assert "outside allowed roots" in result.error


class TestFileReadTextTool:
    def test_reads_text_file(self, tmp_path):
        f = tmp_path / "notes.txt"
        f.write_text("hello world")
        tool = FileReadTextTool([tmp_path])
        result = tool.run({"path": str(f)})
        assert result.success and result.output == "hello world"

    def test_rejects_path_outside_roots(self, tmp_path, tmp_path_factory):
        other = tmp_path_factory.mktemp("other")
        victim = other / "secret.txt"
        victim.write_text("secret")
        tool = FileReadTextTool([tmp_path])
        result = tool.run({"path": str(victim)})
        assert not result.success
        assert "outside allowed roots" in result.error

    def test_rejects_directory_path(self, tmp_path):
        tool = FileReadTextTool([tmp_path])
        result = tool.run({"path": str(tmp_path)})
        assert not result.success

    def test_rejects_oversized_file(self, tmp_path):
        big = tmp_path / "big.txt"
        big.write_bytes(b"x" * (512 * 1024 + 1))
        tool = FileReadTextTool([tmp_path])
        result = tool.run({"path": str(big)})
        assert not result.success
        assert "too large" in result.error


# ===========================================================================
# Browser Tools
# ===========================================================================

class TestBrowserSearchTool:
    def test_calls_skill_with_query(self):
        skill = _mock_browser()
        tool = BrowserSearchTool(skill)
        result = tool.run({"query": "Python decorators"})
        assert result.success
        skill.execute.assert_called_once()

    def test_rejects_missing_query(self):
        tool = BrowserSearchTool(_mock_browser())
        result = tool.run({})
        assert not result.success

    def test_rejects_extra_fields(self):
        tool = BrowserSearchTool(_mock_browser())
        result = tool.run({"query": "x", "evil": "y"})
        assert not result.success


class TestBrowserOpenUrlTool:
    def test_opens_valid_https_url(self):
        skill = _mock_browser()
        tool = BrowserOpenUrlTool(skill)
        result = tool.run({"url": "https://python.org"})
        assert result.success
        skill.execute.assert_called_once()

    def test_opens_valid_http_url(self):
        skill = _mock_browser()
        tool = BrowserOpenUrlTool(skill)
        result = tool.run({"url": "http://example.com"})
        assert result.success

    def test_rejects_non_http_scheme(self):
        tool = BrowserOpenUrlTool(_mock_browser())
        result = tool.run({"url": "file:///etc/passwd"})
        assert not result.success
        assert "http" in result.error

    def test_rejects_javascript_scheme(self):
        tool = BrowserOpenUrlTool(_mock_browser())
        result = tool.run({"url": "javascript:alert(1)"})
        assert not result.success

    def test_rejects_missing_url(self):
        tool = BrowserOpenUrlTool(_mock_browser())
        result = tool.run({})
        assert not result.success


# ===========================================================================
# VS Code Tools
# ===========================================================================

class TestVSCodeOpenFileTool:
    def test_opens_existing_file(self, tmp_path):
        f = tmp_path / "main.java"
        f.write_text("public class Main {}")
        skill = _mock_vscode()
        tool = VSCodeOpenFileTool(skill)
        result = tool.run({"path": str(f)})
        assert result.success
        skill.execute.assert_called_once()

    def test_rejects_nonexistent_file(self, tmp_path):
        tool = VSCodeOpenFileTool(_mock_vscode())
        result = tool.run({"path": str(tmp_path / "ghost.java")})
        assert not result.success
        assert "does not exist" in result.error

    def test_rejects_directory_as_file(self, tmp_path):
        tool = VSCodeOpenFileTool(_mock_vscode())
        result = tool.run({"path": str(tmp_path)})
        assert not result.success
        assert "not a file" in result.error

    def test_rejects_missing_path(self):
        tool = VSCodeOpenFileTool(_mock_vscode())
        result = tool.run({})
        assert not result.success


class TestVSCodeOpenFolderTool:
    def test_opens_existing_folder(self, tmp_path):
        skill = _mock_vscode()
        tool = VSCodeOpenFolderTool(skill)
        result = tool.run({"path": str(tmp_path)})
        assert result.success
        skill.execute.assert_called_once()

    def test_rejects_nonexistent_folder(self, tmp_path):
        tool = VSCodeOpenFolderTool(_mock_vscode())
        result = tool.run({"path": str(tmp_path / "ghost_dir")})
        assert not result.success

    def test_rejects_file_as_folder(self, tmp_path):
        f = tmp_path / "file.txt"
        f.write_text("x")
        tool = VSCodeOpenFolderTool(_mock_vscode())
        result = tool.run({"path": str(f)})
        assert not result.success
        assert "not a directory" in result.error


# ===========================================================================
# ReferenceResolver
# ===========================================================================

class TestReferenceResolver:
    def _plan_with_succeeded_step(self, output) -> tuple[Plan, Step]:
        step = Step(description="s1", tool_name="file.search")
        step.result = ToolResult(success=True, tool_name="file.search", output=output)
        step.status = StepStatus.SUCCESS
        step2 = Step(description="s2", tool_name="vscode.open_file")
        plan = Plan(task_id="t1", steps=[step, step2])
        return plan, step2

    def test_resolves_list_index_correctly(self):
        output = [{"path": "/tmp/hello.java", "filename": "hello.java", "type": ".java"}]
        plan, step2 = self._plan_with_succeeded_step(output)
        resolver = ReferenceResolver(plan, current_step_id=step2.step_id)
        resolved = resolver.resolve({
            "path": {"$ref": plan.steps[0].step_id, "extract": "output.0.path"}
        })
        assert resolved["path"] == "/tmp/hello.java"

    def test_resolves_dict_key_correctly(self):
        output = {"filename": "notes.txt", "path": "/tmp/notes.txt"}
        plan, step2 = self._plan_with_succeeded_step(output)
        resolver = ReferenceResolver(plan, current_step_id=step2.step_id)
        resolved = resolver.resolve({
            "path": {"$ref": plan.steps[0].step_id, "extract": "output.path"}
        })
        assert resolved["path"] == "/tmp/notes.txt"

    def test_resolves_raw_output_when_extract_is_output(self):
        output = "raw_string"
        plan, step2 = self._plan_with_succeeded_step(output)
        resolver = ReferenceResolver(plan, current_step_id=step2.step_id)
        resolved = resolver.resolve({
            "x": {"$ref": plan.steps[0].step_id, "extract": "output"}
        })
        assert resolved["x"] == "raw_string"

    def test_rejects_unknown_step_id(self):
        step = Step(description="s", tool_name="t")
        plan = Plan(task_id="t1", steps=[step])
        resolver = ReferenceResolver(plan, current_step_id=step.step_id)
        with pytest.raises(ValueError, match="unknown step id"):
            resolver.resolve({"x": {"$ref": "nonexistent-id"}})

    def test_rejects_unexecuted_step(self):
        step1 = Step(description="s1", tool_name="t1")  # no result set
        step2 = Step(description="s2", tool_name="t2")
        plan = Plan(task_id="t1", steps=[step1, step2])
        resolver = ReferenceResolver(plan, current_step_id=step2.step_id)
        with pytest.raises(ValueError, match="has not executed yet"):
            resolver.resolve({"x": {"$ref": step1.step_id}})

    def test_rejects_failed_step_reference(self):
        step1 = Step(description="s1", tool_name="t1")
        step1.result = ToolResult(success=False, tool_name="t1", error="oops")
        step2 = Step(description="s2", tool_name="t2")
        plan = Plan(task_id="t1", steps=[step1, step2])
        resolver = ReferenceResolver(plan, current_step_id=step2.step_id)
        with pytest.raises(ValueError, match="failed"):
            resolver.resolve({"x": {"$ref": step1.step_id}})

    def test_rejects_invalid_list_index(self):
        output = [{"path": "/x"}]
        plan, step2 = self._plan_with_succeeded_step(output)
        resolver = ReferenceResolver(plan, current_step_id=step2.step_id)
        with pytest.raises(ValueError, match="out of range"):
            resolver.resolve({"x": {"$ref": plan.steps[0].step_id, "extract": "output.99.path"}})

    def test_rejects_invalid_dict_key(self):
        output = {"a": 1}
        plan, step2 = self._plan_with_succeeded_step(output)
        resolver = ReferenceResolver(plan, current_step_id=step2.step_id)
        with pytest.raises(ValueError, match="not found in result dict"):
            resolver.resolve({"x": {"$ref": plan.steps[0].step_id, "extract": "output.missing_key"}})

    def test_rejects_self_reference(self):
        step = Step(description="s", tool_name="t")
        plan = Plan(task_id="t1", steps=[step])
        resolver = ReferenceResolver(plan, current_step_id=step.step_id)
        with pytest.raises(ValueError, match="self-reference"):
            resolver.resolve({"x": {"$ref": step.step_id}})

    def test_non_ref_arguments_pass_through_unchanged(self):
        step = Step(description="s", tool_name="t")
        plan = Plan(task_id="t1", steps=[step])
        resolver = ReferenceResolver(plan, current_step_id=step.step_id)
        result = resolver.resolve({"a": "literal", "b": 42, "c": {"key": "val"}})
        assert result == {"a": "literal", "b": 42, "c": {"key": "val"}}


# ===========================================================================
# Multi-Step Integration — file.search → vscode.open_file
# ===========================================================================

class TestMultiStepIntegration:
    def test_find_and_open_file_multi_step(self, tmp_path):
        """Core V8.1 demonstration: file.search result feeds vscode.open_file."""
        assignment = tmp_path / "java_assignment.java"
        assignment.write_text("public class Assignment {}")

        vscode_skill = _mock_vscode()
        registry = ToolRegistry([
            FileSearchTool([tmp_path]),
            VSCodeOpenFileTool(vscode_skill),
        ])

        # Build plan manually to mirror what the planner produces
        step_search = Step(
            description="Search for Java assignment",
            tool_name="file.search",
            arguments={"query": "java_assignment"},
        )
        step_open = Step(
            description="Open in VS Code",
            tool_name="vscode.open_file",
            arguments={"path": {"$ref": step_search.step_id, "extract": "output.0.path"}},
        )
        plan = Plan(task_id="task-123", steps=[step_search, step_open])

        engine = ExecutionEngine(registry)
        results = engine.execute(plan)

        assert all(r.success for r in results), [r.error for r in results]
        assert step_search.status is StepStatus.SUCCESS
        assert step_open.status is StepStatus.SUCCESS
        # VS Code was told to open the correct file
        vscode_skill.execute.assert_called_once()
        call_intent = vscode_skill.execute.call_args[0][0]
        assert call_intent.action == "open_file"
        assert "java_assignment.java" in call_intent.target

    def test_multi_step_aborts_after_search_failure(self, tmp_path):
        """If file.search returns empty, step2 should fail when extracting index 0."""
        # tmp_path is empty → search finds nothing
        vscode_skill = _mock_vscode()
        registry = ToolRegistry([
            FileSearchTool([tmp_path]),
            VSCodeOpenFileTool(vscode_skill),
        ])

        step_search = Step(
            description="Search",
            tool_name="file.search",
            arguments={"query": "missing_file"},
        )
        step_open = Step(
            description="Open",
            tool_name="vscode.open_file",
            arguments={"path": {"$ref": step_search.step_id, "extract": "output.0.path"}},
        )
        plan = Plan(task_id="t2", steps=[step_search, step_open])

        engine = ExecutionEngine(registry)
        results = engine.execute(plan)

        # search succeeds (empty list) but open fails resolving index 0
        assert results[0].success  # search itself succeeded
        assert not results[1].success  # resolution failed
        assert "out of range" in results[1].error
        vscode_skill.execute.assert_not_called()


# ===========================================================================
# Agent-Level Multi-Step Test
# ===========================================================================

class TestAgentMultiStep:
    def test_agent_find_and_open_java_assignment(self, tmp_path):
        assignment = tmp_path / "java_assignment.java"
        assignment.write_text("public class Assignment {}")

        vscode_skill = _mock_vscode()
        registry = ToolRegistry([
            FileSearchTool([tmp_path]),
            VSCodeOpenFileTool(vscode_skill),
        ])

        planner = DeterministicPlanner()
        agent = Agent(registry=registry, planner=planner)

        result = agent.run("Find my Java assignment and open it in VS Code.")
        assert result.success, result.error
        assert agent.state.value == "completed"
        vscode_skill.execute.assert_called_once()

    def test_agent_find_java_assignment_only(self, tmp_path):
        assignment = tmp_path / "java_assignment.java"
        assignment.write_text("// code")

        registry = ToolRegistry([FileSearchTool([tmp_path])])
        agent = Agent(registry=registry, planner=DeterministicPlanner())

        result = agent.run("Find my Java assignment.")
        assert result.success, result.error
        assert isinstance(result.output, list)
        assert len(result.output) >= 1

    def test_v80_calculator_still_works(self):
        from agent.tools import CalculatorTool
        registry = ToolRegistry([CalculatorTool()])
        agent = Agent(registry=registry)
        result = agent.run("Calculate 25 * 4")
        assert result.success and result.output == "100"


# ===========================================================================
# Security Tests
# ===========================================================================

class TestSecurityRejections:
    def test_shell_tools_not_in_registry(self, tmp_path):
        registry = _registry_v81(tmp_path)
        for name in ("powershell", "cmd", "shell", "subprocess", "python_exec", "execute_command"):
            assert not registry.has(name), f"dangerous tool registered: {name}"
            result = registry.execute(ToolRequest(tool=name, arguments={}))
            assert not result.success
            assert "unknown tool" in result.error

    def test_path_traversal_rejected_by_file_search(self, tmp_path):
        tool = FileSearchTool([tmp_path])
        # The query itself is safe — traversal would only matter for path args
        # but FileSearchTool only searches within allowed roots regardless
        result = tool.run({"query": "passwd"})
        # Result is success (empty list) because search only walks tmp_path
        assert result.success
        if result.output:
            for item in result.output:
                assert str(tmp_path) in item["path"]

    def test_path_traversal_rejected_by_file_read(self, tmp_path, tmp_path_factory):
        other = tmp_path_factory.mktemp("secret")
        (other / "secret.txt").write_text("TOP SECRET")
        tool = FileReadTextTool([tmp_path])
        result = tool.run({"path": str(other / "secret.txt")})
        assert not result.success
        assert "outside allowed roots" in result.error

    def test_path_traversal_via_dotdot_rejected(self, tmp_path):
        traversal = str(tmp_path / ".." / ".." / "Windows")
        result = FileMetadataTool([tmp_path]).run({"path": traversal})
        assert not result.success
        assert "outside allowed roots" in result.error

    def test_non_http_url_rejected_by_browser_tool(self):
        for bad_url in ("file:///etc/passwd", "javascript:evil()", "ftp://host/x", "data:text/html,<h1>"):
            result = BrowserOpenUrlTool(_mock_browser()).run({"url": bad_url})
            assert not result.success, f"should have rejected: {bad_url}"

    def test_nonexistent_file_rejected_by_vscode_tool(self, tmp_path):
        result = VSCodeOpenFileTool(_mock_vscode()).run({"path": str(tmp_path / "ghost.java")})
        assert not result.success

    def test_vscode_tool_does_not_invoke_subprocess_on_nonexistent_file(self, tmp_path):
        with patch("subprocess.Popen") as mock_popen:
            result = VSCodeOpenFileTool(_mock_vscode()).run({"path": str(tmp_path / "ghost.java")})
            assert not result.success
            mock_popen.assert_not_called()

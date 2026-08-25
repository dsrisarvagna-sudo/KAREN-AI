from ui.state import KarenStatus, UIState
from core.events import RuntimeEvent, RuntimeEventType


def test_ui_package_imports_without_starting_a_window():
    import ui

    assert ui.KarenStatus.ONLINE.display == "🟢 Online"


def test_ui_state_supports_status_transitions_and_messages():
    state = UIState()
    state.set_status("Thinking")
    state.add_message("You", "Hello")
    state.add_message("Karen", "Hi there")

    assert state.status is KarenStatus.THINKING
    assert [(message.speaker, message.text) for message in state.messages] == [("You", "Hello"), ("Karen", "Hi there")]


def test_all_visual_statuses_have_labels():
    assert [status.display for status in KarenStatus] == [
        "🟢 Online", "🎤 Listening", "🧠 Thinking", "👀 Looking",
        "🔊 Speaking", "💤 Paused", "🔴 Offline",
    ]


def test_window_can_be_constructed_when_a_display_is_available():
    import tkinter as tk

    import pytest

    from ui.window import KarenWindow

    try:
        root = tk.Tk()
    except tk.TclError as error:
        pytest.skip(f"graphical display unavailable: {error}")
    root.withdraw()
    window = KarenWindow(root)
    window.set_status(KarenStatus.LOOKING)
    window.add_message("Karen", "Ready")
    window.close()


def test_window_renders_messages_and_navigates_ui_panels_when_display_is_available(tmp_path):
    import tkinter as tk
    import pytest

    from memory.history import ConversationHistory
    from ui.window import KarenWindow

    try:
        root = tk.Tk()
    except tk.TclError as error:
        pytest.skip(f"graphical display unavailable: {error}")
    root.withdraw()
    window = KarenWindow(root, history=ConversationHistory(tmp_path))
    window.add_message("You", "What is on my screen?")
    window.add_message("Karen", "I can see Visual Studio Code.")
    rendered = window.conversation.text.get("1.0", "end")
    assert "YOU" in rendered
    assert "I can see Visual Studio Code." in rendered

    window._action("settings")
    assert window.settings_view.winfo_manager() == "pack"
    window._action("skills")
    assert window.skills_view.winfo_manager() == "pack"
    window._action("history")
    assert window.history_view.winfo_manager() == "pack"
    window.show_main()
    assert window.shell.winfo_manager() == "pack"
    window.close()


def test_window_submits_text_to_the_runtime_and_displays_runtime_status_when_available(tmp_path):
    import tkinter as tk
    import pytest

    from memory.history import ConversationHistory
    from ui.window import KarenWindow

    class FakeRuntime:
        def __init__(self):
            self.commands = []
            self.current_conversation_id = None

        def submit_text(self, command):
            self.commands.append(command)
            return True

        def poll_events(self):
            return []

        def stop(self):
            pass

    try:
        root = tk.Tk()
    except tk.TclError as error:
        pytest.skip(f"graphical display unavailable: {error}")
    root.withdraw()
    runtime = FakeRuntime()
    window = KarenWindow(root, history=ConversationHistory(tmp_path), runtime=runtime)
    window.input_var.set("what is on my screen")
    window._submit_text()
    assert runtime.commands == ["what is on my screen"]
    window._handle_runtime_event(RuntimeEvent(RuntimeEventType.VISION_STARTED))
    assert "Looking" in window.state.runtime_status
    window.close()

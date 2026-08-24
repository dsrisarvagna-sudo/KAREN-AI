from ui.state import KarenStatus, UIState


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

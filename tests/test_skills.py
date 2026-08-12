from unittest.mock import patch

import pytest

from router.intent_router import IntentRouter
from skills.browser import BrowserSkill


@pytest.mark.parametrize("command", [
    "open youtube",
    "open YouTube",
    "hey karen open youtube",
    "Karen, open YouTube",
])
def test_browser_skill_opens_youtube(command):
    intent = IntentRouter().route(command)

    with patch("skills.browser.webbrowser.open") as open_browser:
        reply = BrowserSkill().execute(intent)

    open_browser.assert_called_once_with("https://www.youtube.com")
    assert reply == "Opening YouTube."


def test_browser_skill_opens_google():
    intent = IntentRouter().route("open google")

    with patch("skills.browser.webbrowser.open") as open_browser:
        reply = BrowserSkill().execute(intent)

    open_browser.assert_called_once_with("https://www.google.com")
    assert reply == "Opening Google."


def test_browser_skill_keeps_generic_browser_behavior():
    intent = IntentRouter().route("open browser")

    with patch("skills.browser.webbrowser.open") as open_browser:
        reply = BrowserSkill().execute(intent)

    open_browser.assert_called_once_with("https://www.google.com")
    assert reply == "Opening browser."


@pytest.mark.parametrize("query", ["ps5", "nissan patrol", "pawan kalyan"])
def test_browser_skill_searches_without_for(query):
    intent = IntentRouter().route(f"search for {query}")

    with patch("skills.browser.webbrowser.open") as open_browser:
        reply = BrowserSkill().execute(intent)

    expected_query = query.replace(" ", "+")
    open_browser.assert_called_once_with(
        f"https://www.google.com/search?q={expected_query}"
    )
    assert f"for {query}" in reply

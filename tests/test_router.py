import pytest

from router.intent_router import IntentRouter


@pytest.mark.parametrize("command", [
    "open youtube",
    "open YouTube",
    "hey karen open youtube",
    "Karen, open YouTube",
])
def test_youtube_routes_to_browser_target(command):
    intent = IntentRouter().route(command)

    assert intent.skill == "browser"
    assert intent.action == "open"
    assert intent.target == "youtube"


def test_google_routes_to_browser_target():
    intent = IntentRouter().route("open google")

    assert intent.skill == "browser"
    assert intent.action == "open"
    assert intent.target == "google"


def test_open_browser_keeps_generic_browser_intent():
    intent = IntentRouter().route("open browser")

    assert intent.skill == "browser"
    assert intent.action == "open"
    assert intent.target is None


@pytest.mark.parametrize("command, expected", [
    ("search for ps5", "ps5"),
    ("search for nissan patrol", "nissan patrol"),
    ("search for pawan kalyan", "pawan kalyan"),
])
def test_search_query_excludes_for(command, expected):
    intent = IntentRouter().route(command)

    assert intent.skill == "browser"
    assert intent.action == "search"
    assert intent.query == expected

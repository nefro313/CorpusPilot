from services.rag import memory


def setup_function(_func) -> None:
    memory._session_history.clear()


def test_recent_history_empty_for_unknown_session() -> None:
    assert memory.recent_history(None) == []
    assert memory.recent_history("nope") == []


def test_append_history_records_turns_in_order() -> None:
    memory.append_history("s1", "q1", "a1")
    memory.append_history("s1", "q2", "a2")
    assert memory.recent_history("s1") == [
        {"question": "q1", "answer": "a1"},
        {"question": "q2", "answer": "a2"},
    ]


def test_append_history_caps_at_session_limit() -> None:
    cap = memory._SESSION_HISTORY_CAP
    for i in range(cap + 5):
        memory.append_history("s1", f"q{i}", f"a{i}")
    history = memory.recent_history("s1")
    assert len(history) == cap
    assert history[-1] == {"question": f"q{cap + 4}", "answer": f"a{cap + 4}"}


def test_append_history_ignores_blank_answers() -> None:
    memory.append_history("s1", "q", "   ")
    assert memory.recent_history("s1") == []

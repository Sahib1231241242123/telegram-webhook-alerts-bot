from app.handlers import fsm


def test_fsm_state_transition_and_reset() -> None:
    user_data: dict[str, str] = {}
    assert not fsm.is_details_state(user_data)

    fsm.set_details_state(user_data, "AL-1")
    assert fsm.is_details_state(user_data)
    assert user_data[fsm.CURRENT_ALERT_KEY] == "AL-1"

    fsm.reset_state(user_data)
    assert not fsm.is_details_state(user_data)
    assert fsm.CURRENT_ALERT_KEY not in user_data

DETAILS_STATE = "DETAILS_VIEW"
FSM_STATE_KEY = "fsm_state"
CURRENT_ALERT_KEY = "current_alert_id"


def set_details_state(user_data: dict, alert_id: str) -> None:
    user_data[FSM_STATE_KEY] = DETAILS_STATE
    user_data[CURRENT_ALERT_KEY] = alert_id


def reset_state(user_data: dict) -> None:
    user_data.pop(FSM_STATE_KEY, None)
    user_data.pop(CURRENT_ALERT_KEY, None)


def is_details_state(user_data: dict) -> bool:
    return user_data.get(FSM_STATE_KEY) == DETAILS_STATE

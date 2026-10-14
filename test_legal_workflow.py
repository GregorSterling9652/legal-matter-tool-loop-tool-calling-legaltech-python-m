from legal_workflow import MatterIntake, decide_follow_up


def test_follow_up_is_three_days_before_deadline():
    matter = MatterIntake(matter_id="M-1", client_name="Casey", deadline_days=10)
    assert decide_follow_up(matter.deadline_days) == 7
    assert decide_follow_up(None) is None

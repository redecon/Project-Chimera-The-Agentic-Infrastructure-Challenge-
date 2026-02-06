import pytest
from skills import skills_interface


# Assuming skills_interface.py will expose a class or function called SkillInterface
from skills import skills_interface

def test_skill_interface_parameters():
    """
    Test that the skills interface accepts the correct parameters.
    Expected contract (example from technical.md):
    run_skill(skill_name: str, input_data: dict) -> dict
    """
    interface = skills_interface.SkillInterface()

    # Try calling with missing parameters
    with pytest.raises(TypeError):
        interface.run_skill()

    # Try calling with wrong types
    with pytest.raises(Exception):
        interface.run_skill(skill_name=123, input_data="not_a_dict")

    # Try calling with correct parameters (should fail until implemented)
    result = interface.run_skill(skill_name="trend_fetcher", input_data={"query": "AI"})
    assert isinstance(result, dict), "Expected result to be a dict"

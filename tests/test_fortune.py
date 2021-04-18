
def test_run_fortune():
    """Tests that the `call_fortune` function in the `fortune` module works as planned."""
    from sarathi.fortune import run_fortune
    fortune_string = run_fortune('funny')
    assert isinstance(fortune_string, str), "The call_fortune function should have returned a string."


    

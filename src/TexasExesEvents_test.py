from . import TexasExesEvents

def test_TexasExesEvents():
    assert TexasExesEvents.apply("Jane") == "hello Jane"

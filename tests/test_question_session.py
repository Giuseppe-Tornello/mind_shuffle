from src.ui.question_session import QuestionSession
from tests.test_constants import VALID_DECK

def test_has_cards():
    qs = QuestionSession()
    assert qs.has_cards() == False

def test_current_card():
    qs = QuestionSession(VALID_DECK)
    assert qs.current_card() == VALID_DECK[0]

def test_next_question():
    qs = QuestionSession()
    qs.next_question()

def test_previous_question(): 
    qs = QuestionSession(VALID_DECK)
    qs.previous_question()

def test_all_answered(): 
    qs = QuestionSession(VALID_DECK)
    assert qs.all_answered() == False

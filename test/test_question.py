from gameutils.question import Question

EXPECTED_FIELDS = ["category", "correct_answer", "incorrect_answers", "question", "type", "difficulty"]
EXPECTED_FIELDS_FOR_CLIENT = ["category", "type", "difficulty", "possible_answers", "question"]


def test_to_json():
    # Arrange
    question = Question("category", "type", "difficulty", "question", "correct_answer", ["incorrect_answers"])
    # Act
    result = question.to_json()
    # Assert
    assert isinstance(result, dict)
    assert all(field in result for field in EXPECTED_FIELDS)


def test_to_json_for_client():
    # Arrange
    question = Question("category", "type", "difficulty", "question", "correct_answer", ["incorrect_answers"])
    # Act
    result = question.to_json_for_client()
    # Assert
    assert isinstance(result, dict)
    assert all(field in result for field in EXPECTED_FIELDS_FOR_CLIENT)


def test_from_json_for_client():
    # Arrange
    question = Question("category", "type", "difficulty", "question", "correct_answer", ["incorrect_answers"])
    # Act
    result = question.from_json_for_client(question.to_json_for_client())
    # Assert
    assert isinstance(result, Question)
    assert all(field in result.to_json_for_client() for field in EXPECTED_FIELDS_FOR_CLIENT)
    # test if all fields are in the result


def test_get_url():
    """ We won't test the API itself, but we can test if the url is correct"""

    # Arrange
    question = Question("category", "type", "difficulty", "question", "correct_answer", ["incorrect_answers"])
    # Act
    result = question.get_url(amount=10, encode="utf-8")
    # Assert
    assert isinstance(result, str)
    assert result.startswith("https://opentdb.com/api.php?amount=10&encoding=utf-8")

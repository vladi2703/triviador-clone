import html


import requests


class Question:
    def __init__(self, category, question_type, difficulty, question, correct_answer=None, incorrect_answers=None,
                 possible_answers=None):
        self.category = category
        self.correct_answer = correct_answer
        self.incorrect_answers = incorrect_answers
        self.question = question
        self.question_type = question_type
        self.difficulty = difficulty

        if incorrect_answers and correct_answer:
            self.possible_answers = incorrect_answers + [correct_answer]
        elif possible_answers:
            self.possible_answers = possible_answers
        else:
            raise ValueError("Incorrect answers and correct answer must be provided")

    def to_json(self):
        return {
            "category": self.category,
            "correct_answer": self.correct_answer,
            "incorrect_answers": self.incorrect_answers,
            "question": self.question,
            "type": self.question_type,
            "difficulty": self.difficulty
        }

    def to_json_for_client(self):
        return {
            "category": self.category,
            "type": self.question_type,
            "difficulty": self.difficulty,
            "possible_answers": self.incorrect_answers + [self.correct_answer],
            "question": self.question,
        }

    @classmethod
    def from_json_for_client(cls, param):
        return cls(
            question=param["question"],
            possible_answers=param["possible_answers"],
            category=param["category"],
            question_type=param["type"],
            difficulty=param["difficulty"]
        )

    def __str__(self):
        return f"{self.category=} \n{self.difficulty=} \n{self.question_type=} \n{self.question=} \n{self.correct_answer=} \n{self.incorrect_answers=} \n {self.possible_answers=}"

    @classmethod
    def get_one_question(cls, category=None, difficulty=None, q_type=None, encode="utf-8"):
        questions = cls.get_questions_by_params(category, difficulty, q_type, 1, encode)
        return questions[0]

    @staticmethod
    def get_url(category=None, difficulty=None, q_type=None, amount=10, encode="utf-8") -> str:
        """Get the base url for the API. Returns a string."""
        base_url = "https://opentdb.com/api.php?"
        params = {
            "amount": amount
        }
        if category is not None:
            params["category"] = category
        if difficulty is not None:
            params["difficulty"] = difficulty
        if q_type is not None:
            params["type"] = q_type
        if encode is not None:
            params["encoding"] = encode

        return requests.Request("GET", base_url, params=params).prepare().url
    @staticmethod
    def get_questions_by_params(category=None, difficulty=None, q_type=None, amount=10, encode="utf-8") -> list:
        """Get questions from the API. Returns a list of Question objects."""

        base_url = Question.get_url(category, difficulty, q_type, amount, encode)
        response = requests.get(base_url)

        if response.status_code == 200:
            results = response.json()["results"]
            questions = []
            for result in results:
                question = Question(
                    result["category"],
                    result["type"],
                    result["difficulty"],
                    html.unescape(result["question"]),
                    result["correct_answer"],
                    result["incorrect_answers"]
                )
                questions.append(question)
            return questions
        else:
            raise Exception("Error getting questions, status code: " + str(response.status_code))



class Quiz:
    def __init__(self, question, choices, answer):
        if not isinstance(question, str) or not question.strip():
            raise ValueError("문제 내용이 올바르지 않습니다.")

        if not isinstance(choices, list) or len(choices) != 4:
            raise ValueError("선택지는 4개여야 합니다.")

        if not all(isinstance(choice, str) and choice.strip() for choice in choices):
            raise ValueError("선택지 내용이 올바르지 않습니다.")

        if isinstance(answer, bool) or not isinstance(answer, int) or not 1 <= answer <= 4:
            raise ValueError("정답은 1~4 사이의 정수여야 합니다.")

        self.question = question
        self.choices = choices
        self.answer = answer

    def show_question(self):
        print(self.question)

        for index, choice in enumerate(self.choices, start=1):
            print(f"{index}. {choice}")

    def check_answer(self, user_answer):
        return user_answer == self.answer
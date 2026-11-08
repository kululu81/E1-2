import json
import random
from pathlib import Path

from quiz import Quiz


class QuizGame:
    def __init__(self):
        self.state_file = Path(__file__).parent / "state.json"
        self.quizzes = self._default_quizzes()
        self.best_score = None  # 100점 만점 기준 점수, None이면 아직 퀴즈를 풀지 않은 상태

        self.load_data()

    @staticmethod
    def _default_quizzes():
        """기본 퀴즈 5개를 만들어 반환한다."""
        return [
            Quiz("Python의 파일 확장자는?",
                 [".py", ".html", ".css", ".java"], 1),
            Quiz("Python에서 화면에 글자를 출력하는 명령어는?",
                 ["input()", "print()", "write()", "show()"], 2),
            Quiz("Python에서 두 숫자를 더하는 연산자는?",
                 ["-", "*", "+", "/"], 3),
            Quiz("Python에서 반복문을 만들 때 사용하는 키워드는?",
                 ["if", "for", "def", "class"], 2),
            Quiz("Python에서 여러 값을 순서대로 저장하는 자료형은?",
                 ["list", "int", "str", "bool"], 1),
        ]

    def save_data(self):
        data = {
            "quizzes": [
                {
                    "question": quiz.question,
                    "choices": quiz.choices,
                    "answer": quiz.answer,
                }
                for quiz in self.quizzes
            ],
            "best_score": self.best_score,
        }

        try:
            with open(self.state_file, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)

            print("게임 데이터가 저장되었습니다.")

        except OSError:
            print("데이터 저장에 실패했습니다.")

    def load_data(self):
        if not self.state_file.exists():
            print("저장된 데이터가 없습니다. 기본 퀴즈를 사용합니다.")
            return

        try:
            with open(self.state_file, "r", encoding="utf-8") as file:
                data = json.load(file)

            saved_best_score = data.get("best_score")

            if saved_best_score is not None and not isinstance(saved_best_score, int):
                raise ValueError("best_score 형식이 올바르지 않습니다.")

            loaded_quizzes = []

            for item in data["quizzes"]:
                loaded_quizzes.append(
                    Quiz(
                        item["question"],
                        item["choices"],
                        item["answer"],
                    )
                )

            self.quizzes = loaded_quizzes
            self.best_score = saved_best_score

            print(f"저장된 게임 데이터를 불러왔습니다. (퀴즈 {len(self.quizzes)}개)")

        except OSError:
            print("파일을 읽는 중 오류가 발생했습니다. 기본 퀴즈를 사용합니다.")

        except (json.JSONDecodeError, KeyError, TypeError, ValueError, AttributeError):
            print("저장 파일이 손상되었습니다. 기본 퀴즈로 초기화합니다.")
            self.quizzes = self._default_quizzes()
            self.best_score = None
            self.save_data()

    def show_quizzes(self):
        if not self.quizzes:
            print("등록된 퀴즈가 없습니다.")
            return

        print(f"\n===== 퀴즈 목록 (총 {len(self.quizzes)}개) =====")

        for index, quiz in enumerate(self.quizzes, start=1):
            print(f"{index}. {quiz.question}")

    def show_best_score(self):
        if self.best_score is None:
            print("아직 퀴즈를 풀지 않았습니다.")
        else:
            print(f"🏆 최고 점수: {self.best_score}점 (100점 만점)")

    def _ask_question_count(self):
        """풀 문제 수를 입력받아 반환한다. 올바른 값이 들어올 때까지 다시 묻는다."""
        total = len(self.quizzes)

        while True:
            raw = input(f"풀 문제 수를 입력하세요 (1~{total}): ").strip()

            if not raw:
                print("⚠️ 문제 수를 입력해주세요.")
                continue

            if not raw.isdecimal():
                print("⚠️ 숫자를 입력해주세요.")
                continue

            count = int(raw)

            if 1 <= count <= total:
                return count

            print(f"⚠️ 1부터 {total} 사이의 숫자를 입력해주세요.")

    def play(self):
        if not self.quizzes:
            print("등록된 퀴즈가 없습니다.")
            return

        count = self._ask_question_count()

        # 원본 순서는 유지하고, 이번 게임에서 출제할 문제만 랜덤으로 뽑는다.
        selected_quizzes = random.sample(self.quizzes, count)
        correct = 0

        print(f"\n===== 퀴즈 시작 (총 {count}문제, 순서는 랜덤입니다) =====")

        for index, quiz in enumerate(selected_quizzes, start=1):
            print(f"\n[{index}번 문제]")
            quiz.show_question()

            while True:
                answer = input("정답 번호를 입력하세요: ").strip()

                if answer in ["1", "2", "3", "4"]:
                    break

                print("1부터 4까지의 숫자를 입력해주세요.")

            if quiz.check_answer(int(answer)):
                print("정답입니다!")
                correct += 1
            else:
                print("오답입니다.")

        # 문제 수가 달라도 비교할 수 있도록 100점 만점으로 환산한다.
        score = correct * 100 // count

        print("\n===== 퀴즈 결과 =====")
        print(f"🏆 결과: {count}문제 중 {correct}문제 정답! ({score}점)")

        if self.best_score is None or score > self.best_score:
            self.best_score = score
            print("🎉 새로운 최고 점수입니다!")
            self.save_data()

    def add_quiz(self):
        print("\n===== 새 퀴즈 추가 =====")

        question = input("문제를 입력하세요: ").strip()

        while not question:
            print("문제 내용을 입력해주세요.")
            question = input("문제를 입력하세요: ").strip()

        choices = []

        for index in range(1, 5):
            while True:
                choice = input(f"{index}번 선택지를 입력하세요: ").strip()

                if choice:
                    choices.append(choice)
                    break

                print("선택지 내용을 입력해주세요.")

        while True:
            answer = input("정답 번호를 입력하세요 (1~4): ").strip()

            if answer in ["1", "2", "3", "4"]:
                break

            print("정답은 1부터 4까지의 숫자로 입력해주세요.")

        quiz = Quiz(question, choices, int(answer))
        self.quizzes.append(quiz)

        print("새 퀴즈가 추가되었습니다!")
        self.save_data()

import json
import random
import shutil
from pathlib import Path

from quiz import Quiz


class QuizGame:
    def __init__(self):
        self.state_file = Path(__file__).parent / "state.json"
        self.backup_file = Path(__file__).parent / "state.json.bak"
        self.temp_file = Path(__file__).parent / "state.json.tmp"

        self.quizzes = self._default_quizzes()
        self.best_score = None

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

    def _make_data(self):
        """현재 게임 데이터를 JSON 저장용 딕셔너리로 변환한다."""
        return {
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

    @staticmethod
    def _validate_data(data):
        """불러온 JSON 데이터의 구조와 내용을 검증한다."""
        if not isinstance(data, dict):
            raise ValueError("저장 데이터는 객체여야 합니다.")

        if "quizzes" not in data or not isinstance(data["quizzes"], list):
            raise ValueError("퀴즈 목록 형식이 올바르지 않습니다.")

        if "best_score" not in data:
            raise ValueError("최고 점수 항목이 없습니다.")

        score = data["best_score"]

        if score is not None:
            if isinstance(score, bool) or not isinstance(score, int):
                raise ValueError("최고 점수 형식이 올바르지 않습니다.")

            if not 0 <= score <= 100:
                raise ValueError("최고 점수는 0~100 사이여야 합니다.")

        quizzes = []

        for item in data["quizzes"]:
            if not isinstance(item, dict):
                raise ValueError("퀴즈 데이터 형식이 올바르지 않습니다.")

            quiz = Quiz(
                item["question"],
                item["choices"],
                item["answer"],
            )

            if len(set(choice.strip() for choice in quiz.choices)) != 4:
                raise ValueError("중복된 선택지가 있습니다.")

            quizzes.append(quiz)

        return quizzes, score

    def _read_data(self, file_path):
        """지정한 JSON 파일을 읽고 검증한다."""
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        return self._validate_data(data)

    def _backup_current_data(self):
        """기존 저장 파일을 백업한다."""
        if not self.state_file.exists():
            return True

        try:
            shutil.copy2(self.state_file, self.backup_file)
            return True

        except OSError as error:
            print(f"백업 파일 생성에 실패했습니다: {error}")
            return False

    def save_data(self):
        """임시 파일에 저장한 후 교체하여 데이터 손상을 줄인다."""
        try:
            data = self._make_data()

            with open(self.temp_file, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
                file.flush()

            # 기존 파일이 있으면 교체 전에 백업한다.
            if self.state_file.exists():
                if not self._backup_current_data():
                    print("기존 데이터를 백업하지 못해 저장을 취소합니다.")
                    return False

            # 임시 파일을 실제 저장 파일로 교체한다.
            self.temp_file.replace(self.state_file)

            print("게임 데이터가 안전하게 저장되었습니다.")
            return True

        except (OSError, TypeError, ValueError) as error:
            print(f"데이터 저장에 실패했습니다: {error}")

            try:
                if self.temp_file.exists():
                    self.temp_file.unlink()
            except OSError:
                pass

            return False

    def load_data(self):
        """저장 파일을 불러오고, 손상된 경우 백업으로 복구한다."""
        if not self.state_file.exists():
            print("저장된 데이터가 없습니다. 기본 퀴즈를 사용합니다.")
            return

        try:
            quizzes, score = self._read_data(self.state_file)
            self.quizzes = quizzes
            self.best_score = score

            print(
                f"저장된 게임 데이터를 불러왔습니다. "
                f"(퀴즈 {len(self.quizzes)}개)"
            )
            return

        except (OSError, json.JSONDecodeError, KeyError,
                TypeError, ValueError, AttributeError) as error:
            print(f"저장 파일을 불러오지 못했습니다: {error}")

        # 원본 파일을 별도로 보존한다.
        try:
            if self.state_file.exists():
                damaged_file = self.state_file.with_name("state.json.corrupt")
                shutil.copy2(self.state_file, damaged_file)
                print(f"손상된 파일을 보존했습니다: {damaged_file.name}")
        except OSError as error:
            print(f"손상 파일 보존에 실패했습니다: {error}")

        # 백업 파일에서 복구를 시도한다.
        if self.backup_file.exists():
            try:
                quizzes, score = self._read_data(self.backup_file)

                self.quizzes = quizzes
                self.best_score = score

                print("백업 파일을 이용해 데이터를 복구했습니다.")

                if self.save_data():
                    print("복구된 데이터가 저장되었습니다.")

                return

            except (OSError, json.JSONDecodeError, KeyError,
                    TypeError, ValueError, AttributeError) as error:
                print(f"백업 파일도 손상되었습니다: {error}")

        # 복구할 수 없는 경우 기본 데이터로 초기화한다.
        print("기본 퀴즈 5개로 초기화합니다.")
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
        """풀 문제 수를 입력받는다."""
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

                if not choice:
                    print("선택지 내용을 입력해주세요.")
                    continue

                if choice in choices:
                    print("이미 등록한 선택지입니다. 다른 내용을 입력해주세요.")
                    continue

                choices.append(choice)
                break

        while True:
            answer = input("정답 번호를 입력하세요 (1~4): ").strip()

            if answer in ["1", "2", "3", "4"]:
                break

            print("정답은 1부터 4까지의 숫자로 입력해주세요.")

        quiz = Quiz(question, choices, int(answer))
        self.quizzes.append(quiz)

        print("새 퀴즈가 추가되었습니다!")
        self.save_data()

    def delete_quiz(self):
        if not self.quizzes:
            print("삭제할 퀴즈가 없습니다.")
            return

        self.show_quizzes()
        total = len(self.quizzes)

        while True:
            raw = input(f"삭제할 퀴즈 번호를 입력하세요 (1~{total}): ").strip()

            if not raw:
                print("⚠️ 삭제할 번호를 입력해주세요.")
                continue

            if not raw.isdecimal():
                print("⚠️ 숫자를 입력해주세요.")
                continue

            number = int(raw)

            if 1 <= number <= total:
                break

            print(f"⚠️ 1부터 {total} 사이의 숫자를 입력해주세요.")

        target = self.quizzes[number - 1]

        while True:
            confirm = input(
                f"'{target.question}' 퀴즈를 삭제할까요? (y/n): "
            ).strip().lower()

            if confirm in ["y", "n"]:
                break

            print("⚠️ y 또는 n을 입력해주세요.")

        if confirm == "n":
            print("삭제를 취소했습니다.")
            return

        self.quizzes.pop(number - 1)
        print("퀴즈가 삭제되었습니다.")
        self.save_data()

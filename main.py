from quiz_game import QuizGame


def print_menu():
    """메뉴 화면을 출력한다."""
    print("\n================================")
    print("       Python 기초 퀴즈 게임")
    print("================================")
    print("1. 퀴즈 풀기")
    print("2. 퀴즈 추가하기")
    print("3. 퀴즈 목록 보기")
    print("4. 최고 점수 확인")
    print("5. 종료하기")


def main():
    """프로그램의 메뉴 루프를 실행한다."""
    game = QuizGame()

    try:
        while True:
            print_menu()
            choice = input("메뉴를 선택하세요: ").strip()

            if choice == "1":
                game.play()
            elif choice == "2":
                game.add_quiz()
            elif choice == "3":
                game.show_quizzes()
            elif choice == "4":
                game.show_best_score()
            elif choice == "5":
                print("게임을 종료합니다.")
                break
            elif choice == "":
                print("⚠️ 메뉴 번호를 입력해주세요.")
            else:
                print("⚠️ 잘못된 입력입니다. 1-5 사이의 숫자를 입력하세요.")

    except (KeyboardInterrupt, EOFError):
        print("\n프로그램을 안전하게 종료합니다.")

    finally:
        game.save_data()


if __name__ == "__main__":
    main()
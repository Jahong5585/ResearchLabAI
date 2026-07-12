from Agents.Director.director import Director

from Tools.register_tools import register_tools


def main():

    register_tools()

    print("=" * 60)
    print("ResearchLab AI")
    print("=" * 60)

    director = Director()

    while True:

        print()

        user_request = input(
            "Введите задачу (exit для выхода):\n"
        ).strip()

        if user_request.lower() == "exit":
            break

        print()

        answer = director.execute(user_request)

        print("Ответ:\n")
        print(answer)


if __name__ == "__main__":
    main()
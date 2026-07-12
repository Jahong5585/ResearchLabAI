from Core.query_optimizer import QueryOptimizer


def main():

    optimizer = QueryOptimizer()

    query = "Сделай обзор литературы по искусственному интеллекту в образовании"

    print()

    print("Исходный запрос:")

    print(query)

    print()

    print("Оптимизированный:")

    print(optimizer.optimize(query))


if __name__ == "__main__":
    main()
from Core.query_optimizer import QueryOptimizer


def test_known_russian_phrases_are_translated():
    result = QueryOptimizer().optimize(
        "Сделай обзор литературы по искусственному интеллекту в образовании"
    )

    assert "Artificial" in result
    assert "Intelligence" in result
    assert "Education" in result


def test_unknown_cyrillic_topic_is_preserved():
    result = QueryOptimizer().optimize(
        "Сделай обзор литературы о наследии эпохи Темуридов"
    )

    assert result
    assert "наследии" in result.lower()
    assert "темуридов" in result.lower()

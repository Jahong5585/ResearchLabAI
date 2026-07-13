# ResearchLab AI

## Назначение

ResearchLab AI — модульная мультиагентная система для поиска научных публикаций, структурированного извлечения данных, межстатейного синтеза и подготовки обзора литературы.

## Текущий pipeline

```text
Director
  ↓
Planner
  ↓
Orchestrator / Workflow
  ↓
Researcher
  ↓
Ranking
  ↓
Summarizer
  ↓
Cluster
  ↓
Outline
  ↓
Synthesis
  ↓
Writer
  ↓
Reviewer
```

### Разделение обязанностей

- **Researcher** ищет публикации через Crossref и OpenAlex.
- **Ranking** ранжирует найденные публикации.
- **Summarizer** отдельно анализирует каждую публикацию и возвращает структурированный JSON.
- **Cluster** группирует публикации.
- **Outline** строит предварительную структуру обзора.
- **Synthesis** сравнивает исследования и создаёт проверяемые аналитические утверждения с номерами поддерживающих и противоречащих статей.
- **Writer** не анализирует статьи самостоятельно, а оформляет готовые synthesis claims в академический текст.
- **Reviewer** проверяет соответствие текста synthesis claims и корректность ссылок на статьи.

## Главное изменение версии 0.2.0

Ранее система передавала Writer преимущественно отдельные факты по статьям. Это приводило к последовательному пересказу исследований.

Теперь между Outline и Writer добавлен слой научного синтеза:

```text
ArticleSummary[]
  ↓
SynthesisAgent
  ↓
SynthesisClaim[]
  ↓
Writer
```

Каждый `SynthesisClaim` содержит:

- тип аналитического утверждения;
- текст утверждения;
- номера поддерживающих статей;
- номера противоречащих статей;
- уровень уверенности;
- обоснование;
- ограничения и оговорки.

## Установка

Откройте PowerShell в папке проекта:

```powershell
cd D:\ResearchLabAI
```

Активируйте виртуальное окружение:

```powershell
.\.venv\Scripts\Activate.ps1
```

Установите зависимости:

```powershell
pip install -r requirements.txt
```

Для запуска тестов:

```powershell
pip install -r requirements-dev.txt
python -m pytest -q
```

## Настройка API-ключа

Создайте локальный файл `.env` на основе `.env.example`:

```powershell
Copy-Item .env.example .env
notepad .env
```

Для OpenRouter заполните:

```text
OPENROUTER_API_KEY=ваш_ключ
```

Файл `.env` и папка `API` исключены из Git.

## Запуск

```powershell
python main.py
```

## Проверка

Локальные unit-тесты не вызывают внешние API. Интеграционные тесты Gemini и OpenRouter автоматически пропускаются, если соответствующий ключ отсутствует.

Текущий проверенный результат:

```text
7 passed
3 skipped
```

## Текущие ограничения

- Summarizer пока анализирует преимущественно metadata и abstract, а не полный PDF.
- Поиск выполняется через Crossref и OpenAlex.
- Cluster пока использует простую тематическую группировку.
- Автоматический цикл исправления `Reviewer → Revision → Reviewer` ещё не реализован.
- Масштабируемый map-reduce synthesis для сотен и тысяч статей будет добавлен следующим отдельным этапом.

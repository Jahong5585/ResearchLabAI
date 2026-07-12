from Core.prompt_loader import load_prompt
from Providers.manager import ask
from Core.output_cleaner import OutputCleaner

from Config import settings


class BaseAgent:

    PROMPT_NAME = None

    MODEL_NAME = None

    def get_system_prompt(self):

        if self.PROMPT_NAME is None:
            raise ValueError("PROMPT_NAME не указан.")

        return load_prompt(self.PROMPT_NAME)

    def get_model(self):

        if self.MODEL_NAME:

            return getattr(
                settings,
                self.MODEL_NAME
            )

        return settings.OPENROUTER_MODEL

    def ask_llm(self, prompt):

        system_prompt = self.get_system_prompt()

        answer = ask(

            prompt=prompt,

            system_prompt=system_prompt,

            model=self.get_model()

        )

        return OutputCleaner.clean(answer)

    def execute(self, task):

        system_prompt = self.get_system_prompt()

        context = task.memory.all()

        prompt = f"""
{system_prompt}

========================================

Контекст:

{context}

========================================

Запрос пользователя:

{task.user_request}
"""

        answer = ask(

            prompt=prompt,

            system_prompt=system_prompt,

            model=self.get_model()

        )

        answer = OutputCleaner.clean(answer)

        task.result = answer

        task.memory.set(

            self.__class__.__name__,

            answer

        )

        return answer
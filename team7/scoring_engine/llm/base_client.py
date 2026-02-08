class BaseLLMClient:
    """
    Abstract LLM interface.
    """

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        raise NotImplementedError

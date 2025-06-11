from lwe.core.tool import Tool

class AnthropicWebSearch(Tool):

    def get_config(self) -> dict:
        return {
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": 5,
        }

    def __call__(self) -> None:
        pass

from lwe.core.function import Function

CATEGORIES = [
    'VALID',
    'UNAVAILABLE',
    'OUT_OF_SCOPE'
]


class CategorizeUserQuestion(Function):

    def get_config(self) -> dict:
        return {
            "name": "categorize_user_question",
            "description": "Categorize a user's question in reference to a knowledge base",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": f"The category of the question, must be one of: {', '.join(CATEGORIES)}",
                        "enum": CATEGORIES,
                    },
                    "reason": {
                        "type": "string",
                        "description": "A short explanation for why the category was chosen for the question",
                    },
                },
                "required": [
                    "category",
                    "reason",
                ],
            },
        }

    def __call__(self, category: str, reason: str) -> dict:
        """
        Categorize a user's question in reference to a knowledge base

        :param category: The category of the question.
        :type category: str
        :param reason: A short explanation for why the category was chosen for the question.
        :type reason:: str
        :return: A dictionary containing the category of the question.
        :rtype: dict
        """
        try:
            output = {
                'category': category,
                'reason': reason,
                'message': 'Determined the category of the question',
            }
        except Exception as e:
            output = {
                'error': str(e),
            }
        return output

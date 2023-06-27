from lwe.core.function import Function

class UppercaseContent(Function):
    def __call__(self, content: str) -> dict:
        """
        Uppercase the provided content

        :param content: The content to uppercase.
        :type content: str
        :return: A dictionary containing the uppercased content.
        :rtype: dict
        """
        try:
            uppercased_content = content.upper()
            output = {
                'result': uppercased_content,
                'message': 'Uppercased the content string',
            }
        except Exception as e:
            output = {
                'error': str(e),
            }
        return output

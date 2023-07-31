# import base64
from lwe.core.function import Function

class ApplyCodeChanges(Function):
    def __call__(self, changed_code: str, applied_changes: str = None) -> dict:
        """
        Apply changes to the provided code based on the provided instructions.

        :param changed_code: The changed code.
        :type changed_code: str
        :param applied_changes: A brief description of the changes applied to the original code.
        :type applied_changes: str, optional
        :return: A dictionary containing the changed code and list of applied changes.
        :rtype: dict
        """
        try:
            # decoded_string = base64.b64decode(changed_code).decode()
            output = {
                'applied_changes': applied_changes,
                # 'changed_code': decoded_string,
                'changed_code': changed_code,
                'message': 'Applied the changes to the code',
            }
        except Exception as e:
            output = {
                'error': str(e),
            }
        return output

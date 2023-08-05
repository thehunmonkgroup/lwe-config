from pydantic import BaseModel, Field
from typing import List
from enum import Enum

from lwe.core.function import Function


class Reaction(Enum):
    trust: str = 'trust'
    disagree: str = 'disagree'

class UserReaction(BaseModel):
    user_id: int = Field(..., description="The ID of the persona reacting to the post")
    reaction: Reaction = Field(..., description="The user's reaction to the post")

class UserReactions(BaseModel):
    reactions: List[UserReaction] = Field(..., description="List of user reactions")

class UserPostReactions(Function):

    def get_config(self) -> dict:
        return {
            "name": "user_post_reactions",
            "description": "Store post reactions from users",
            "parameters": UserReactions.schema()
        }

    def __call__(self, reactions: List[dict]) -> dict:
        """
        Store post reactions from users

        :param reactions: The list of reactions.
        :type reactions: List[dict]
        :return: A dictionary containing the reactions from users.
        :rtype: dict
        """
        try:
            output = {
                'reactions': reactions,
                'message': 'Stored the reactions from users',
            }
        except Exception as e:
            output = {
                'error': str(e),
            }
        return output

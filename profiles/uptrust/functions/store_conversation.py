from pydantic import BaseModel, Field
from typing import List

from lwe.core.function import Function

class Comment(BaseModel):
    comment_id: str = Field(..., description="The ID of the comment")
    user_id: str = Field(..., description="The ID of the user making the comment")
    comment: str = Field(..., description="The user's comment")

class SubTopic(BaseModel):
    comment_id: str = Field(..., description="The ID of the comment where a suggested sub-topic begins")
    sub_topic: str = Field(..., description="The suggested sub-topic")

class CommentThread(BaseModel):
    comments: List[Comment] = Field(..., description="List of comments, in the order they were made")
    subtopics: List[SubTopic] = Field(..., description="List of sub-topics")

class StoreConversation(Function):

    def get_config(self) -> dict:
        return {
            "name": "store_conversation",
            "description": "Store the conversation comments and suggested sub-topics",
            "parameters": CommentThread.schema()
        }

    def __call__(self, comments: List[dict], subtopics: List[dict]) -> dict:
        """
        Store the conversation comments and suggested sub-topics

        :param comments: The list of comments.
        :type comments: List[dict]
        :param subtopics: The list of suggested sub-topics.
        :type subtopics: List[dict]
        :return: A dictionary containing the comments and sub-topics.
        :rtype: dict
        """
        try:
            output = {
                'comments': comments,
                'subtopics': subtopics,
                'message': 'Stored the conversation comments and suggested sub-topics',
            }
        except Exception as e:
            output = {
                'error': str(e),
            }
        return output

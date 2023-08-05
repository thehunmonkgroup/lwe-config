from pydantic import BaseModel, Field
from typing import List

from lwe.core.function import Function

class Post(BaseModel):
    post_id: int = Field(..., description="The ID of the post")
    user_id: int = Field(..., description="The ID of the user making the post")
    content: str = Field(..., description="The content of the user's post")

class SubTopic(BaseModel):
    post_id: int = Field(..., description="The ID of the post where a suggested sub-topic begins")
    sub_topic: str = Field(..., description="The suggested sub-topic")

class ConversationThread(BaseModel):
    posts: List[Post] = Field(..., description="List of posts, in the order they were made")
    subtopics: List[SubTopic] = Field(..., description="List of sub-topics")

class StoreConversation(Function):

    def get_config(self) -> dict:
        return {
            "name": "store_conversation",
            "description": "Store the conversation posts and suggested sub-topics",
            "parameters": ConversationThread.schema()
        }

    def __call__(self, posts: List[dict], subtopics: List[dict]) -> dict:
        """
        Store the conversation posts and suggested sub-topics

        :param posts: The list of posts.
        :type posts: List[dict]
        :param subtopics: The list of suggested sub-topics.
        :type subtopics: List[dict]
        :return: A dictionary containing the posts and sub-topics.
        :rtype: dict
        """
        try:
            output = {
                'posts': posts,
                'subtopics': subtopics,
                'message': 'Stored the conversation posts and suggested sub-topics',
            }
        except Exception as e:
            output = {
                'error': str(e),
            }
        return output

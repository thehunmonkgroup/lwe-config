import re

from pydantic import BaseModel, Field
from typing import List

from lwe.core.tool import Tool

class Sentiment(BaseModel):
    name: str = Field(..., description="Single word sentiment description")

class Topic(BaseModel):
    name: str = Field(..., description="One or two word description of a topic")

class ExtractSentimentTopics(BaseModel):
    sentiments: List[Sentiment] = Field(..., description="One to three sentiment descriptions")
    topics: List[Topic] = Field(..., description="One to three topic descriptions")

class StoreSentimentAndTopics(Tool):

    def clean_results(self, results):
        return [re.sub(r'\W', '_', elem.lower()) for elem in results]

    def get_config(self) -> dict:
        return {
            "name": "store_sentiment_and_topics",
            "description": "Store the extracted sentiments and topics",
            "parameters": ExtractSentimentTopics.schema()
        }

    def __call__(self, sentiments: List[str], topics: List[str]) -> dict:
        try:
            output = {
                'sentiments': self.clean_results(sentiments),
                'topics': self.clean_results(topics),
                'message': 'Stored the sentiments and topics',
            }
        except Exception as e:
            output = {
                'error': str(e),
            }
            if self.config.debug:
                import traceback
                traceback.print_exc()

        return output

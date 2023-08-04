#!/usr/bin/env python

import argparse
import logging
import psycopg2
import random
from psycopg2 import sql
from psycopg2.extras import DictCursor

from lwe.core.config import Config
from lwe.core import util
from lwe.backends.api.backend import ApiBackend

# Constants
DEFAULT_BRANCH_DEPTH = 5
DEFAULT_USERS_MIN = 3
DEFAULT_USERS_MAX = 8
DEFAULT_THREAD_LENGTH_MIN = 5
DEFAULT_THREAD_LENGTH_MAX = 15
DEFAULT_SUBTOPIC_MIN = 2
DEFAULT_SUBTOPIC_MAX = 5
DEFAULT_DB_HOST = 'localhost'
DEFAULT_DB_NAME = 'uptrust'
DEFAULT_DB_USERNAME = 'general'
DEFAULT_DB_PASSWORD = 'general'
DEFAULT_LWE_PROFILE = 'uptrust'
LWE_CONVERSATION_THREAD_TEMPLATE = 'conversation-thread-generator.md'

class ThreadedConversationGenerator:
    def __init__(self,
                 topic,
                 branch_depth=DEFAULT_BRANCH_DEPTH,
                 users_min=DEFAULT_USERS_MIN,
                 users_max=DEFAULT_USERS_MAX,
                 thread_length_min=DEFAULT_THREAD_LENGTH_MIN,
                 thread_length_max=DEFAULT_THREAD_LENGTH_MAX,
                 subtopic_min=DEFAULT_SUBTOPIC_MIN,
                 subtopic_max=DEFAULT_SUBTOPIC_MAX,
                 db_host=DEFAULT_DB_HOST,
                 db_name=DEFAULT_DB_NAME,
                 db_username=DEFAULT_DB_USERNAME,
                 db_password=DEFAULT_DB_PASSWORD,
                 lwe_profile=DEFAULT_LWE_PROFILE,
                 debug=False):
        self.topic = topic
        self.branch_depth = branch_depth
        self.users_min = users_min
        self.users_max = users_max
        self.thread_length_min = thread_length_min
        self.thread_length_max = thread_length_max
        self.subtopic_min = subtopic_min
        self.subtopic_max = subtopic_max
        self.db_host = db_host
        self.db_name = db_name
        self.db_username = db_username
        self.db_password = db_password
        self.lwe_profile = lwe_profile
        self.conn = psycopg2.connect(host=self.db_host, dbname=self.db_name, user=self.db_username, password=self.db_password)
        config = Config(profile=self.lwe_profile)
        # util.debug.console(config.config)
        self.llm = ApiBackend(config)
        self.debug = debug
        config.set('debug.log.enabled', self.debug)
        level = 'debug' if self.debug else 'info'
        config.set('log.console.level', level)
        config.set('debug.log.level', level)
        # util.debug.console(config.config)
        logging.basicConfig(level=logging.DEBUG if self.debug else logging.INFO)

    def generate_conversation_thread(self, branch_depth, topic, parent_id=None):
        users = self.get_random_users()
        thread_length = random.randint(self.thread_length_min, self.thread_length_max)
        branch_points = random.randint(self.subtopic_min, self.subtopic_max)
        logging.info(f"Generating conversation thread at branch depth: {branch_depth}, for topic: {topic}, parent_id: {parent_id}, users: {len(users)}, thread_length: {thread_length}, branch_points: {branch_points}")
        comments, subtopics = self.llm_conversation_thread(topic, users, thread_length, branch_points)
        for comment in comments:
            comment_id = self.store_comment(comment, parent_id)
            if branch_depth > 0:
                for subtopic in subtopics:
                    if subtopic['comment_id'] == comment['comment_id']:
                        logging.info(f"Found branch point for comment: {comment_id}")
                        branch_depth -= 1
                        self.generate_conversation_thread(branch_depth, subtopic['sub_topic'], comment_id)

    def get_random_users(self):
        num_users = random.randint(self.users_min, self.users_max)
        logging.debug(f"Fetching {num_users} random users from the database")
        cur = self.conn.cursor(cursor_factory=DictCursor)
        cur.execute("SELECT u.username, p.user_id, p.characteristics, p.description FROM users u INNER JOIN personas p ON u.id = p.user_id ORDER BY RANDOM() LIMIT %s", (num_users,))
        return cur.fetchall()

    def llm_conversation_thread(self, topic, users, thread_length, branch_points):
        template_vars = {
            'thread_length': self.int_to_en(thread_length),
            'personas': self.format_users_to_personas(users),
            'topic': topic,
            'branch_points': self.int_to_en(branch_points),
        }
        success, response, _user_message = self.llm.run_template(LWE_CONVERSATION_THREAD_TEMPLATE, template_vars)
        assert success
        return response['comments'], response['subtopics']

    def format_users_to_personas(self, users):
        formatted_personas = []
        for i, user in enumerate(users, start=1):
            formatted_persona = f"""
[Persona {i}]

ID: {user['user_id']}
Name: {user['username']}

CHARACTERISTICS:

{user['characteristics']}

DESCRIPTION:

{user['description']}
    """
            formatted_personas.append(formatted_persona)
        return "\n\n".join(formatted_personas)

    def store_comment(self, comment, parent_id):
        logging.info(f"Storing comment, ID: {comment['comment_id']}, comment: {comment['comment']}")
        cur = self.conn.cursor(cursor_factory=DictCursor)
        cur.execute(sql.SQL("INSERT INTO posts (user_id, post_content, parent_id, created_at, updated_at) VALUES (%s, %s, %s, NOW(), NOW()) RETURNING id"), (comment['user_id'], comment['comment'], parent_id))
        self.conn.commit()
        return cur.fetchone()['id']

    def int_to_en(self, num):
        d = {
            0: 'zero', 1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five',
            6: 'six', 7: 'seven', 8: 'eight', 9: 'nine', 10: 'ten',
            11: 'eleven', 12: 'twelve', 13: 'thirteen', 14: 'fourteen',
            15: 'fifteen', 16: 'sixteen', 17: 'seventeen', 18: 'eighteen',
            19: 'nineteen', 20: 'twenty',
            30: 'thirty', 40: 'forty', 50: 'fifty', 60: 'sixty',
            70: 'seventy', 80: 'eighty', 90: 'ninety'
        }
        assert (0 <= num)
        if num < 20:
            return d[num]
        if num < 100:
            if num % 10 == 0:
                return d[num]
            else:
                return d[num // 10 * 10] + '-' + d[num % 10]
        if num < 1000:
            if num % 100 == 0:
                return d[num // 100] + ' hundred'
            else:
                return d[num // 100] + ' hundred and ' + self.int_to_en(num % 100)
        raise AssertionError('num is too large: %s' % str(num))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate a multi-branching threaded conversation.')
    parser.add_argument('topic', type=str, help='The topic for the root conversation thread.')
    parser.add_argument('--branch-depth', type=int, default=DEFAULT_BRANCH_DEPTH, help='The number of layers in the branching tree.')
    parser.add_argument('--users-min', type=int, default=DEFAULT_USERS_MIN, help='The minimum number of users participating in an individual conversation thread.')
    parser.add_argument('--users-max', type=int, default=DEFAULT_USERS_MAX, help='The maximum number of users participating in an individual conversation thread.')
    parser.add_argument('--thread-length-min', type=int, default=DEFAULT_THREAD_LENGTH_MIN, help='The minimum number of comments in an individual conversation thread.')
    parser.add_argument('--thread-length-max', type=int, default=DEFAULT_THREAD_LENGTH_MAX, help='The maximum number of comments in an individual conversation thread.')
    parser.add_argument('--subtopic-min', type=int, default=DEFAULT_SUBTOPIC_MIN, help='The minimum number of subtopics to branch from a conversation thread.')
    parser.add_argument('--subtopic-max', type=int, default=DEFAULT_SUBTOPIC_MAX, help='The maximum number of subtopics to branch from a conversation thread.')
    parser.add_argument('--db-host', type=str, default=DEFAULT_DB_HOST, help='The database host address.')
    parser.add_argument('--db-name', type=str, default=DEFAULT_DB_NAME, help='The name of the database used for storage.')
    parser.add_argument('--db-username', type=str, default=DEFAULT_DB_USERNAME, help='The database login username.')
    parser.add_argument('--db-password', type=str, default=DEFAULT_DB_PASSWORD, help='The database login password.')
    parser.add_argument('--lwe-profile', type=str, default=DEFAULT_LWE_PROFILE, help='The LWE profile to use.')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging.')
    args = parser.parse_args()

    generator = ThreadedConversationGenerator(
        args.topic,
        args.branch_depth,
        args.users_min,
        args.users_max,
        args.thread_length_min,
        args.thread_length_max,
        args.subtopic_min,
        args.subtopic_max,
        args.db_host,
        args.db_name,
        args.db_username,
        args.db_password,
        args.lwe_profile,
        args.debug
    )
    generator.generate_conversation_thread(args.branch_depth, args.topic)

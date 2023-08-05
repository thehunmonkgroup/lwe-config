#!/usr/bin/env python

import argparse
import logging
import psycopg2
import random
from psycopg2 import sql
from psycopg2.extras import DictCursor

from lwe.core.config import Config
# from lwe.core import util
from lwe.backends.api.backend import ApiBackend

import tiktoken
from langchain.embeddings import OpenAIEmbeddings

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
LWE_USER_POST_REACTIONS_TEMPLATE = 'user-post-reaction-generator.md'
EMBEDDING_MODEL = 'text-embedding-ada-002'
EMBEDDING_CTX_LENGTH = 8191

class BaseConversationGenerator:

    def setup_db_conn(self, db_host, db_name, db_username, db_password):
        self.log.debug(f"Setting up DB connection: {db_host, db_name, db_username, db_password}")
        self.conn = psycopg2.connect(host=db_host, dbname=db_name, user=db_username, password=db_password)

    def setup_lwe_backend(self, lwe_profile):
        self.log.debug(f"Setting up LWE backend with profile: {lwe_profile}")
        self.lwe_profile = lwe_profile
        config = Config(profile=self.lwe_profile)
        config.set('debug.log.enabled', self.debug)
        level = 'debug' if self.debug else 'warning'
        config.set('log.console.level', level)
        config.set('debug.log.level', level)
        self.llm = ApiBackend(config)

    def setup_embeddings(self):
        self.log.debug(f"Setting up embeddings, model: {EMBEDDING_MODEL}, content length: {EMBEDDING_CTX_LENGTH}")
        self.embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL, embedding_ctx_length=EMBEDDING_CTX_LENGTH)

    def get_logger(self):
        logger = logging.getLogger(self.__class__.__name__)
        # Prevent duplicate loggers.
        if logger.hasHandlers():
            return logger
        logger.setLevel(logging.DEBUG if self.debug else logging.INFO)
        log_console_handler = logging.StreamHandler()
        log_console_handler.setFormatter(logging.Formatter('%(name)s - %(levelname)s - %(message)s'))
        log_console_handler.setLevel(logging.DEBUG if self.debug else logging.INFO)
        logger.addHandler(log_console_handler)
        return logger

    def get_random_users(self):
        num_users = random.randint(self.users_min, self.users_max)
        self.log.debug(f"Fetching {num_users} random users from the database")
        cur = self.conn.cursor(cursor_factory=DictCursor)
        cur.execute("SELECT u.username, p.user_id, p.characteristics, p.description FROM users u INNER JOIN personas p ON u.id = p.user_id ORDER BY RANDOM() LIMIT %s", (num_users,))
        return cur.fetchall()

    def format_users_to_personas(self, users):
        self.log.debug(f"Formatting {len(users)} users to personas")
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

    def truncate_text_tokens(self, text, embedding_model=EMBEDDING_MODEL, max_tokens=EMBEDDING_CTX_LENGTH):
        """Truncate a string to have `max_tokens` according to the given encoding."""
        encoding = tiktoken.encoding_for_model(embedding_model)
        return encoding.encode(text)[:max_tokens]


class ThreadedConversationGenerator(BaseConversationGenerator):
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
        self.debug = debug
        self.log = self.get_logger()
        self.topic = topic
        self.branch_depth = branch_depth
        self.users_min = users_min
        self.users_max = users_max
        self.thread_length_min = thread_length_min
        self.thread_length_max = thread_length_max
        self.subtopic_min = subtopic_min
        self.subtopic_max = subtopic_max
        self.setup_lwe_backend(lwe_profile)
        self.setup_db_conn(db_host, db_name, db_username, db_password)
        self.setup_embeddings()
        # util.debug.console(config.config)

    def generate_conversation_thread(self, branch_depth, topic, parent_id=None):
        branch_depth -= 1
        users = self.get_random_users()
        thread_length = random.randint(self.thread_length_min, self.thread_length_max)
        branch_points = random.randint(self.subtopic_min, self.subtopic_max)
        self.log.info(f"Generating conversation thread for topic: {topic}, parent_id: {parent_id}, users: {len(users)}, thread_length: {thread_length}, branch_points: {branch_points}")
        self.log.info(f"Branch depth remaining: {branch_depth}")
        posts, subtopics = self.llm_conversation_thread(topic, users, thread_length, branch_points)
        for post in posts:
            post_id = self.store_post(post, parent_id)
            # NOTE: As written, this stores the topic for EVERY post, which is not
            # technically necessary, as it could be stored once then looked up by
            # post_id or parent_id.
            self.store_topic(post_id, topic)
            if branch_depth > 0:
                for subtopic in subtopics:
                    if subtopic['post_id'] == post['post_id']:
                        self.log.info(f"Found branch point for post: {post_id}")
                        self.generate_conversation_thread(branch_depth, subtopic['sub_topic'], post_id)

    def llm_conversation_thread(self, topic, users, thread_length, branch_points):
        template_vars = {
            'thread_length': self.int_to_en(thread_length),
            'personas': self.format_users_to_personas(users),
            'topic': topic,
            'branch_points': self.int_to_en(branch_points),
        }
        self.log.debug(f"Calling LLM with template: {LWE_CONVERSATION_THREAD_TEMPLATE}")
        success, response, _user_message = self.llm.run_template(LWE_CONVERSATION_THREAD_TEMPLATE, template_vars)
        assert success
        return response['posts'], response['subtopics']

    def store_post(self, post, parent_id):
        user_id = post['user_id']
        content = post['content']
        self.log.debug(f"Storing post, ID: {post['post_id']}, for user: {user_id}, content: {content}")
        cur = self.conn.cursor(cursor_factory=DictCursor)
        embedded_content = self.post_to_embedding(content)
        cur.execute(sql.SQL("INSERT INTO posts (user_id, post_content, post_vec, parent_id, created_at, updated_at) VALUES (%s, %s, %s, %s, NOW(), NOW()) RETURNING id"), (user_id, content, embedded_content, parent_id))
        self.conn.commit()
        return cur.fetchone()['id']

    def store_topic(self, post_id, topic):
        self.log.debug(f"Storing topic for post, ID: {post_id}, topic: {topic}")
        cur = self.conn.cursor(cursor_factory=DictCursor)
        cur.execute(sql.SQL("INSERT INTO post_topics (post_id, topic, created_at, updated_at) VALUES (%s, %s, NOW(), NOW())"), (post_id, topic))
        self.conn.commit()

    def post_to_embedding(self, post):
        self.log.debug(f"Generating embedding for post: {post}")
        tokenized_post = self.truncate_text_tokens(post, EMBEDDING_MODEL, EMBEDDING_CTX_LENGTH)
        embedding = self.embeddings.embed_query(tokenized_post)
        return embedding

class PostReactionGenerator(BaseConversationGenerator):
    def __init__(self,
                 users_min=DEFAULT_USERS_MIN,
                 users_max=DEFAULT_USERS_MAX,
                 db_host=DEFAULT_DB_HOST,
                 db_name=DEFAULT_DB_NAME,
                 db_username=DEFAULT_DB_USERNAME,
                 db_password=DEFAULT_DB_PASSWORD,
                 lwe_profile=DEFAULT_LWE_PROFILE,
                 debug=False):
        self.debug = debug
        self.log = self.get_logger()
        self.users_min = users_min
        self.users_max = users_max
        self.setup_lwe_backend(lwe_profile)
        self.setup_db_conn(db_host, db_name, db_username, db_password)

    def generate_post_reactions(self):
        cur = self.conn.cursor(cursor_factory=DictCursor)
        cur.execute("SELECT p.id, p.post_content, pt.topic FROM posts p INNER JOIN post_topics pt ON p.id = pt.post_id")
        posts = cur.fetchall()
        for post in posts:
            users = self.get_random_users()
            template_vars = {
                'topic': post['topic'],
                'post': post['post_content'],
                'personas': self.format_users_to_personas(users),
            }
            self.log.debug(f"Calling LLM with template: {LWE_USER_POST_REACTIONS_TEMPLATE}")
            success, result, _user_message = self.llm.run_template(LWE_USER_POST_REACTIONS_TEMPLATE, template_vars)
            assert success
            for reaction in result['reactions']:
                self.store_reaction(post['id'], reaction['user_id'], reaction['reaction'])

    def store_reaction(self, post_id, user_id, reaction):
        self.log.debug(f"Storing reaction, post ID: {post_id}, user ID: {user_id}, reaction: {reaction}")
        cur = self.conn.cursor(cursor_factory=DictCursor)
        cur.execute(sql.SQL("INSERT INTO edges (edge_out_user_id, edge_in_post_id, edge_type, created_at) VALUES (%s, %s, %s, NOW())"), (user_id, post_id, reaction))
        self.conn.commit()


def run_threaded_conversation_generator(args):
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
    generator.log.info(f"Starting conversation thread generation with root topic: {args.topic}")
    generator.generate_conversation_thread(args.branch_depth, args.topic)
    generator.log.info("Finished conversation thread generation")


def run_post_reaction_generator(args):
    generator = PostReactionGenerator(
        args.users_min,
        args.users_max,
        args.db_host,
        args.db_name,
        args.db_username,
        args.db_password,
        args.lwe_profile,
        args.debug
    )
    generator.log.info("Starting post reaction generation")
    generator.generate_post_reactions()
    generator.log.info("Finished post reaction generation")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate a multi-branching threaded conversation or post reactions.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--generate-conversation', action='store_true', help='Generate a multi-branching threaded conversation.')
    group.add_argument('--generate-reactions', action='store_true', help='Generate reactions to posts.')
    parser.add_argument('--topic', type=str, help='The topic for the root conversation thread.')
    parser.add_argument('--branch-depth', type=int, default=DEFAULT_BRANCH_DEPTH, help=f'The number of layers in the branching tree. Default is {DEFAULT_BRANCH_DEPTH}')
    parser.add_argument('--users-min', type=int, default=DEFAULT_USERS_MIN, help=f'The minimum number of users participating in an individual conversation thread or reacting to a post. Default is {DEFAULT_USERS_MIN}')
    parser.add_argument('--users-max', type=int, default=DEFAULT_USERS_MAX, help=f'The maximum number of users participating in an individual conversation thread or reacting to a post. Default is {DEFAULT_USERS_MAX}')
    parser.add_argument('--thread-length-min', type=int, default=DEFAULT_THREAD_LENGTH_MIN, help=f'The minimum number of posts in an individual conversation thread. Default is {DEFAULT_THREAD_LENGTH_MIN}')
    parser.add_argument('--thread-length-max', type=int, default=DEFAULT_THREAD_LENGTH_MAX, help=f'The maximum number of posts in an individual conversation thread. Default is {DEFAULT_THREAD_LENGTH_MAX}')
    parser.add_argument('--subtopic-min', type=int, default=DEFAULT_SUBTOPIC_MIN, help=f'The minimum number of subtopics to branch from a conversation thread. Default is {DEFAULT_SUBTOPIC_MIN}')
    parser.add_argument('--subtopic-max', type=int, default=DEFAULT_SUBTOPIC_MAX, help=f'The maximum number of subtopics to branch from a conversation thread. Default is {DEFAULT_SUBTOPIC_MAX}')
    parser.add_argument('--db-host', type=str, default=DEFAULT_DB_HOST, help=f'The database host address. Default is {DEFAULT_DB_HOST}')
    parser.add_argument('--db-name', type=str, default=DEFAULT_DB_NAME, help=f'The name of the database used for storage. Default is {DEFAULT_DB_NAME}')
    parser.add_argument('--db-username', type=str, default=DEFAULT_DB_USERNAME, help=f'The database login username. Default is {DEFAULT_DB_USERNAME}')
    parser.add_argument('--db-password', type=str, default=DEFAULT_DB_PASSWORD, help=f'The database login password. Default is {DEFAULT_DB_PASSWORD}')
    parser.add_argument('--lwe-profile', type=str, default=DEFAULT_LWE_PROFILE, help=f'The LWE profile to use. Default is {DEFAULT_LWE_PROFILE}')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging.')

    args = parser.parse_args()

    if args.generate_conversation:
        if not args.topic:
            parser.error("Topic is required when generating a conversation.")
            parser.print_help()
            exit(1)
        run_threaded_conversation_generator(args)
    elif args.generate_reactions:
        run_post_reaction_generator(args)

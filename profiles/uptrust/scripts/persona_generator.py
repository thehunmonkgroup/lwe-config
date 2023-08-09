#!/usr/bin/env python

import json
import psycopg2
import random
import os
import argparse
import logging

from psycopg2 import sql

from lwe.core.config import Config
# from lwe.core import util
from lwe.backends.api.backend import ApiBackend

# Constants.
DEFAULT_ITERATIONS = 30
DEFAULT_START_ITERATION = 1
DEFAULT_LWE_PROFILE = 'uptrust'
DEFAULT_PERSONA_JSON_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'persona-characteristics.json')
DEFAULT_OUTPUT_DIR = "/tmp/personas"
DEFAULT_DB_HOST = 'localhost'
DEFAULT_DB_NAME = 'uptrust'
DEFAULT_DB_USERNAME = 'general'
DEFAULT_DB_PASSWORD = 'general'
LWE_PERSONA_GENERATOR_TEMPLATE = 'persona-generator.md'

class PersonaGenerator:

    def __init__(self,
                 lwe_profile=DEFAULT_LWE_PROFILE,
                 persona_json_file=DEFAULT_PERSONA_JSON_FILE,
                 iterations=DEFAULT_ITERATIONS,
                 start_iteration=DEFAULT_START_ITERATION,
                 output_dir=DEFAULT_OUTPUT_DIR,
                 db_host=DEFAULT_DB_HOST,
                 db_name=DEFAULT_DB_NAME,
                 db_username=DEFAULT_DB_USERNAME,
                 db_password=DEFAULT_DB_PASSWORD,
                 debug=False,):
        self.debug = debug
        self.log = self.get_logger()
        self.lwe_profile = lwe_profile
        self.persona_json_file = persona_json_file
        self.iterations = iterations
        self.start_iteration = start_iteration
        self.output_dir = output_dir
        self.characteristics = []
        self.setup_lwe_backend(lwe_profile)
        self.setup_db_conn(db_host, db_name, db_username, db_password)

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

    def retrieve_json_data(self):
        self.log.debug(f"Retrieving JSON data from URL: {self.persona_json_file}")
        with open(self.persona_json_file, 'r') as f:
            data = json.load(f)
        for key, values in data.items():
            data[key] = [k for k, v in values.items() for _ in range(v)]
        return data

    def generate_personas(self):
        data = self.retrieve_json_data()
        for iteration in range(self.start_iteration, self.start_iteration + self.iterations):
            self.log.debug(f"Iteration: {iteration}")
            if not self.persona_exists(iteration):
                characteristics = self.generate_characteristics(data)
                name, description, formatted_characteristics = self.generate_persona(iteration, characteristics)
                self.store_persona_in_db(iteration, name, description, formatted_characteristics)
                self.store_persona_in_file(iteration, name, description, formatted_characteristics)

    def persona_exists(self, iteration):
        self.log.debug(f"Checking if persona {iteration} exists")
        cur = self.conn.cursor()
        cur.execute("SELECT id FROM users WHERE id = %s", (iteration,))
        result = cur.fetchone()
        if result:
            self.log.info(f"Persona {iteration} already exists")
        return result is not None

    def generate_characteristics(self, data):
        self.log.debug("Generating characteristics")
        characteristics = {}
        for key in data.keys():
            value = random.choice(data[key])
            characteristics[key] = value
        return characteristics

    def format_characteristics(self, characteristics):
        self.log.debug("Formatting characteristics")
        return "\n".join(f"{k}: {v}" for k, v in characteristics.items())

    def generate_persona(self, iteration, characteristics):
        # Stub for the developer to fill in
        formatted_characteristics = self.format_characteristics(characteristics)
        self.log.info(f"Generatering persona: {iteration}\n\nCharacteristics:\n\n{formatted_characteristics}\n")
        response = self.call_llm(formatted_characteristics)
        name = response['name']
        description = response['description']
        self.log.info(f"Generated persona {iteration}:\n\nName: {name}\n\nDescription: {description}\n")
        return name, description, formatted_characteristics

    def call_llm(self, formatted_characteristics):
        template_vars = {
            'formatted_characteristics': formatted_characteristics,
        }
        self.log.debug(f"Calling LLM with template: {LWE_PERSONA_GENERATOR_TEMPLATE}")
        success, response, _user_message = self.llm.run_template(LWE_PERSONA_GENERATOR_TEMPLATE, template_vars)
        assert success
        return response

    def store_persona_in_db(self, iteration, name, description, characteristics_string):
        self.log.debug(f"Storing persona {iteration} in DB")
        cur = self.conn.cursor()
        cur.execute(sql.SQL("INSERT INTO users (id, username, created_at) VALUES (%s, %s, NOW())"), (iteration, name))
        cur.execute(sql.SQL("INSERT INTO personas (user_id, characteristics, description, created_at, updated_at) VALUES (%s, %s, %s, NOW(), NOW())"), (iteration, characteristics_string, description))
        self.conn.commit()

    def store_persona_in_file(self, iteration, name, description, formatted_characteristics):
        file = f"persona-{iteration}"
        self.log.debug(f"Storing persona {iteration} in file {self.output_dir}/{file}")
        with open(os.path.join(self.output_dir, file), "w") as f:
            f.write(f"CHARACTERISTICS:\n\n{formatted_characteristics}\n\nNAME:\n\n{name}, DESCRIPTION:\n\n{description}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate personas based on a provided characteristics JSON spec.')
    parser.add_argument('--profile', default=DEFAULT_LWE_PROFILE, help=f'Profile to use for LLM (default: {DEFAULT_LWE_PROFILE})')
    parser.add_argument('--persona-json-file', default=DEFAULT_PERSONA_JSON_FILE, help=f'JSON characteristics file to generate personas from (default: {DEFAULT_PERSONA_JSON_FILE})')
    parser.add_argument('--iterations', type=int, default=DEFAULT_ITERATIONS, help=f'Number of iterations to generate personas (default: {DEFAULT_ITERATIONS})')
    parser.add_argument('--start-iteration', type=int, default=DEFAULT_START_ITERATION, help=f'Iteration start position (default: {DEFAULT_START_ITERATION})')
    parser.add_argument('--output-dir', default=DEFAULT_OUTPUT_DIR, help=f'Directory to store generated persona files (default: {DEFAULT_OUTPUT_DIR})')
    parser.add_argument('--db-host', type=str, default=DEFAULT_DB_HOST, help=f'The database host address (default: {DEFAULT_DB_HOST}).')
    parser.add_argument('--db-name', type=str, default=DEFAULT_DB_NAME, help=f'The name of the database used for storage (default: {DEFAULT_DB_NAME}).')
    parser.add_argument('--db-username', type=str, default=DEFAULT_DB_USERNAME, help=f'The database login username (default: {DEFAULT_DB_USERNAME}).')
    parser.add_argument('--db-password', type=str, default=DEFAULT_DB_PASSWORD, help=f'The database login password (default: {DEFAULT_DB_PASSWORD}).')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging.')

    args = parser.parse_args()

    # Create and run the PersonaGenerator
    generator = PersonaGenerator(
        args.profile,
        args.persona_json_file,
        args.iterations,
        args.start_iteration,
        args.output_dir,
        args.db_host,
        args.db_name,
        args.db_username,
        args.db_password,
        args.debug,
    )
    generator.log.info(f"Starting personas generation, iterations: {args.iterations}")
    generator.generate_personas()
    generator.log.info("Finished personas generation")

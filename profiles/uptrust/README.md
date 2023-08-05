# Uptrust LWE configurations and scripts.

Uptrust configuration files and scripts for use with [LLM Workflow Engine](https://github.com/llm-workflow-engine/llm-workflow-engine)

## Scripts

### calculate_max_posts.py

Simple script to easily get a sense for the maximum total posts you'll get when using a particular branch points / depth configuration.

```bash
./calculate_max_posts.py -h
./calculate_max_posts.py -v -b 4 -d 10
```

### threaded_conversation_generator.py

Script to generate a threaded conversation and reactions to posts.

You'll need:

* Uptrust Postgres database schema installed
* LWE installed and configured
* The `psycopg2` package

```bash
pip install psycopg2
pip install git+https://github.com/llm-workflow-engine/llm-workflow-engine
# Symlink this repo to ${HOME}/.config/llm-workflow-engine
# Install the lwe database, create the first user.
lwe
```

Many options for this script, see the help:

```bash
./threaded_conversation_generator.py -h
```

Conversation threads and reactions are generated separately from each other.

First, generate the conversation thread:

```bash
./threaded_conversation_generator.py --topic "War solves nothing" --branch-depth 3 --subtopic-max 2 --thread-length-max 8 --generate-conversation
```

Then, generate reactions to the thread posts:

```bash
./threaded_conversation_generator.py --generate-reactions
```

Default output from this script is fairly readable, adding `--debug` flag will produce a **lot** of debug info.

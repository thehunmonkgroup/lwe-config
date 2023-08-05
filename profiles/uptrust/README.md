# Uptrust LWE configurations and scripts.

Uptrust configuration files and scripts for use with [LLM Workflow Engine](https://github.com/llm-workflow-engine/llm-workflow-engine)


## Dependencies

You'll need:

* OpenAI account with GPT-4 access and an API key created
* Uptrust Postgres database schema installed
* LWE installed and configured
* The `psycopg2` package

OpenAI API keys can be generated here: https://platform.openai.com/account/api-keys

```bash
# You'll want to put this export somewhere permanent so the key is always available in your CLI environment.
export OPENAI_API_KEY="sk-...the rest of your key..."
pip install psycopg2
pip install git+https://github.com/llm-workflow-engine/llm-workflow-engine
# Symlink this repo to the default LWE config location.
ln -s "$(pwd)" "$(lwe config config_dir)"
# Install the lwe database, create the first user.
lwe -p uptrust
```


## Workflows

Workflows can be listed and run from within LWE.

Start LWE:

```bash
lwe -p uptrust
```

List workflows:

```
/workflows
```

View a particular workflow config:

```
/workflow-show [workflow name]
```

Run a workflow:

```
/workflow-run [workflow name]
```


## Scripts


### calculate_max_posts.py

Simple script to easily get a sense for the maximum total posts you'll get when using a particular branch points / depth configuration.

```bash
./calculate_max_posts.py -h
./calculate_max_posts.py -v -b 4 -d 10
```


### persona_generator.py

Generates unique names, characteristics, and descriptions for users based on a configurable JSON file,
and stores them in the database.

Default persona file lives at [data/persona-characteristics.json](data/persona-characteristics.json)

The script only generates a persona if the iteration its on does **not** have a user in the database with that ID.
This allows selective replacement of personas.

Run with help to see available arguements:

```bash
./persona_generator.py -h
```

Generate 5 personas:

```bash
./persona_generator.py --iterations 5
```


### threaded_conversation_generator.py

Script to generate a threaded conversation and reactions to posts.

Many options for this script, see the help:

```bash
./threaded_conversation_generator.py -h
```

Conversation threads and reactions are generated separately from each other.

First, generate the conversation thread:

```bash
./threaded_conversation_generator.py --generate-conversation --topic "War solves nothing" --branch-depth 3 --subtopic-max 2 --thread-length-max 8
```

Then, generate reactions to the thread posts:

```bash
./threaded_conversation_generator.py --generate-reactions
```

Default output from this script is fairly readable, adding `--debug` flag will produce a **lot** of debug info.


## Refining the generation of personas/posts/reactions

There are two places to look to refine the outputs:

1. **[data/persona-characteristics.json](data/persona-characteristics.json):** Here you can alter the characteristics, the available values for those characteristics, and the 'frequency' that a value is selected (higher numbers are selected more frequently)
2. **[templates](templates):** The templates contain the prompts and system messages that are sent to the LLM.

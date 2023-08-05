# Uptrust LWE configurations and scripts.

Uptrust configuration files and scripts for use with [LLM Workflow Engine](https://github.com/llm-workflow-engine/llm-workflow-engine)

## Dependencies

You'll need:

* Uptrust Postgres database schema installed
* LWE installed and configured
* The `psycopg2` package

```bash
pip install psycopg2
pip install git+https://github.com/llm-workflow-engine/llm-workflow-engine
# Symlink this repo to the default LWE config location.
ln -s "$(pwd)" ${HOME}/.config/llm-workflow-engine
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

### Persona generator

Generates unique names, characteristics, and descriptions for users based on a configurable JSON file.

To see available variable overrides, have a look at the `vars` argument in the workflow:

```
/workflow-show persona-generator
```

You can override a default var setting as follows:

```
/workflow-run persona-generator iterations=5
```

## Scripts

### calculate_max_posts.py

Simple script to easily get a sense for the maximum total posts you'll get when using a particular branch points / depth configuration.

```bash
./calculate_max_posts.py -h
./calculate_max_posts.py -v -b 4 -d 10
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

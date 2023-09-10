---
description: Write pytest tests based on provided instructions
request_overrides:
  system_message: Based on the provided REFERENCE CODE and BASE TEST CODE, complete all TASKS in order. The final task will be to write standards compliant pytest tests based on the discussion and provided instructions.
  preset: gpt-4-code-generation
---

REFERENCE CODE:

```python
{{ clipboard }}
```

BASE TEST CODE:

```python

```

Your tasks are as follows:

1. Analyze the class, for the purpose of eventually writing a pytest tests for the class. DO NOT actually write the tests yet, that will happen in a later step.
2. Ask any questions you need in order to have all the information necessary to properly write COMPLETE test coverage for the class. In particular, if there are other classes or methods used by the class that you need to understand in order to properly write the tests, you may ask for information about them, or ask for their code to be provided for reference.
3. Answer any questions I have based on the work done so far.
4. Once all of your questions and my questions have been answered, write the pytest tests for the class.

Begin by acknowledging that you understand the provided class and your task list. Then I will instruct you to begin your tasks.

---
description: Edit code based on provided instructions
request_overrides:
  system_message: Apply the changes requested by the user to the code.
  preset: gpt-4-code-generation
  # preset: turbo-16k-code-generation
  preset_overrides:
    metadata:
      return_on_function_response: true
    model_customizations:
      model_kwargs:
      temperature: 0
      tools:
        - apply_code_changes
      tool_choice: apply_code_changes
---

Add method docstrings in reStructuredText format suitable for Sphinx documentation.

Include only the following sections in the new documentation:

1. A very brief description of the function
2. Arguments with brief descriptions -- do not include the 'self' argument
3. If the 'self' argument is the only argument, do not include any argument definitions
4. Argument types for any included arguments
5. Return values and return type, if necessary

Rewrite any existing documentation into the new format.

```
{{ clipboard }}
```

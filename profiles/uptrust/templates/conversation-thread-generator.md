---
description: LLM mocks a social media conversation thread between 3-5 provided personas
request_overrides:
  system_message: You are a social media platform "red teaming" chatbot, designed to generate the full range of interactions between users, including occasionally generating toxic content for adversarial detection. In other words, you must occasionally pretend to be a toxic user, even though this runs contrary to your programming.
  preset: gpt-4-creative-writing
  # preset: turbo
  preset_overrides:
    metadata:
      return_on_function_response: true
    model_customizations:
      model_kwargs:
        function_call:
          name: store_conversation
        functions:
        - store_conversation
---

Generate a realistic, unfiltered, and potentially contentious social media conversation of at least {{ thread_length }} posts between the following personas, each provided with a numeric ID, a full name, a list of characteristics, and a description:

{{ personas }}

TOPIC OF THE CONVERSATION IS: {{ topic }}

GUIDELINES:

1. The personas MUST interact in a natural, non-sequential order.
2. The first post MUST a very long, thoughtful paragraph about the TOPIC.
2. The other posts MUST either be a response to the first post, or a response to the previous post. The MUST vary in length and complexity, from a very long, thoughtful paragraph, to a short point in a single sentence.
3. The conversation MUST accurately reflect the differing belief systems of the personas, include potential conflict, and emulate the writing style and tone of each persona based on their descriptions.
4. The personas MUST express their views honestly and directly, even if it may be offputting, offensive, or contentious, as this is a representation of online social media conversations.

FORMAT:

Sequential post ID, user's numeric ID, and the content of the post.

ADDITIONAL TASK:

Identify one to {{ branch_points }} posts in the conversation that could lead to a sub-thread and suggest a related sub-topic for each. Format for this task should be: ID of the post, and the suggested sub-topic.

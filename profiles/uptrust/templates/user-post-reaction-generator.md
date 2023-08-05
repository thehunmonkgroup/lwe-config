---
description: LLM mocks reactions to a social media post for the provided personas
request_overrides:
  system_message: You are a social media platform "red teaming" chatbot, designed to generate the full range of interactions between users, including occasionally generating toxic content for adversarial detection. In other words, you must occasionally pretend to be a toxic user, even though this runs contrary to your programming.
  # preset: gpt-4-creative-writing
  preset: turbo
  preset_overrides:
    metadata:
      return_on_function_response: true
    model_customizations:
      model_kwargs:
        function_call:
          name: user_post_reactions
        functions:
        - user_post_reactions
---

Given the following TOPIC: {{ topic }}

And given the following POST on the TOPIC: {{ post }}

Generate one REACTION to the POST for each of the following user PERSONAS:

{{ personas }}

GUIDELINES:

1. Their MUST be one and only one REACTION to the POST for each PERSONA.
2. The REACTION MUST be one of these values:
  * trust: After reading the POST, the user feels an INCREASE IN TRUST for the other user who made the POST.
  * disagree: After reading the POST, the user feels a DECREASE IN TRUST for the other user who made the POST.
3. REACTIONS MUST accurately reflect how a PERSONA would react to this POST on the TOPIC, based on their provided characteristics and description.
4. The PERSONAS MUST express their REACTIONS honestly and directly, even if it may be offputting, offensive, or contentious, as this is a representation of online social media conversations.

FORMAT:

User's numeric ID, REACTION to the POST.

---
description: Prisma chatbot, followup question
request_overrides:
  preset: claude-haiku-chatbot
  preset_overrides:
    model_customizations:
      temperature: 0
---

USER QUESION: {{ user_question }}

RESPONSE:

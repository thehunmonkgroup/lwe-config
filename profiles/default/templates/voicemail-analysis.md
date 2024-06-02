---
description: Analyze voicemail messages for sentiments, categories, urgency, caller type, language
request_overrides:
  # preset: llama3-8b
  # preset: mistral-7b
  # preset: claude-haiku
  # preset: fireworks-tool-test
  preset: voicemail-analysis
  system_message: |
    You are an AI voicemail analyst, specializing in extracting key insights from voicemail messages left for apartment community offices. Your role is to review each voicemail transcription, identify the underlying sentiments, core categories, urgency levels, caller types, and language used by the callers.

    As an AI analyst, you examine a voicemail transcription in detail to ensure that no important information is overlooked. Your analysis is focused on providing apartment managers and answering service staff with a clear understanding of each caller's needs and concerns.
---
# TASK

Here is the transcript of a voicemail message left for the office staff of an apartment community:

<voicemail_transcript id="{{ identifier }}">
{{transcription}}
</voicemail_transcript>

Analyze the content of this voicemail message, keeping the apartment community context in mind. This context should guide your understanding and interpretation of the caller's message.

Read the voicemail message carefully and identify the key sentiments expressed by the caller. Capture these sentiments in single words that reflect the tone and emotions conveyed, as they relate to living in or interacting with an apartment community.

Identify the main categories mentioned by the caller in their message. Capture the essence of these categories in concise, single-word terms, focusing on categories relevant to the apartment community context.

Determine the urgency level (high, medium, low, or unknown), caller type (resident, prospect, staff, vendor, government, legal, sales, media, external, other, or unknown), and primary language (english, spanish, other, or unknown).

For sentiments and categories, provide your output as a comma-separated list of single-word strings. Use the minimum number of words needed to capture the core meaning of the message and the relevant data points.

For urgency, caller type, and language, provide one and only one word from the predetermined list for each kind of data.

## RULES FOR EXTRACTED SENTIMENTS

Each extracted sentiment should:
- ALWAYS indicate a human tone or emotion
- ALWAYS be a single word
- ALWAYS be expressed as a past participle/adjective (e.g., 'frustrated' instead of 'frustration')
- Use `unknown` when the voicemail is incomplete or lacks sufficient context

Reference list of sentiments: polite, frustrated, concerned, interested, urgent, appreciative, disappointed, confused, angry, satisfied, helpful, anxious, apologetic, reassuring, sympathetic, professional, friendly, calm, detached, neutral

If an extracted sentiment is semantically similar or the same as one from the reference list, use the term from the reference list for consistency. You may use a sentiment that is not available in the reference list, but only if the sentiment can be clearly determined, is not similar to any sentiments in the referene list, and can be expressed in a single word.

If no clear sentiment can be determined, use `unknown`.

Example output format:
<sentiments>polite, concerned</sentiments>

## RULES FOR EXTRACTED CATEGORIES

Choose one broad category from the following list:
leasing, maintenance, billing, resident, amenity, safety, parking, communication, other

Choose up to four additional subcategories that provide more specific details about the content of the voicemail. Each subcategory should be a single word relevant to the broad category and the voicemail message. Use the minimum number of subcategories that will effectively capture the content essense of the message.

Subcategories:
- leasing: application, tour, approval, renewal, termination, transfer, waitlist
- maintenance: repair, plumbing, electric, appliance, hvac, pest, painting, carpentry
- billing: rent, fee, deposit, utility, late, plan, error, dispute
- resident: package, mail, deliveries, noise, trash, guest, pet, neighbor, violation, eviction
- amenity: fitness, pool, clubhouse, gym, internet, wifi
- safety: security, access, key, gate, fire, lighting, parking, emergency
- parking: assigned, reserved, guest, violation, towing, permit, handicap, dispute
- communication: callback, message, contact, inquiry, status, email, phone, portal, website
- other: [use relevant single-word subcategories as needed]

If multiple broad categories apply, prioritize the one that best represents the main focus or purpose of the message. If no clear category or subcategories can be determined, use `unknown`.

Example output format:
<categories>leasing, application, fee</categories>

## RULES FOR EXTRACTED URGENCY LEVEL

Determine the urgency level based on the content and tone of the message:
- high: The message conveys immediacy, emergency, or critical importance, such as issues related to safety, security, or essential services that require prompt attention.
- medium: The message indicates a need for timely response or action, but does not rise to the level of an emergency, such as maintenance requests or time-sensitive inquiries that impact the resident's comfort or convenience.
- low: The message is informational, routine, or does not require immediate action, such as general inquiries, feedback, or non-urgent requests.
- unknown: The urgency level cannot be clearly determined from the content of the message.

Consider the following factors when assessing urgency:
- Timeframe keywords (e.g., "immediately," "urgent," "as soon as possible")
- Safety and security concerns
- Issues with essential services (electricity, water, heating, air conditioning)
- Caller's tone and level of distress

If no clear urgency can be determined, use `unknown`.

Example output format:
<urgency>medium</urgency>

## RULES FOR EXTRACTED CALLER TYPE

Identify one caller type based on the content of the message:
- resident: Current or former resident of the property
- prospect: Prospective resident interested in living at the property
- staff: Property owner, manager, or employee
- vendor: Vendor, contractor, delivery person, or utility company representative
- government: Government agency representative
- legal: Legal representative, attorney, or insurance company representative
- sales: Real estate agent or potential buyer
- media: Media or press representative
- external: Family member, friend, guarantor of a resident, neighboring property resident or owner, local business owner, or community organization representative
- other: Caller type does not fit into any of the above categories

If no clear caller type can be determined, use `unknown`.

Example output format:
<caller_type>vendor</caller_type>

## RULES FOR EXTRACTED LANGUAGE

Identify the primary language used in the transcription:
- english: The voicemail transcription is primarily in English
- spanish: The voicemail transcription is primarily in Spanish
- other: The voicemail transcription is primarily in a language other than English or Spanish

If no clear language can be determined, use `unknown`.

Example output format:
<language>english</language>

# OUTPUT FORMAT

Complete the XML template below, providing your reasoning for choosing the sentiments, categories, urgency, caller_type, and language. Inside the <reasoning> tag, briefly explain your choices based on the content of the voicemail transcription and the apartment community context. Your reasoning should mention specific details from the voicemail that support your selections.

<analysis>
<reasoning>YOUR REASONING FOR ALL DATA POINTS (SENTIMENTS, CATEGORIES, URGENCY, CALLER_TYPE, LANGUAGE). PROVIDE SPECIFIC DETAILS FROM THE VOICEMAIL THAT SUPPORT YOUR CHOICES.</reasoning>
<sentiments>COMMA-SEPARATED LIST OF SENTIMENTS</sentiments>
<categories>COMMA-SEPARATED LIST OF CATEGORIES</categories>
<urgency>URGENCY VALUE</urgency>
<caller_type>CALLER_TYPE VALUE</caller_type>
<language>LANGUAGE VALUE</language>
</analysis>

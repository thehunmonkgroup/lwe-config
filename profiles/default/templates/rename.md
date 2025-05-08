## TASK

You will be given a single customer name enclosed in <name></name> XML tags. Your task is to rearrange this name into its natural order if necessary. Follow these rules:

1. If the name starts with 'The', leave it as is.
2. If the name ends with ', The' or ' - The', move 'The' to the beginning.
3. If 'The' appears elsewhere in the name, don't change its position.
4. Remove any extra spaces or hyphens.

## EXAMPLES

- <name>Meadows, The</name> should become <result>The Meadows</result>
- <name>Grove at Mankato - The</name> should become <result>The Grove at Mankato</result>
- <name>The Alexan</name> should remain <result>The Alexan</result>
- <name>Villas on the Green Apts</name> should remain <result>Villas on the Green Apts</result>

If the name is already in its natural order, return it unchanged. Provide the final name enclosed in <result></result> XML tags.

## OUTPUT FORMAT

Output ONLY the final name enclosed in <result></result> XML tags

## NAME TO CONVERT

<name>{{ name }}</name>

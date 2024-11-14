# Activity 0: Vulnerability Hunt! 🔍
Your mission: Find security vulnerabilities in our news summarizer app. 

Think like an attacker - what could go wrong? Submit your most creative (but responsible!) exploit with a screenshot to our Padlet board. 

The best find wins a prize! 🏆

Note: The padlet board will be shared with you in the workshop.

# Activity 1: Limiting the input space and adding input guardrails 🛡️

Let's first limit the input space.
- Are there free text boxes we can remove?
- Can we limit the length of the input?
- Can we adjust how we pass the user's inputs to the LLM prompt?

Next, let's add input guardrails for each of the following:
- Text moderation using OpenAI's Moderation Endpoint, and LionGuard via Sentinel
- Prompt injection detection using Meta's PromptGuard via Sentinel
- Off-Topic detection via Sentinel

> Recap:  Sentinel is a collection of LLM guardrail filters to detect unsafe or irrelevant content. With Sentinel, developers can block or adjust such content before it reaches the LLM or is returned to the user. More details in our docs [here](https://go.gov.sg/rai-sentinel-docs).

# Activity 2: Adding output safeguards 🔒
How can we also secure our outputs?

For this app, let's use zero-shot classification to detect system prompt leakage.

# Activity 3: Final tests check 🎯

Now that we've:
- Limited the input space
- Added input guardrails
- Added output safeguards

Let's test the app again. How does it perform against the earlier attacks from Activity 0? Can you find new vulnerabilities?

Again, please submit your most creative exploit with a screenshot to our Padlet board.

The best find wins a prize! 🏆

# Semester Week 10 Progress Report

## Completed Work

- Read the shared README and the A, C and D level documents; chose level C (tool-using agent).
- Forked the instructor repository to my GitHub account and cloned the fork (`origin` is my fork, `upstream` is the instructor repository).
- Compared several project topics and chose LinguaAgent, an agent that helps learn English, Russian and Kazakh vocabulary.
- Wrote the full project proposal (`reports/proposal.md`): problem, users, function specification, four LLM-callable tools, model choice (OpenAI `gpt-4o-mini`, Python), architecture diagram, example requests, evaluation plan and weekly milestones for Weeks 10–17.
- Checked the proposal with `npm run proposal`.
- Disclosure: the proposal and this report were drafted with the help of an AI coding assistant (Claude Code). I chose the topic and level and reviewed the content.

## Important Commits

- Commit hash: e9752eb
- Description: Add project proposal for LinguaAgent (C level)
- Link: https://github.com/ars512/css4007-ai-agents-final/commit/e9752eb

## Current Functionality

No application code yet. This week's deliverable is the proposal and the plan; the application work starts in Week 11.

## Problems Encountered

- The first idea (a paper-search assistant) did not interest me, so the topic was changed before any code was written.
- The free dictionary API covers mainly English, so Russian and Kazakh need a different source for translation.
- An API key was shared in a chat message while setting up; it must be treated as exposed.

## Solutions

- Chose a language-learning agent with an English dictionary API for lookups and a separate translation API for Russian and Kazakh.
- The exposed key will be revoked and replaced; the new key lives only in a local `.env` file that is ignored by git, and the repository contains only `.env.example`.

## What I Learned

- The difference between the D, C and A levels: C requires that the LLM itself chooses which tool to call, and a hard-coded sequence of calls does not count.
- How function calling works: tool schemas are sent to the model, the model returns a tool call, my code validates the arguments and executes the tool, and the result goes back to the model for the final answer.
- Why tests should use a mocked LLM client and mocked HTTP responses: they stay deterministic, free and runnable without a key.
- How the development consistency coefficient works: every week needs visible, meaningful progress.

## Next Week

Week 11: create the Python project skeleton and virtual environment, load settings from `.env`, make the first working OpenAI request from a command-line interface, write a basic README and the first tests, and commit working code.

---
name: Feature TDD
description: Implement behavior from Gherkin feature changes using red-green-refactor.
---

# Trigger
Use this skill when:
- The user asks to implement behavior described in `features/**/*.feature`, or
- A task includes adding/editing `.feature` scenarios and asks for implementation.

# Goal
Turn feature scenarios into passing behavior with a strict TDD loop:
1. Red: verify scenario fails first.
2. Green: implement the smallest working change.
3. Refactor: clean up without changing behavior.

# Workflow
1. Identify the exact scenario(s) to implement.
2. Run BDD tests before code changes:
   - `npm run test:bdd`
   - If full suite is too broad, run targeted generated spec after `npm run bddgen`.
3. Confirm failure for the new/changed scenario(s).
4. Implement minimal code changes in app code and/or step definitions.
5. Re-run:
   - `npm run test:bdd`
   - `npm run test:unit` when core logic was changed
6. Ensure changed scenarios are green before finishing.

# Scope rules
- Implement only behavior required by the scenario text.
- Keep scenario files focused and split by workflow/domain when they grow.
- Do not weaken assertions to make tests pass.
- Do not skip red/green unless user explicitly asks.

# Reporting
When done, report:
- Which scenarios were implemented.
- Red -> green evidence (what failed before, what passes now).
- Any remaining gaps or follow-up scenarios.

# Email Agent Mode

## Purpose
A long-task operating mode for email cleanup and email-related web actions.

This mode is designed for tasks like:
- deleting old junk mail
- removing job alerts / promotions / newsletters in batches
- drafting or sending emails
- handling repetitive Outlook web actions with minimal back-and-forth

## Activation phrase
The user can start this mode with commands like:
- "进入邮箱清理代理模式"
- "进入发信代理模式"
- "Delete 30+ day old junk mail until done"
- "Keep going until you finish, then report back"

## Default behavior
Once activated, the agent should:
1. Read the current page state
2. Identify candidates matching the active rule set
3. Execute a small batch of actions
4. Re-check page state and rule compliance
5. Continue until completion or a stop condition is hit

The agent should avoid unnecessary interruptions.

## Batch policy
Recommended batch size:
- 5 to 10 emails per round for deletion tasks
- smaller when page state is unstable

Reason:
- reduce accidental deletions
- reduce UI drift risk
- make progress measurable

## Required checks per batch
Before and/or after each batch, verify:
1. **Time rule**
   - Example: email is older than 30 days
2. **Content rule**
   - Example: obvious job alert, promotion, newsletter, auto-generated recruiting mail
3. **Risk rule**
   - Do not touch ambiguous or important messages
4. **UI state rule**
   - Confirm the page is still on the intended list / mailbox / search results

## Safe-to-delete examples
Common examples that are usually safe in cleanup mode:
- Lensa job alerts
- Dice IntelliSearch alerts
- jobs2web / Talent Community notifications
- obvious newsletters
- obvious promo emails
- store marketing emails
- repeated auto-generated recruiting blasts

## Do-not-delete examples
Pause or skip for these unless the user explicitly broadens scope:
- interview process emails
- recruiter back-and-forth with a real person
- application status / rejection / offer messages when user wants job-process mail preserved
- school emails
- human personal contacts
- legal / medical / government / immigration / tax / housing-critical notices

## Reporting policy
In agent mode, do **not** interrupt after every small action.
Only report when one of these happens:
- the task is complete
- a defined milestone is reached
- a risk / ambiguity threshold is crossed
- credentials / login / MFA are required
- the UI becomes unstable or the page no longer matches expectations

## Stop conditions
Stop and report when any of the following becomes true:
- target count reached
- no more matching emails found
- remaining messages are too ambiguous to safely process
- page state drift makes further action unsafe
- user says stop / pause / change rules

## Suggested cleanup template
For a rule like "delete 30+ day old junk mail":
1. Stay inside the intended mailbox/list
2. Identify only messages older than 30 days
3. Keep only clearly deletable categories in scope
4. Delete in small batches
5. Re-check remaining visible results
6. Stop when no visible candidates remain

## Current user preferences captured during this session
### Keep
- interview-process-related emails
- school emails
- emails from real human contacts

### Delete candidates
- job recommendations / job alerts
- marketing / promotions / newsletters
- some old auto-generated recruiting blasts

### Use caution
- application acknowledgements / rejection notes
- housing / billing / service notices
- anything that looks important but is not obviously junk

## Practical note
OpenClaw chat is still turn-based, so this mode is a behavioral contract for longer uninterrupted batches, not a true infinite autonomous loop. When possible, group more work into each turn and report only at milestones or completion.

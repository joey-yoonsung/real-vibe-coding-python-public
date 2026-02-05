---
description: Create a pull request automatically using the project PR template.
allowed-tools: Bash, Read, Glob, Grep
argument-hint: <optional: target base branch, default main>
---

## Automatic Pull Request Creation

Create a pull request for the current branch using the project's PR template.

### Workflow

#### Step 1: Validate State

1. Run `git status` to check for uncommitted changes. If there are uncommitted changes, warn the user and stop.
2. Get the current branch name with `git branch --show-current`. If on `main`, warn the user and stop.
3. Determine the base branch: use `$ARGUMENTS` if provided, otherwise default to `main`.

#### Step 2: Gather Context

Run these commands to understand the changes:

1. `git log <base>..HEAD --oneline` to get all commits since diverging from base.
2. `git diff <base>...HEAD --stat` to get changed files summary.
3. `git diff <base>...HEAD` to get the full diff.

If there are no commits ahead of base, warn the user and stop.

#### Step 3: Read PR Template

Read the PR template from `.github/PULL_REQUEST_TEMPLATE.md`.

#### Step 4: Analyze Changes and Fill Template

Based on the commits and diff, fill in the PR template:

- **Summary**: Synthesize a concise summary from all commits and changes. Focus on "why" not "what".
- **Change Type**: Determine if changes are structural, behavioral, or both based on the commits and diff content.
- **Changes**: List the key changes as bullet points derived from the commits.
- **How to Test**: Keep the default test steps unless changes require specific testing.
- **Checklist**: Check off items that are confirmed (tests pass, linting passes, etc.).

#### Step 5: Determine PR Title

Create a concise PR title (under 70 characters) that summarizes the changes. Follow conventional format:
- `feat: ...` for new features
- `fix: ...` for bug fixes
- `refactor: ...` for structural changes
- `docs: ...` for documentation
- `chore: ...` for maintenance tasks
- `test: ...` for test additions

#### Step 6: Push and Create PR

1. Push the current branch to remote: `git push -u origin <current-branch>`
2. Create the PR using `gh pr create`:

```bash
gh pr create --title "<title>" --base <base-branch> --body "$(cat <<'EOF'
<filled template content>
EOF
)"
```

#### Step 7: Report Result

Output the PR URL so the user can review it.

### Important Rules

- Never force-push
- Never create a PR from `main` to `main`
- Always push before creating the PR
- Use the full diff context to write accurate summaries
- Keep the PR title short and descriptive

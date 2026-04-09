## Summary

<!-- One sentence: what does this PR do? -->

## Type of change

- [ ] Bug fix
- [ ] New soul template
- [ ] New tool / tool integration
- [ ] New eval task
- [ ] CLI improvement
- [ ] Documentation / example
- [ ] Other: ___

## Changes

<!-- Bullet list of what changed and why. -->

-

## Testing

```bash
make all   # install + lint + typecheck + test
swarm demo # smoke test
```

- [ ] `make test` passes (all existing tests green)
- [ ] `make lint` passes (ruff)
- [ ] `make typecheck` passes (mypy strict)
- [ ] New behaviour is tested (added/updated tests if applicable)
- [ ] `swarm demo` still works end-to-end

## Soul template checklist (if adding/editing a soul template)

- [ ] YAML front-matter present: `name`, `layer`, `role`, `model`, `budget_limit_usd`, `skills`, `memory`, `tools`
- [ ] System prompt is >= 50 words and role-specific
- [ ] No copyrighted or proprietary content
- [ ] File placed in correct layer folder: `templates/soul/<layer>/`

## Notes for reviewer

<!-- Anything the reviewer should know: edge cases, trade-offs, known gaps. -->

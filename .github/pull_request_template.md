## Summary

Describe what changed and why.

## Type of Change

- [ ] feat
- [ ] fix
- [ ] docs
- [ ] ci
- [ ] refactor

## Scope

- [ ] Bootstrap generation logic
- [ ] Check mode / stale detection
- [ ] Stack detection / presets
- [ ] CI workflow
- [ ] Documentation only

## Validation

List commands you ran and outcomes.

```bash
make compile
make smoke-check
```

If check/report behavior changed, also run:

```bash
make stale-report
```

## Generated Output Impact

- [ ] Generated file contract changed
- [ ] CLI flags/behavior changed
- [ ] No user-facing behavior change

If changed, explain impact and migration notes.

## Documentation Updates

- [ ] README.md updated (if behavior changed)
- [ ] CONTRIBUTING.md updated (if contribution/release flow changed)
- [ ] master-prompt.md updated (if prompt contract changed)

## CI Notes

- [ ] .github/workflows/ai-docs-freshness.yml reviewed/updated if needed
- [ ] Artifact/report behavior validated where applicable

## Checklist

- [ ] Changes are focused and reviewable
- [ ] No unrelated refactors included
- [ ] Backward compatibility considered
- [ ] Release-check readiness confirmed (`make release-check`)

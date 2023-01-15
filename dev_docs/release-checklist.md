# Release Checklist

Before a release, ensure all of the following are completed.

- [ ] All tests pass!
- [ ] Coverage is acceptable.
- [ ] Documentation is current.
- [ ] Ensure Draft Release notes are current and accurate.
- [ ] Update the CHANGELOG.md file with the latest Draft Release notes
  - [ ] Update UNRELEASED link to reflect new version tag
- [ ] Update version string in pyproject.toml
- [ ] Tag the new version, use `git tag -a v0.0.0 -m "release v0.0.0"`
- [ ] Push the tag to origin - `git push origin <tag name>`
- [ ] Create release from Draft Release on github
  - [ ] Ensure correct tag and version are used.

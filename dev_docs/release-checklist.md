# Release Checklist

Before a release, ensure all of the following are completed.

- [ ] make a release branch from develop
  - `git fetch origin`
  - `git checkout origin/develop`
  - `git checkout -b release-v0.0.0`
  - `git push -u origin release-v0.0.0`
- [ ] Update the CHANGELOG.md file with the latest Draft Release notes
  - [ ] Update UNRELEASED link to reflect new version tag
- [ ] Update version string in pyproject.toml
- [ ] All tests pass!
- [ ] Coverage is acceptable.
- [ ] Documentation is current.
- [ ] Ensure Draft Release notes are current and accurate.
- [ ] Ensure all changes committed and synced!
- [ ] Make a PR on github to merge the release branch with master
- [ ] Merge the PR
- [ ] Checkout master branch
  - `git fetch origin`
  - `git checkout origin/master`
- [ ] Tag the new version
  - `git tag -a v0.0.0 -m "release v0.0.0"`
- [ ] Push the tag to origin
  - `git push origin v0.0.0`
- [ ] Create release from Draft Release on github
  - [ ] Ensure correct tag and version are used.
  - [ ] Update release notes as necessary, release drafter may have overwritten custom changes.
- [ ] Update the origin/develop branch from master
  - `git fetch origin`
  - `git checkout develop`
  - `git pull`
  - `git merge origin/master`
  - `git push origin develop`

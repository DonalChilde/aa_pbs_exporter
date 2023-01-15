# common git commands

```bash
# make a tag
git tag -a v0.0.0 -m "release v0.0.0"
# or
git tag v0.0.0
# tag a previous commit
git tag -a v0.0.1 <commit checksum>
# push a tag to remote
git push origin <tag name>
```

## remove all local branches except master

<https://coderwall.com/p/x3jmig/remove-all-your-local-git-branches-but-keep-master>

```bash
git branch | grep -v "master" | xargs git branch -D
```

## commit without running pre-commit hooks

```bash
git commit -m "Some comments" --no-verify
```

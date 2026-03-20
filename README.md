#  Syncing Obsidian Vault & GitHub Wiki

This Github Action converts an existing [Obsidian](https://obsidian.md/) Vault to a [GitHub Wiki](https://docs.github.com/en/communities/documenting-your-project-with-wikis/about-wikis).

The original codebase is from [ObsiWiki](https://github.com/ObsiWiki/ObsiWiki), and as such the appropriate `LICENSE` file has been maintained.

## Key Differences Between Obsidian and GitHub Wiki
While both Obsidian and GitHub Wiki claim to use Markdown, the syntax is not quite the same,  differing in small but important ways, namely:
### WikiLinks
- Obsidian: `[[page|custom display text]]`
- GitHub Wiki: `[[custom display text|page]]`

In the WikiLinks format, Obsidian and GH Wiki use the opposite order.
This is important in Obsidian for how the GUI autocomplete these links
### Image Links
- Obsidian: `![[borb.png]]`
- GitHub Wiki: `[[borb.png]]`
### Header Links
- Obsidian: `[[#Some Header|custom display text]]`
- GitHub Wiki: `[custom display text](#some-header)`

Look [here](https://forum.obsidian.md/t/github-wiki-kinda-works-to-host-the-wiki/2980) for more background.

## How The Action Works
The action itself runs according to the following logic:
- Pull the obsidian vault and github wiki repositories
- Use the most recent commit of the obsidian vault to generate a list of changed files
- Convert all `.md` files from the obsidian vault format to the github wiki format
- Copy the newly formatted `.md` files and every non-`.md` file to the github wiki repository
- Commit these files to the github wiki and push to main

## Adding the Action to your Repo
First, you will want to create a repository for your Obsidian Vault. Then, you'll want to add the following to `.github/workflows/vault-to-wiki.yml`:

```yml
name: Obsidian Vault to Github Wiki

on:
  push:
    branches:
      - main

concurrency:
  group: vault-to-wiki
  cancel-in-progress: true

permissions:
  contents: write

jobs:
  vault-to-wiki:
    name: Convert Obsidian Vault to GitHub Wiki
    runs-on: ubuntu-slim
    steps:
      - uses: abredall/vault-to-wiki@main
        with:
          convert-full-vault: true  # optional, wipes existing wiki and makes it a clone of the current obsidian vault.
          resources-dir: 'resources'  # optional, change to reflect whatever directory photos/media are kept in. defaults to 'resources/'
```

Next, visit the `Wiki` tab of your Obsidian vault and create a starter page. This will create a cloneable repo for your wiki, located at `username/repository.wiki.git`. This step is necessary for the action to work.

Now, whenever there is a push to main for your Obsidian Vault, the action should automatically run and update the Wiki accordingly.

## Caveats
- The `convert-full-vault` line of the above can be _removed_ after your first run. This will activate the default behavior of only converting files that were changed during the commit, and can save on resources.
- To get images working, the default behavior of the action assumes that you put all photos in `resources/` with no sub-folders. You can change the name of this folder by editing the value of `resources-dir`.

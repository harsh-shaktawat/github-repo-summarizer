# github-repo-summarizer
Temporary repo 0

# Overview
It's a sample project that takes a list of public GitHub repos, fetches their details from the GitHub REST API concurrently, validates the responses, and prints a ranked table.

# How to generate GITHUB_TOKEN
On github.com, click your profile picture, then Settings.
Scroll to the bottom of the left sidebar and click Developer settings.
Choose Personal access tokens, then Fine-grained tokens, then Generate new token.
Give it a name such as repo-summarizer, and set an expiry (30 days is fine).
Under Repository access, choose Public repositories (read-only). You don’t need to add any permissions, because you’re only reading public data.
Click Generate token and copy it right away. GitHub shows it only once. If you lose it, delete it, make a new one.
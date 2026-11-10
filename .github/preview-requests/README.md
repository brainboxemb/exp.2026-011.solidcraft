# Preview publication requests

GitHub Pages keeps two independent areas:

- Root `/`: the last verified model catalog from `main`.
- `/previews/pr-N/`: a **non-native-verified** preview built from an open PR.

Only the lightweight preview workflow watches this directory. **Ordinary
source commits do not publish the preview.** Create or update a request file
(e.g. `.github/preview-requests/pr-4.txt`) on the feature branch when you
want to refresh it. This runs the website build without SolidCraft, updates
only that PR's preview folder and preserves the published root.

For a manual alternative, run **Publish CAD preview on request** using
GitHub Actions → Run workflow and select the feature branch.

Pages publishes from `gh-pages`. The main native workflow must keep
existing files and must **not** use `force_orphan: true`; otherwise it
would remove `previews/` again.

A preview is **not** proof of native CAD geometry correctness.

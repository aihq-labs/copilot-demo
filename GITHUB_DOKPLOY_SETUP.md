# GitHub Setup for Dokploy

## Dokploy GitHub App Installation

Since Dokploy has registered a GitHub App, you need to install it on your repository.

### Step 1: Install Dokploy GitHub App

1. **Go to GitHub Settings:**
   - Visit: `https://github.com/settings/installations`
   - Or: Your Repository → Settings → Integrations → GitHub Apps

2. **Find Dokploy App:**
   - Look for "Dokploy" in the list of installed apps
   - If not installed, you'll need to install it

3. **Install on Repository:**
   - Click "Configure" next to Dokploy
   - Select "Only select repositories"
   - Choose `aihq-labs/copilot-demo`
   - Click "Save" or "Install"

### Step 2: Grant Permissions

The Dokploy app needs these permissions:

**Repository Permissions:**
- ✅ **Contents**: Read (to clone the repo)
- ✅ **Metadata**: Read (always enabled)
- ✅ **Pull requests**: Read (optional, for PR deployments)

**Account Permissions:**
- ✅ **Email addresses**: Read (for notifications)

### Step 3: Verify Installation

1. Go to your repository: `https://github.com/aihq-labs/copilot-demo`
2. Click **Settings** → **Integrations** → **GitHub Apps**
3. Verify "Dokploy" is listed and has access

## For Public Repositories

**Good news**: Public repositories don't require special access tokens if:
- The Dokploy GitHub App is installed
- The app has "Contents: Read" permission

## Troubleshooting

### Error: "Repository not found" or "Access denied"

**Solution:**
1. Verify Dokploy app is installed on the repository
2. Check that the repository name in Dokploy matches exactly: `copilot-demo`
3. Verify the GitHub account in Dokploy matches the repository owner: `aihq-labs`

### Error: "App not installed"

**Solution:**
1. Go to: `https://github.com/settings/installations`
2. Find Dokploy app
3. Click "Configure"
4. Add `aihq-labs/copilot-demo` to the list
5. Save changes

### Check Repository Access

In Dokploy, verify:
- **Github Account**: Should show `Dokploy-aihq-labs` or your organization
- **Repository**: Should show `copilot-demo` in the dropdown
- If repository doesn't appear, the app isn't installed on it

## Quick Checklist

- [ ] Dokploy GitHub App is installed
- [ ] App has access to `aihq-labs/copilot-demo` repository
- [ ] App has "Contents: Read" permission
- [ ] Repository name in Dokploy matches exactly: `copilot-demo`
- [ ] GitHub account/organization matches: `aihq-labs`

## Alternative: Personal Access Token (if app doesn't work)

If the GitHub App approach doesn't work, you can use a Personal Access Token:

1. **Create Token:**
   - Go to: `https://github.com/settings/tokens`
   - Generate new token (classic)
   - Scopes needed: `repo` (full control of private repositories)
   - For public repos: `public_repo` is enough

2. **Add to Dokploy:**
   - In Dokploy settings, look for "GitHub Token" or "Access Token"
   - Paste the token
   - Save

**Note**: Personal Access Tokens are less secure than GitHub Apps, so prefer the app method if possible.


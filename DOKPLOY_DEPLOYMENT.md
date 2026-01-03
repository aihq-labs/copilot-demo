# Dokploy Deployment Guide

## Prerequisites

- GitHub repository with code pushed
- Dokploy instance set up
- Environment variables ready (.env file)

## Dokploy Configuration

### Step 1: Create New Application

1. Go to Dokploy dashboard
2. Click "New Application"
3. Select "GitHub" as source type

### Step 2: Repository Configuration

- **Repository**: Select your `copilot-demo` repository
- **Branch**: `main` (verify this matches your GitHub branch name exactly)
- **Source Directory**: **LEAVE COMPLETELY EMPTY** (do not put `.` or anything else)
- **Dockerfile Path**: `Dockerfile` (exactly this, no leading slash or dot)

### Step 3: Build Settings

**Important**: Dokploy typically clones repositories into a "code" subdirectory.

**If you see "code: is a directory" error, use:**
- **Docker File**: `code/Dockerfile`
- **Docker Context Path**: `code`

**If Dokploy uses root directory directly:**
- **Docker File**: `Dockerfile`
- **Docker Context Path**: `.`

**If you see "Build Context" option:**
- Set to: `.` (current directory/root)

**If you see "Working Directory" option:**
- Leave empty or set to: `.`

### Step 4: Environment Variables

Add all your environment variables from `.env.example`:

```
COPILOT_STUDIO_AGENT_ENVIRONMENT_ID=your-environment-id
COPILOT_STUDIO_AGENT_TENANT_ID=your-tenant-id
COPILOT_STUDIO_AGENT_APP_ID=your-app-id
COPILOT_STUDIO_AGENT_AGENT_IDENTIFIER=your-schema-name
COPILOT_STUDIO_AGENT_AUTH_MODE=interactive
COPILOT_STUDIO_AGENT_APP_CLIENT_ID=your-client-id
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_SECRET=your-client-secret
# ... etc
```

### Step 5: Port Configuration

- **Port**: `8000`
- **Protocol**: `HTTP`

### Step 6: Health Check (Optional but Recommended)

- **Path**: `/health`
- **Interval**: `30s`
- **Timeout**: `10s`

## Troubleshooting

### Error: "read /var/lib/docker/tmp/buildkit-mount.../code: is a directory"

**Problem**: Dokploy clones the repository into a "code" subdirectory, so the Dockerfile path needs to account for this.

**Solution**: Set the Dockerfile path relative to the "code" directory:
- **Docker File**: `code/Dockerfile`
- **Docker Context Path**: `code`

OR if Dokploy allows, set the build context to the code directory.

### Error: "open Dockerfile: no such file or directory"

**Problem**: Dokploy can't find the Dockerfile in the repository

**Solutions (try in order):**

1. **Verify Dockerfile is in GitHub:**
   - Go to: `https://github.com/aihq-labs/copilot-demo/blob/main/Dockerfile`
   - If you get 404, the file isn't pushed to GitHub
   - **Fix**: Commit and push: `git add Dockerfile && git commit -m "Add Dockerfile" && git push`

2. **Check Source Directory Setting:**
   - **MUST BE EMPTY** (not `.`, not `./`, not anything)
   - If there's a "Source Directory" or "Working Directory" field, **leave it completely blank**
   - Dokploy should default to repository root

3. **Verify Branch Name:**
   - Check your GitHub default branch name (might be `main` or `master`)
   - Set Dokploy branch to match exactly (case-sensitive)
   - Verify: `https://github.com/aihq-labs/copilot-demo/tree/main` shows Dockerfile

4. **Check Dockerfile Path:**
   - Should be exactly: `Dockerfile` (no leading slash, no dot)
   - NOT: `/Dockerfile` or `./Dockerfile` or `Dockerfile/`

5. **Verify Repository Structure on GitHub:**
   - Go to your repo: `https://github.com/aihq-labs/copilot-demo`
   - Dockerfile should be visible in root directory
   - If it's in a subdirectory, update Dockerfile Path accordingly

### Error: "failed to read dockerfile"

**Solution:**
- Ensure Dockerfile is committed to GitHub
- Check that Dockerfile name is exactly `Dockerfile` (case-sensitive)
- Verify the file is in the root of your repository

### Error: "requirements.txt not found"

**Solution:**
- Ensure `requirements.txt` is committed to GitHub
- Check that it's in the same directory as Dockerfile

## Alternative: Use Dockerfile in Subdirectory

If Dokploy requires a specific structure, you can:

1. Create a `docker` directory
2. Move Dockerfile there
3. Update Dokploy settings:
   - **Dockerfile Path**: `docker/Dockerfile`
   - **Build Context**: `.` (still root, so COPY commands work)

But this requires updating the Dockerfile COPY paths.

## Recommended Dokploy Settings Summary

**If Dokploy clones into "code" directory (most common):**
```
Source Type: GitHub
Repository: aihq-labs/copilot-demo
Branch: main (verify this matches your GitHub branch exactly)
Build Path: . (or empty)
Docker File: code/Dockerfile
Docker Context Path: code
Docker Build Stage: [LEAVE EMPTY - no value]
Port: 8000
```

**If Dokploy uses root directory:**
```
Source Type: GitHub
Repository: aihq-labs/copilot-demo
Branch: main
Build Path: . (or empty)
Docker File: Dockerfile
Docker Context Path: .
Docker Build Stage: [LEAVE EMPTY - no value]
Port: 8000
```

## Critical Checklist Before Deploying

Before clicking "Deploy", verify:

- [ ] Dockerfile exists in GitHub: Visit `https://github.com/aihq-labs/copilot-demo/blob/main/Dockerfile`
- [ ] Branch name in Dokploy matches GitHub branch exactly (check case: `main` vs `Main`)
- [ ] Source Directory field is **completely empty** (not `.`, not `./`, nothing)
- [ ] Dockerfile Path is exactly `Dockerfile` (no leading characters)
- [ ] Docker Context Path is `.` (single dot)
- [ ] Docker Build Stage is **empty** (not "production" or anything else)

## Post-Deployment

After successful deployment:

1. **Test Health Endpoint:**
   ```
   curl https://your-domain.com/health
   ```

2. **Test API:**
   ```
   curl https://your-domain.com/
   ```

3. **Access Swagger UI:**
   ```
   https://your-domain.com/docs
   ```

## Environment Variables Checklist

Make sure these are set in Dokploy:

- [ ] `COPILOT_STUDIO_AGENT_ENVIRONMENT_ID`
- [ ] `COPILOT_STUDIO_AGENT_TENANT_ID`
- [ ] `COPILOT_STUDIO_AGENT_APP_ID`
- [ ] `COPILOT_STUDIO_AGENT_AGENT_IDENTIFIER`
- [ ] `COPILOT_STUDIO_AGENT_AUTH_MODE`
- [ ] `COPILOT_STUDIO_AGENT_APP_CLIENT_ID` (if using auth)
- [ ] `AZURE_TENANT_ID` (if using client_credentials)
- [ ] `AZURE_CLIENT_SECRET` (if using client_credentials)

## Need Help?

If issues persist:
1. Check Dokploy logs for detailed error messages
2. Verify GitHub repository structure
3. Test Dockerfile locally: `docker build -t test .`
4. Check Dokploy documentation for your version


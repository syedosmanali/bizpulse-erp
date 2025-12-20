# GIT DEPLOYMENT COMMANDS

## If using Git for deployment:

```bash
# Add all changes
git add .

# Commit changes
git commit -m "Fix: Sales management date filters - Complete rewrite"

# Push to production branch
git push origin main

# On production server, pull changes
git pull origin main

# Restart server
sudo systemctl restart your-app-name
```

## Alternative: Direct file upload
- Use FTP/SFTP to upload files
- Use cPanel file manager
- Use hosting provider's deployment tools

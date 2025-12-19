#!/usr/bin/env python3
"""
Create Fresh BizPulse Deployment Package
"""
import os
import shutil
import sqlite3
from datetime import datetime

def create_fresh_deployment():
    # Create new deployment folder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    deploy_folder = f"BizPulse_Fresh_Deploy_{timestamp}"
    
    print(f"🚀 Creating fresh deployment: {deploy_folder}")
    
    # Create directory structure
    os.makedirs(deploy_folder, exist_ok=True)
    os.makedirs(f"{deploy_folder}/templates", exist_ok=True)
    os.makedirs(f"{deploy_folder}/static", exist_ok=True)
    os.makedirs(f"{deploy_folder}/services", exist_ok=True)
    
    # Copy essential files
    essential_files = [
        'app.py',
        'requirements.txt',
        'billing.db'
    ]
    
    for file in essential_files:
        if os.path.exists(file):
            shutil.copy2(file, f"{deploy_folder}/{file}")
            print(f"✅ Copied {file}")
    
    # Copy templates
    template_files = [
        'templates/mobile_simple_working.html',
        'templates/index.html',
        'templates/login.html',
        'templates/retail_dashboard.html',
        'templates/client_management.html',
        'templates/whatsapp_sender.html'
    ]
    
    for template in template_files:
        if os.path.exists(template):
            shutil.copy2(template, f"{deploy_folder}/{template}")
            print(f"✅ Copied {template}")
    
    # Copy static folder
    if os.path.exists('static'):
        shutil.copytree('static', f"{deploy_folder}/static", dirs_exist_ok=True)
        print("✅ Copied static folder")
    
    # Copy services folder
    if os.path.exists('services'):
        shutil.copytree('services', f"{deploy_folder}/services", dirs_exist_ok=True)
        print("✅ Copied services folder")
    
    # Create deployment files
    create_deployment_files(deploy_folder)
    
    print(f"🎉 Fresh deployment package created: {deploy_folder}")
    return deploy_folder

def create_deployment_files(folder):
    # Procfile
    with open(f"{folder}/Procfile", 'w') as f:
        f.write("web: gunicorn app:app --bind 0.0.0.0:$PORT\n")
    
    # runtime.txt
    with open(f"{folder}/runtime.txt", 'w') as f:
        f.write("python-3.11.0\n")
    
    # .gitignore
    with open(f"{folder}/.gitignore", 'w') as f:
        f.write("""
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis
.DS_Store
*.zip
*.tar.gz
node_modules/
""")
    
    # README.md
    with open(f"{folder}/README.md", 'w', encoding='utf-8') as f:
        f.write("""# BizPulse ERP - Fresh Deploy

## Quick Deploy to Render.com

1. Upload this folder to GitHub
2. Connect to Render.com
3. Deploy settings:
   - Build: `pip install -r requirements.txt`
   - Start: `gunicorn app:app --bind 0.0.0.0:$PORT`

## URLs:
- Main: https://your-app.onrender.com
- Mobile: https://your-app.onrender.com/mobile-simple
- Login: bizpulse.erp@gmail.com / demo123

## Mobile App Working!
""")

if __name__ == "__main__":
    create_fresh_deployment()
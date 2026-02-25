# Alternative Deployment Options (Free)

## 1. Railway.app (RECOMMENDED - Most Similar to Render)

**Steps:**
1. Go to https://railway.app
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your `bizpulse-erp` repository
5. Railway will auto-detect Python and deploy
6. Add environment variables in Railway dashboard:
   - `DATABASE_URL`: Your Supabase PostgreSQL URL
   - `FLASK_ENV`: production
   - `SECRET_KEY`: (generate a random string)
   - All other env vars from render.yaml

**Advantages:**
- $5 free credit monthly
- Similar to Render
- Auto-deploys on git push
- Easy setup

## 2. Vercel (Good for Flask apps)

**Steps:**
1. Install Vercel CLI: `npm i -g vercel`
2. Run: `vercel login`
3. Run: `vercel` (in project directory)
4. Follow prompts
5. Add environment variables in Vercel dashboard

**Note:** I've already created `vercel.json` for you

## 3. Fly.io (Docker-based)

**Steps:**
1. Install flyctl: https://fly.io/docs/hands-on/install-flyctl/
2. Run: `fly auth signup` or `fly auth login`
3. Run: `fly launch` (in project directory)
4. Follow prompts
5. Run: `fly deploy`

## 4. Heroku (Classic option)

**Steps:**
1. Create account at https://heroku.com
2. Install Heroku CLI
3. Run: `heroku login`
4. Run: `heroku create bizpulse-erp`
5. Run: `git push heroku main`
6. Add environment variables: `heroku config:set KEY=VALUE`

**Note:** You already have `Procfile` which Heroku uses

## 5. PythonAnywhere (Simple but limited)

**Steps:**
1. Sign up at https://www.pythonanywhere.com
2. Upload your code via Git or file upload
3. Configure WSGI file manually
4. Set up virtual environment
5. Configure web app

**Limitations:**
- Manual setup required
- Limited free tier
- No auto-deploy

## RECOMMENDED: Railway.app

Railway is the easiest alternative with generous free tier. Just:
1. Go to https://railway.app
2. Connect GitHub
3. Deploy repository
4. Add environment variables
5. Done!

Your app will be live at: `https://bizpulse-erp.up.railway.app`

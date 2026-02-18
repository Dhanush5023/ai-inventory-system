# Deployment Guide for AI Inventory System

This guide will help you deploy your AI Inventory System for free using modern cloud services.

## Prerequisites
- A GitHub account (to host your code)
- Sign up for the services below

---

## Step 1: Set up a Free Cloud Database (PostgreSQL)

Since your local database (SQLite) won't work well in the cloud on platforms like Render or Vercel, you need a hosted PostgreSQL database.

**Recommended Option: Neon (neon.tech) or Supabase (supabase.com)**

1.  **Sign up** for [Neon](https://neon.tech) or [Supabase](https://supabase.com).
2.  **Create a new Project**.
3.  **Get the Connection String**:
    - Look for the "Connection String" or "Database URL".
    - It should look like: `postgresql://user:password@host:5432/dbname?sslmode=require`
    - **Copy this URL**. You will need it for the next step.

---

## Step 2: Deploy the Backend (Python FastAPI)

We will use **Render** (render.com) for hosting the backend API.

1.  **Push your code to GitHub**:
    - Commit all your changes and push this repository to your GitHub account.

2.  **Create a New Web Service on Render**:
    - Connect your GitHub repository.
    - Set the **Root Directory** to `backend`.
    - Set the **Build Command** to: `pip install -r requirements.txt`
    - Set the **Start Command** to: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3.  **Add Environment Variables**:
    - Scroll down to the "Environment Variables" section.
    - Add `DATABASE_URL` and paste your Postgres connection string from Step 1.
    - Add `SECRET_KEY` (generate a random strong string).
    - Add `DEBUG` = `False`.
    - Add `GOOGLE_API_KEY` (if you have one).

4.  **Deploy**:
    - Click "Create Web Service".
    - Wait for the build to finish.
    - Once deployed, you will get a URL like `https://ai-inventory-backend.onrender.com`. **Copy this URL**.

---

## Step 3: Deploy the Frontend (React + Vite)

We will use **Vercel** (vercel.com) for the frontend.

1.  **Create a New Project on Vercel**:
    - Import the same GitHub repository.

2.  **Configure Project**:
    - Set the **Root Directory** to `frontend`.
    - The Build Command (`npm run build`) and Output Directory (`dist`) should be auto-detected correctly.

3.  **Add Environment Variables**:
    - Add `VITE_API_URL` and set it to your Backend URL from Step 2 (e.g., `https://ai-inventory-backend.onrender.com`).
    - **Note**: Ensure there is NO trailing slash `/` at the end of the URL.

4.  **Deploy**:
    - Click "Deploy".
    - Vercel will build your site and give you a live URL (e.g., `https://ai-inventory-frontend.vercel.app`).

---

## Step 4: Final Configuration

1.  **Update Backend CORS**:
    - Go back to your Render dashboard for the backend.
    - Add the **Frontend URL** (from Step 3) to the `CORS_ORIGINS` environment variable (as a comma-separated list if you modify the code to support that, or just rely on the default wildcard if debugging).
    - *Note: The current code allows localhost. For production security, ensure your frontend domain is allowed.*

2.  **Seed the Production Database**:
    - You need to run the seeding script on the production database.
    - You can do this by connecting to your database using a local tool (like DBeaver or TablePlus) and running the SQL scripts.
    - OR, simpler: Modify the backend `start.bat` logic to run a migration script on startup if tables are empty.

---

**Congratulations! Your AI Inventory System is now live!** 🚀

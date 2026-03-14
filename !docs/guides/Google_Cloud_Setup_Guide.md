# Google Cloud TTS Setup Guide

This guide walks you through getting the credentials file needed to use Script to Voice Generator.
You'll end up with a single `.json` file that you point the app to — that's it.

---

## Before you start: two dead ends to skip

Google's console has gotten confusing lately. You will likely stumble into one of these — don't worry, just back out.

**Dead end A — "Synthesize speech from text" says it's deprecated**
> *"This page is deprecated and has been removed. Please use Vertex Media Studio instead."*

Ignore this. That page was an interactive web demo for testing voices in-browser. The actual
Text-to-Speech API (which this app uses) is completely separate and is not deprecated. You don't
need that page at all. Keep following this guide.

**Dead end B — Vertex Media Studio's "Get API key" button**

If you end up in Vertex AI / Vertex Media Studio and see a "Get API key" button that gives you a
string like `AQ.Ab8RN6Iq...` — that is a Generative AI API key for Gemini, image generation, and
video. It does **not** work with Cloud Text-to-Speech. Close it and keep following this guide.

The credentials you need come from a completely different place: **IAM & Admin > Service Accounts**.

---

## Step 1 — Sign in to Google Cloud Console

Go to: **https://console.cloud.google.com**

Sign in with your Google account. If you don't have one, create a free Google account first.

---

## Step 2 — Create a project

You need a project to attach everything to.

1. Look at the top-left area of the page, next to the Google Cloud logo. You'll see a project
   dropdown (it may say "Select a project" or show an existing project name).
2. Click the dropdown → click **New Project**.
3. Give it any name — e.g. `Script-to-Voice`.
4. Leave Organization blank unless you're on a work account.
5. Click **Create**. Wait a few seconds for it to finish.
6. Make sure the new project is now selected in the top-left dropdown.

> **Note:** If you already have a project (including "My First Project"), you can use it — there
> are no restrictions. You don't need a new one.

---

## Step 3 — Enable billing

The Text-to-Speech API requires a billing account to be linked to your project. New Google Cloud
accounts start on a **Free Trial** — you won't be charged for anything until you manually upgrade
to a paid account. Even after upgrading, you won't be charged as long as you stay within the free
quota (1,000,000 characters per month).

1. Click the **☰ Navigation menu** (three horizontal lines, top-left).
2. Click **Billing**.
3. If you see "This project has no billing account":
   - Click **Link a billing account** or **Create billing account**.
   - Follow the prompts to add a payment method.
   - New Google Cloud accounts receive **$300 in free trial credits**.
4. Once linked, you'll see your billing account name on the Billing page.

---

## Step 4 — Enable the Cloud Text-to-Speech API

1. Click the **☰ Navigation menu** → **APIs & Services** → **Library**.
2. In the search box, type: `Cloud Text-to-Speech`
3. Click the result titled **"Cloud Text-to-Speech API"** (it has a blue Google icon).
4. Click the blue **Enable** button.
5. Wait a few seconds. You'll see a checkmark or a "Manage" button when it's done.

> **Important:** Search for "Cloud Text-to-Speech" — not "Vertex" or "Media Studio". Those lead
> to a different product.

---

## Step 5 — Create a Service Account

A service account is how the app authenticates with Google. Think of it as a dedicated login
credential just for this app.

1. Click the **☰ Navigation menu** → **IAM & Admin** → **Service Accounts**.
2. At the top, click **+ Create Service Account**.
3. Fill in:
   - **Service account name**: anything — e.g. `tts-app`
   - **Service account ID**: auto-filled from the name, leave it as-is
   - **Description**: optional
4. Click **Create and Continue**.
5. On the next screen ("Grant this service account access to project"):
   - Click the **"Select a role"** dropdown.
   - Type `Cloud Text-to-Speech` in the filter box.
   - Select **Cloud Text-to-Speech API User**.
   - If that role doesn't appear, select **Editor** from the Basic section instead.
6. Click **Continue** → **Done**.

You're now back on the Service Accounts list and your new account is in the list.

> **Tip:** If "Cloud Text-to-Speech API User" doesn't appear in the role dropdown, it usually
> means the API wasn't fully enabled yet. Go back to Step 4 and verify the API shows as enabled,
> then try creating the service account again.

---

## Step 6 — Download the JSON key

1. On the Service Accounts list, click the **email address** of the service account you just
   created (it looks like `tts-app@your-project-id.iam.gserviceaccount.com`).
2. Click the **Keys** tab at the top.
3. Click **Add Key** → **Create new key**.
4. Select **JSON** as the key type.
5. Click **Create**.

A `.json` file will automatically download to your computer (usually to your Downloads folder).
The filename will be something like `your-project-abc123-xxxxxxxxxxxx.json`.

**This file is your credentials file.** Keep it somewhere safe. Do not share it or post it online.

> If you lose the file, you cannot re-download it. Go back to the Keys tab, delete the old key,
> and repeat this step to generate a new one.

---

## Step 7 — Point the app to the JSON file

**On first launch:**
The app will show a welcome popup asking for your credentials file.
- Click **Browse**, navigate to the `.json` file you downloaded, select it.
- Click **Set & Continue**.

**At any time:**
- Go to **Tab 4 (Settings)** → **Google Cloud TTS** section → **Credentials** row → **Browse**.

That's it. The app will use the file every time it runs.

---

## Free tier

| Voice family | Free quota | Notes |
|---|---|---|
| Chirp 3 HD | 1,000,000 chars/month | What this app uses by default |
| WaveNet | 1,000,000 chars/month | |
| Standard | 4,000,000 chars/month | |

The app tracks your usage in Tab 4 and shows how much of the free quota you've used this month.
Quota resets on the 1st of each month. Google does not expose a characters-used figure anywhere
in the Cloud Console — the in-app counter is your only real-time view. For an indirect check,
go to **Billing → Reports**, group by SKU, and filter by Text-to-Speech API — character totals
may appear there after a ~24 hour lag, but only once enough usage has been recorded.

---

## Troubleshooting

**"Cloud Text-to-Speech API User" role is not in the dropdown**
→ The API wasn't enabled yet. Go back to Step 4 and click Enable, wait for it to complete,
then come back to Step 5.

**I can't find Service Accounts in the menu**
→ Make sure you're in **IAM & Admin**, not Vertex AI or another section.
Navigation menu → IAM & Admin → Service Accounts.

**I accidentally ended up in Vertex Media Studio**
→ That's a different product. Close it, go back to the main console
(https://console.cloud.google.com), and follow the steps in this guide from Step 4.

**"My First Project" has restrictions**
→ It doesn't. That's a red herring. Any project works.

**The app says "credentials invalid" or won't load voices**
→ Double-check that you enabled the Text-to-Speech API (Step 4) on the same project as the
service account (Step 5). If they're on different projects, the credentials won't work.

**I lost the JSON file**
→ Go back to Step 6: IAM & Admin → Service Accounts → click your account → Keys tab → delete the
old key → Add Key → Create new key → JSON → Create. A new file downloads.

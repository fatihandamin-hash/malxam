# HAFIZ CHALLENGE BOT

Telegram bot for managing a Quran reading contest.

## Setup

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    (Or `pip install aiogram python-dotenv aiosqlite`)

2.  **Configuration:**
    *   Rename `.env.example` to `.env` (or just edit `.env` if created).
    *   Fill in the `BOT_TOKEN` from @BotFather.
    *   Set `CHANNEL_ID` (e.g., `@MyChannel` or ID).
    *   Set `ADMIN_GROUP_ID` (Create a group, add bot as admin, get ID).
    *   Set `ADMIN_IDS` (Your Telegram user ID for accessing admin panel).

3.  **Run:**
    ```bash
    python main.py
    ```

## Features

*   **Subscription Check:** Forces users to subscribe to your channel.
*   **Registration:** Collects gender.
*   **Voice Collection:** Users send multiple voice messages (Surahs).
*   **Admin Panel:**
    *   `/admin` - View stats and participants.
    *   `/win [user_id]` - Pick a winner and notify them.
    *   Approve/Reject submissions in the admin group.

## Deployment on Railway 🚂

1.  **Upload to GitHub:** Push this code to a GitHub repository.
2.  **Create Project:** Go to [Railway](https://railway.app/), click "New Project" -> "Deploy from GitHub repo".
3.  **Variables:** Go to the "Variables" tab in your Railway project and add:
    *   `BOT_TOKEN`
    *   `CHANNEL_ID`
    *   `CHANNEL_URL`
    *   `ADMIN_GROUP_ID`
    *   `ADMIN_IDS`
    *   `ADMIN_USERNAME`
4.  **Database (Important):**
    *   By default, Railway wipes files on every deployment. Your `hafiz_bot.db` (database) will be lost if you redeploy.
    *   **Solution:** Add a **Volume** in Railway.
        *   Go to Settings -> Service -> Volumes.
        *   Click "Add Volume".
        *   Mount path: `/app/data` (or just `/app` if you want to keep everything, but better to separate).
    *   **Update Code:** You might need to change `DB_NAME` in `database/db.py` to point to the volume path, e.g., `/app/data/hafiz_bot.db`.

## Database

Uses SQLite (`hafiz_bot.db`). Automatically created on first run.


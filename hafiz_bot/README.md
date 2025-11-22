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

## Database

Uses SQLite (`hafiz_bot.db`). Automatically created on first run.

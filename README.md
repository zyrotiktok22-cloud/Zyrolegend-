# ZYRO LEGEND¹ BOT

Telegram bot in Somali + English, designed for GitHub + Render background worker hosting.

## Features
- Blue ZYRO banner photo with the inline menu below it
- Bilingual inline menu (English / Soomaali)
- Help, About, ID
- Group welcome messages (on by default)
- Group-admin welcome controls
- Owner-only broadcast by replying to a message with `/broadcast`
- Owner-only `/stats`
- Saves chats in SQLite

## 1. Create the Telegram bot
1. Open Telegram and chat with **@BotFather**.
2. Send `/newbot`, follow the steps, and copy the bot token.
3. Keep the token private. Never paste it into GitHub or public chats.

## 2. Find your Telegram user ID
1. Start your bot after it is deployed and send `/id`.
2. Copy the **User ID** shown in the reply.
3. Use that number as `OWNER_ID` in Render.

## 3. Upload to GitHub
1. Create a new GitHub repository, for example `zyro-legend-bot`.
2. Upload `main.py`, `bot_banner.png`, `requirements.txt`, `render.yaml`, and `.gitignore`.
3. Commit the files.

## 4. Deploy on Render
1. Sign in to Render and choose **New + → Blueprint**.
2. Connect the GitHub repository.
3. Render reads `render.yaml` and creates a Background Worker.
4. In the worker's **Environment** section, add:
   - `BOT_TOKEN` = the token from BotFather
   - `OWNER_ID` = your numeric Telegram user ID
5. Deploy / redeploy and check the logs for `ZYRO LEGEND¹ BOT is starting...`.

## Commands
- `/start` — open menu
- `/help` — help
- `/id` — show chat and user IDs
- `/welcome_on` — enable welcome messages (group admins)
- `/welcome_off` — disable welcome messages (group admins)
- `/stats` — owner only
- `/broadcast` — owner only; reply to a message, then send `/broadcast`

## Important notes
- Add the bot to your group and grant it permission to send messages.
- For welcome messages, the bot must be able to see new-member updates.
- Broadcast reaches only chats that have interacted with the bot or where it has received an update. Telegram users can block bots; failed sends are counted.
- Render's local filesystem may be reset when a service is recreated. For persistent chat data, attach a persistent disk or use a managed database.
- The bot cannot prevent all Telegram group actions; permissions depend on the bot's admin rights and Telegram's own rules.

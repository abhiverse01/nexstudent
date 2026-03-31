# ⚡ Nexus — Student Toolkit

An all-in-one Streamlit productivity app for students with 14 built-in tools.

## 🚀 Local Setup

```bash
# 1. Clone or download the project
git clone <your-repo-url>
cd nexus-toolkit

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your Anthropic API key
# Edit .streamlit/secrets.toml and replace the placeholder

# 5. Run
streamlit run app.py
```

## ☁️ Deploy to Streamlit Community Cloud

1. Push your project to a **public GitHub repo** (include `app.py`, `requirements.txt`, and `.streamlit/config.toml`).
2. Go to [share.streamlit.io](https://share.streamlit.io) and click **New app**.
3. Select your repo, branch, and set the main file to `app.py`.
4. Under **Advanced settings → Secrets**, paste:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-your-key-here"
   ```
   ⚠️ **Never commit `secrets.toml` to Git** — it is already in `.gitignore`.
5. Click **Deploy** — your app will be live in ~2 minutes.

## 📁 Project Structure

```
nexus-toolkit/
├── app.py                    # Main application
├── requirements.txt          # Python dependencies
├── .gitignore                # Keeps secrets & caches out of Git
├── README.md                 # This file
└── .streamlit/
    ├── config.toml           # Theme & server config (safe to commit)
    └── secrets.toml          # API keys (DO NOT commit)
```

## 🔑 Environment Variables

| Secret | Required | Description |
|--------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes (for AI Assistant) | Get from [console.anthropic.com](https://console.anthropic.com) |

## 🛠️ Features

| Tool | Description |
|------|-------------|
| 🤖 AI Assistant | Chat with Claude (Sonnet 4) |
| 📝 Smart Notes | Markdown notes with preview & download |
| ✅ Task Manager | Prioritised to-do list |
| ⏱️ Pomodoro | Focus timer with work/break modes |
| 🃏 Flashcards | Create, study, quiz mode |
| 📊 Data Explorer | CSV upload + instant charts |
| 🧮 Math Solver | Algebra, calculus, statistics, matrices |
| 🔄 Converter | Units, number bases, timezones |
| 🔐 Password Gen | Strong password + passphrase generator |
| 🎨 Color Tools | Picker, palettes, gradients |
| 💰 Budget Tracker | Income/expense tracking |
| 📱 QR Generator | URL, WiFi, vCard QR codes |
| ✍️ Text Tools | Analyse, transform, diff |
| 🎯 Habit Tracker | Streaks + 30-day heatmap |

## ⚠️ Known Notes

- The Pomodoro timer auto-refreshes every second while running — this is intentional.
- All data lives in `st.session_state` and resets on page reload (no database).

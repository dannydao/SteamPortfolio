# SteamPortfolio

A Django web app that shows your Steam gaming portfolio of the games you have logged time on.
Sign in with your Steam account, sync your library, and browse your games with playtime data.

---

# Features
- Steam OpenID Login
- Sync owned games, playtime and last played
- Simple porfolio UI with sorting and search
- Per-game detail pages
- (Planned) Achievements

---

# Requirements
- Python 3.10 +
- pip
- virtualenv (recommended)

---

# Environment Variables

Copy '.env.example' to '.env' and fill in values:

'''ini
SECRET_KEY=your-django-secret
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8000,http//localhost:8000
STEAM_WEB_API_KEY=your-steam-api-key

Get Steam API Key at https://steamcommunity.com/dev/apikey

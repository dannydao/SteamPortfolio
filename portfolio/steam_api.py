import os, requests

API = "https://api.steampowered.com"

def _get(path, **params):
    # Read the key per call so .env changes are picked up without full restart
    key = os.getenv("STEAM_WEB_API_KEY")
    if not key:
        raise RuntimeError("STEAM_WEB_API_KEY is not set.")
    
    params = {"key": key, **params}

    r = requests.get(f"{API}/{path}", params=params, timeout=25)
    try:
        r.raise_for_status()
    except requests.HTTPError as e:
        raise RuntimeError(f"Steam API error {r.status_code} on {r.url}\nBody: {r.text}") from e
    return r.json()

def get_player_summaries(steamid):
    data = _get("ISteamUser/GetPlayerSummaries/v2", steamids=steamid)
    return (data.get("response", {}).get("players") or [{}])[0]

def get_steam_level(steamid):
    data = _get("IPlayerService/GetSteamLevel/v1", steamid=steamid)
    return data.get("response", {}).get("player_level", 0)

def get_owned_games(steamid):
    data = _get("IPlayerService/GetOwnedGames/v1",
                steamid=steamid, include_appinfo=1, include_played_free_games=1)
    return data.get("response", data)

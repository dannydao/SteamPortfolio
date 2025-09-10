import os, requests

API = "https://api.steampowered.com"
KEY = os.getenv("STEAM_WEB_API_KEY")

def _get(path, **params):
    params = {"keys": KEY, **params}
    r = requests.get(f"{API}/{path}", params=params, timeout=25)
    r.raise_for_status()
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
    return data.get("response", {})

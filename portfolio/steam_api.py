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

# --- Players / Accounts ---

def get_player_summaries(steamids):
    """
    Accepts a single steamid or an iterable of ids.
    Returns a list of player dicts.
    """
    if isinstance(steamids, (list, tuple, set)):
        ids_param = ",".join(map(str, steamids))
    else:
        ids_param = str(steamids)
    data = _get("ISteamUser/GetPlayerSummaries/v2", steamids=ids_param)
    return data.get("response", {}).get("players", [])

def get_steam_level(steamid):
    data = _get("IPlayerService/GetSteamLevel/v1", steamid=steamid)
    return data.get("response", {}).get("player_level", 0)

def get_friend_steamids(steamid):
    """
    Returns a list of friend steamids (subject to the user's privacy settings)
    """
    data = _get("ISteamUser/GetFriendList/v1", steamid=steamid, relationship="friend")
    friends = data.get("friendslist", {}).get("friends", []) or []
    return [f.get("steamid") for f in friends if f.get("steamid")]

# --- Library / Stats ---

def get_owned_games(steamid):
    """
    Normalized owned-games response: always return the inner 'response' dict if present.
    Include unplayed titles and app info for names/images.
    """
    data = _get("IPlayerService/GetOwnedGames/v1",
                steamid=steamid, 
                include_appinfo=1, 
                include_played_free_games=1,
                include_unplayed=1,
                skip_unvetted_apps=0
            )
    return data.get("response", data)

def get_number_of_current_players(appid: int) -> int:
    """
    Concurrent players right now for the given appid (may be 0 for niche or older apps).
    """
    url = "https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1"
    try:
        r = requests.get(url, params={"appid": appid}, timeout=20)
        r.raise_for_status()
        data = r.json()
        return int(data.get("response", {}).get("player_count", 0) or 0)
    except Exception:
        return 0
    
# --- Storefront Metadata (no API key required) ---

def get_store_appdetails(appid: int, cc="us", lang="en"):
    """
    Unofficial Storefront API. Return rich app metadata:
    name, genres, short_description, website, screenshots, etc.
    """
    url = "https://store.steampowered.com/api/appdetails"
    r = requests.get(url, params={"appids": appid, "cc": cc, "l": lang}, timeout=25)
    r.raise_for_status()
    payload = r.json()
    entry = payload.get(str(appid))
    if not entry or not entry.get("success"):
        return {}
    return entry.get("data", {})

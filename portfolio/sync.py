from django.utils import timezone
from .models import Profile, Game, UserGame
from . import steam_api

def sync_library(profile_id: int) -> None:
    """
    Fetch the user's Steam profile + owned games and store them.
    Called on first login and when "Sync now" is clicked.
    """
    p = Profile.objects.get(id=profile_id)
    
    # 1) Profile basics (persona, avatar, level)
    try:
        s = steam_api.get_player_summaries(p.steamid64)
        p.persona = s.get("personaname", "") or p.persona
        p.avatar = s.get("avatarfull", "") or p.avatar
        p.level = steam_api.get_steam_level(p.steamid64)
    except Exception:
        # Do not crash the view if Steam hiccups
        pass

    # 2) Owned games + minutes
    data = steam_api.get_owned_games(p.steamid64)
    for g in data.get("game", []):
        game, _ = Game.objects.get_or_create(
            appid=g["appid"],
            defaults={"name":g.get("name", "Unknown")}
        )
        UserGame.objects.update_or_create(
            profile=p, game=game,
            defaults={
                "playtime_forever": g.get("playtime_forever", 0),
                "playtime_2weeks": g.get("playtime_2weeks", 0),
                "rtime_last_played": g.get("rtime_last_played", 0),
            }
        )

    # 3) Mark last sync time
    p.last_synced = timezone.now()
    p.save()
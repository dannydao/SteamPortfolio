from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.core.cache import cache

from .models import Profile, UserGame
from .sync import sync_library
from . import steam_api
from itertools import islice

def login_page(request):
    # Renders a simple page with a "Sign in with Steam" link
    return render(request, "login.html")

def logout_view(request):
    logout(request)
    return redirect("login")

def home(request):
    # If logged in, go to portfolio; otherwise show login page
    return redirect("me") if request.user.is_authenticated else redirect("login")

@login_required
def my_portfolio(request):
    profile = Profile.objects.get(user=request.user)

    # First visit: populate from Steam
    if not profile.last_synced:
        sync_library(profile.id)

    # Cache the heavy query for speed (safe even if cache isn't configured)
    cache_key = f"lib:{profile.id}"
    games = cache.get(cache_key) if cache else None
    if games is None:
        qs = (UserGame.objects
              .select_related("game")
              .filter(profile=profile)
              .order_by("-playtime_forever"))
        games = list(qs.values("game__appid", "game__name",
                               "playtime_forever", "playtime_2weeks", "rtime_last_played"))
        
        if cache:
            cache.set(cache_key, games, 3600)

    return render(request, "portfolio.html", {"profile": profile, "games": games})

@login_required
def game_detail(request, appid: int):
    profile = Profile.objects.get(user=request.user)
    ug = get_object_or_404(
        UserGame.objects.select_related("game"),
        profile=profile, game__appid=appid
        )
    

    header = f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/header.jpg"

    # --- Player Count (live, cache 2 minutes) ---
    pc_key = f"pc:{appid}"
    player_count = cache.get(pc_key) if cache else None
    if player_count is None:
        try:
            player_count = steam_api.get_number_of_current_players(appid)
        except Exception:
            player_count = None
        if cache:
            cache.set(pc_key, player_count, 120)
    
    # --- Store metadata (genres, description, link) - cache 6h ---
    meta_key = f"store:{appid}"
    meta = cache.get(meta_key) if cache else None
    if meta is None:
        try:
            meta = steam_api.get_store_appdetails(appid) or {}
        except Exception:
            meta = {}
        if cache:
            cache.set(meta_key, meta, 6 * 3600)

    genres = [g["description"] for g in (meta.get("genres") or []) if "description" in g]
    description = meta.get("short_description") or None
    store_url = meta.get("website") or f"https://store.steampowered.com/app/{appid}"

    # --- Friends who also own the game - cache 2h ---
    # NOTE: subject to each friend's privacy; may be empty.
    friends_key = f"friends_own:{profile.id}:{appid}"
    friends_who_own = cache.get(friends_key) if cache else None
    if friends_who_own is None:
        friends_who_own = []
        try:
            friend_ids = steam_api.get_friend_steamids(profile.steamid64)[:100]
            # fetch names/avatars in one call
            summaries = {p["steamid"]: p for p in steam_api.get_player_summaries(friend_ids)} if friend_ids else {}

            # check up to 50 friends' libraries to keep a response quick
            for fid in islice(friend_ids, 0, 50):
                try:
                    og = steam_api.get_owned_games(fid)
                    games = og.get("games", []) or []
                    if any(g.get("appid") == appid for g in games):
                        ps = summaries.get(fid, {})
                        friends_who_own.append({
                            "steamid": fid,
                            "name": ps.get("personaname", "Friend"),
                            "avatar": ps.get("avatarFull", ""),
                            "profileurl": ps.get("profileurl", f"https://steamcommunity.com/profiles/{fid}"),
                        })
                except Exception:
                    # skip private/errored friends
                    continue
        except Exception:
            friends_who_own = []
        
        if cache:
            cache.set(friends_key, friends_who_own, 2 * 3600)
    
    ctx = {
        "ug": ug,
        "header": header,
        "player_count": player_count,
        "genres": genres,
        "description": description,
        "store_url": store_url,
        "friends_who_own": friends_who_own,
    }
    return render(request, "game_detail.html", ctx)

@login_required
def force_sync(request):
    profile = Profile.objects.get(user=request.user)
    sync_library(profile.id)
    if cache: cache.delete(f"lib:{profile.id}")
    return redirect("me")
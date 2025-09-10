from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.core.cache import cache

from .models import Profile, UserGame
from .sync import sync_library

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
    ug = get_object_or_404(UserGame.objects.select_related("game"),
                           profile=profile, game__appid=appid)
    header = f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/header.jpg"
    return render(request, "game_detail.html", {"ug": ug, "header": header}) 

@login_required
def force_sync(request):
    profile = Profile.objects.get(user=request.user)
    sync_library(profile.id)
    if cache: cache.delete(f"lib:{profile.id}")
    return redirect("me")
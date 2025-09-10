from .models import Profile

def save_steamid(backend, user, response, *arg, **kwargs):
    """
    Runs during Steam login. Stores the 64-bit SteamID on our Profile.
    """
    steamid64 = kwargs.get("uid")
    if not steamid64:
        return
    Profile.objects.get_or_create(user=user, defaults={"steamid64": steamid64})
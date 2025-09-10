from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    steamid64 = models.CharField(max_length=32, unique=True)
    persona = models.CharField(max_length=100, blank=True)
    avatar = models.URLField(blank=True)
    level = models.IntegerField(default=0)
    last_synced = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.steamid64})"
    
class Game(models.Model):
    appid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)

    def __str__(self): return f"{self.name} [{self.appid}]"

class UserGame(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    playtime_forever = models.IntegerField(default=0)
    playtime_2weeks = models.IntegerField(default=0)
    rtime_last_played = models.IntegerField(default=0)

    class Meta:
        unique_together = ('profile', 'game')

class Achievement(models.Model):
    appid = models.IntegerField()
    apiname =  models.CharField(max_length=200)
    displayname = models.CharField(max_length=200)
    description = models.TextField(blank= True)
    icon = models.URLField(blank=True)
    icongray = models.URLField(blank=True)

    class Meta:
        unique_together = ("appid", "apiname")

class UserAchievement(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    appid = models.IntegerField()
    apiname = models.CharField(max_length=200)
    achieved = models.BooleanField(default=False)
    unlocktime = models.IntegerField(default=0)

    class Meta:
        unique_together = ("profile", "appid", "apiname")
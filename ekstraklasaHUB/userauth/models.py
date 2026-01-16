from django.db import models
from django.contrib.auth.models import User

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00) 

    def __str__(self):
        return f"{self.user.username} - {self.balance} PLN"

class Prediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    match_id = models.CharField(max_length=50)
    home_team = models.CharField(max_length=100)
    away_team = models.CharField(max_length=100)
    home_score = models.IntegerField()
    away_score = models.IntegerField()
    stake = models.DecimalField(max_digits=10, decimal_places=2, default=10.00) 
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'match_id')

    def __str__(self):
        return f"{self.user.username}: {self.home_team}-{self.away_team} ({self.stake} PLN)"
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    favorite_team = models.CharField(max_length=100)

    def __str__(self):
        return f"Profil {self.user.username} ({self.favorite_team})"
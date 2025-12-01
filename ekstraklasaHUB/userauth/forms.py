from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

EKSTRAKLASA_TEAMS = [
    ('Jagiellonia Białystok', 'Jagiellonia Białystok'),
    ('Wisła Płock', 'Wisła Płock'),
    ('Legia Warszawa', 'Legia Warszawa'),
    ('Pogoń Szczecin', 'Pogoń Szczecin'),
    ('Lech Poznań', 'Lech Poznań'),
    ('Górnik Zabrze', 'Górnik Zabrze'),
    ('Raków Częstochowa', 'Raków Częstochowa'),
    ('Zagłębie Lubin', 'Zagłębie Lubin'),
    ('Widzew Łódź', 'Widzew Łódź'),
    ('Piast Gliwice', 'Piast Gliwice'),
    ('Bruk-Bet Termalica Nieciecza', 'Bruk-Bet Termalica Nieciecza'),
    ('Arka Gdynia', 'Arka Gdynia'),
    ('Cracovia', 'Cracovia'),
    ('Korona Kielce', 'Korona Kielce'),
    ('Radomiak Radom', 'Radomiak Radom'),
    ('Lechia Gdańsk', 'Lechia Gdańsk'),
    ('GKS Katowice', 'GKS Katowice'),
    ('Motor Lublin', 'Motor Lublin'),
]

class UserRegistrationForm(forms.ModelForm):
    favorite_team = forms.ChoiceField(
        choices=EKSTRAKLASA_TEAMS, 
        label="Wybierz swój klub",
        widget=forms.RadioSelect(attrs={'class': 'team-radio-input'})
    )
    
    password = forms.CharField(
        label="Hasło",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    confirm_password = forms.CharField(
        label="Potwierdź hasło",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'email'] 
        
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise ValidationError("Hasła nie są identyczne.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])      
        selected_team = self.cleaned_data.get('favorite_team')     
        if commit:
            user.save()       
        return user


class LoginForm(forms.Form):
    username = forms.CharField(
        label="Nazwa użytkownika",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label="Hasło",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
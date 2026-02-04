# ⚽ EkstraklasaHUB - Dokumentacja Projektu

### 📋 Kryteria Oceny i Realizacja Funkcjonalności

---

## 🌐 HTTP (6.0 / 6.0 pkt)

Zaimplementowano pełną komunikację opartą na architekturze REST.

### 🔹 CRUD (Operacje na danych)
| Zasób | Akcje | Metody HTTP |
| :--- | :--- | :--- |
| **Użytkownik** | Logowanie / Rejestracja | `POST` |
| **Zakłady bukmacherskie** | Dodawanie, Pobieranie, Usuwanie | `POST`, `GET`, `DELETE` |
| **Czat tekstowy** | Wysyłanie, Pobieranie, Edycja, Usuwanie | `POST`, `GET`, `PUT`, `DELETE` |

### 🔹 Funkcje dodatkowe HTTP
* **Wyszukiwanie wzorcem:** Możliwość filtrowania danych na stronie głównej przy użyciu wzorca tekstowego (zgodnie z REST).
* **Auth REST:** Pełna obsługa logowania i wylogowywania użytkownika.
* **Klient:** Stworzono dedykowaną aplikację kliencką do obsługi wszystkich punktów końcowych serwera.

---

## 📡 MQTT, WS, SSE (6.0 / 6.0 pkt)

Zaimplementowano mechanizmy komunikacji dwukierunkowej i czasu rzeczywistego.

### 🔹 Backend: MQTT

Protokół **MQTT** został wykorzystany do obsługi:
* 🗨️ **Czatu** (wymiana wiadomości między użytkownikami).
* 📈 **Aktualizacji wyników** meczów w czasie rzeczywistym.
* 🎰 **Typowania wyników** (odświeżanie kursów i zakładów).

### 🔹 Frontend: WebSocket (WS)
* Wykorzystanie protokołu WebSocket na poziomie frontendu do natychmiastowego wyświetlania zmian bez konieczności odświeżania strony.

---

## 🛠️ Inne (6.0 / 6.0 pkt)

Dodatkowe technologie i zaawansowane funkcjonalności systemowe.

### 🔹 Funkcjonalności protokołów
* **Dualizm komunikacji:** Możliwość korzystania z czatu za pomocą dwóch niezależnych protokołów: **MQTT** oraz **HTTP**.
* **Bezpieczeństwo:** Implementacja **JWT** (JSON Web Token) do autoryzacji zapytań.

### 🔹 System i Dane
* **Baza danych:** Wykorzystanie bazy danych do trwałego przechowywania informacji o użytkownikach, meczach i zakładach.

---

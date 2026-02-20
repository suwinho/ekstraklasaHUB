
# EkstraklasaHUB

A modern and interactive web dashboard for tracking the Polish football league, built with the Django framework and MQTT protocol.

## 📋 Project Description

This application serves as a central command center for football fans. It offers real-time access to league tables, club statistics, and live match results. The project combines a robust backend based on **Python (Django)** with a dynamic frontend that utilizes **WebSockets (MQTT)** for live data updates without page reloading. 

## 🚀 Features

- **Dashboard & Analytics:**
  - View current league standings
  - Check upcoming fixtures and recent results
- **Live Score System:**
  - Real-time score updates via MQTT protocol
  - Instant status changes (Live/Finished)
- **Club Profiles:**
  - Detailed information about every team
  - Match history and form analysis
- **Search Engine:**
  - Dynamic club search with autocomplete suggestions

## 🛠️ Tech Stack

The project utilizes the following technologies:

- **Python 3.x** - Programming language
- **Django 4.x** - Web framework
- **JavaScript (ES6+)** - Client-side logic
- **Paho MQTT** - WebSocket client for live data
- **HTML5 / CSS3** - Custom styling (Dark Theme)

## ⚙️ Prerequisites

To run this application locally, you will need:

- Python 3.8 or higher
- pip
- Git

## ▶️ How to Run

1.  **Clone the repository:**

    ```bash
    git clone [https://github.com/suwinho/ekstraklasaHUB.git](https://github.com/suwinho/ekstraklasaHUB.git)
    ```

2.  **Navigate to the project directory:**

    ```bash
    cd ekstraklasaHUB
    ```

3.  **Set up a virtual environment:**

    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

4.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

5.  **Apply database migrations:**

    ```bash
    python manage.py migrate
    ```

6.  **Run the application:**

    ```bash
    python manage.py runserver
    ```

7.  **Access the application:**
    Once the server is running, open your browser and go to: `http://127.0.0.1:8000`

## 🤝 Author

**suwinho** - [GitHub Profile](https://github.com/suwinho)

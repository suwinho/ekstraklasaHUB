# ⚽ EkstraklasaHUB - Real-Time Sports Platform

EkstraklasaHUB is a comprehensive web application designed for live football match tracking, betting simulation, and real-time user interaction. The project focuses on high-performance data synchronization and low-latency communication using a dual-protocol architecture.

---

## 🚀 Key Technical Highlights

* **Dual-Protocol Chat System**: Seamless message exchange using both **MQTT** and **HTTP** protocols.
* **Real-Time Synchronization**: Live match results and betting odds updated instantly via **MQTT** and **WebSockets**.
* **RESTful Architecture**: Full CRUD operations for user management and betting systems.
* **Security First**: Implementation of secure password **hashing** and session-based authentication.

---

## 🛠 Tech Stack

* **Backend**: Python, Django
* **Real-Time**: MQTT Protocol, WebSockets
* **Database**: PostgreSQL / Relational DB
* **Frontend**: JavaScript, HTML/CSS (integrated with WebSocket clients)

---

## 🌐 Feature Breakdown

### 1. HTTP Architecture (REST)
The platform implements a full REST-compliant API for core data management:

| Resource | Actions | HTTP Methods |
| :--- | :--- | :--- |
| **User** | Registration, Authentication | `POST` |
| **Betting** | Odds management, Place/Delete bets | `POST`, `GET`, `DELETE` |
| **Chat History** | Message retrieval and moderation | `POST`, `GET`, `PUT`, `DELETE` |

* **Pattern Search**: Advanced data filtering on the main dashboard using text-pattern matching.
* **Dedicated Client**: Custom application logic to handle server endpoint interactions.

### 2. Real-Time Communication (MQTT & WebSockets)

To ensure low-latency updates, the project leverages bidirectional communication:

* **MQTT Backend**: Used for instant message relay in chat and broadcasting live match score changes.
* **WebSocket Frontend**: Enables the UI to reflect changes immediately without requiring a page refresh.
* **Operational Dualism**: Users can interact with the chat via MQTT or traditional HTTP, ensuring system redundancy.

### 3. Data Integrity & Security
* **Password Protection**: All user credentials are secured using modern hashing functions.
* **Persistent Storage**: A relational database handles complex relationships between users, match events, and betting history.

---

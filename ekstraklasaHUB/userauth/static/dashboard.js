/* ==========================================================================
   STREFA 1: NARZĘDZIA POMOCNICZE (Utils, CSRF, UI)
   ========================================================================== */

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function showToast(text) {
  const container = document.getElementById("notifications");
  const toast = document.createElement("div");
  toast.className = "mqtt-toast";
  toast.innerHTML = `🔔 ${text}`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

function updateBalance(amount) {
  const element = document.getElementById("user-balance");
  if (element) {
    element.innerText = parseFloat(amount).toFixed(2);
  }
}

/* ==========================================================================
   STREFA 2: LOGIKA TYPERA (Obsługa Zakładów)
   ========================================================================== */

function placeBet(id) {
  const box = document.querySelector(`.prediction-box[data-match-id="${id}"]`);
  const homeScore = box.querySelector(".pred-home").value;
  const awayScore = box.querySelector(".pred-away").value;
  const stake = box.querySelector(".pred-stake").value;

  if (homeScore === "" || awayScore === "" || stake === "") {
    alert("Uzupełnij wynik i stawkę!");
    return;
  }

  fetch("/api/predict/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: JSON.stringify({
      match_id: id,
      home_team: box.dataset.home,
      away_team: box.dataset.away,
      home_score: homeScore,
      away_score: awayScore,
      stake: stake,
    }),
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.error) {
        alert("Błąd: " + data.error);
      } else {
        box.querySelector(".btn-del-pred").style.display = "inline-block";
        updateBalance(data.new_balance);
      }
    })
    .catch((err) => console.error("Błąd zapisu zakładu:", err));
}

function cancelBet(id) {
  if (!confirm("Wycofać zakład? Środki wrócą na konto.")) return;

  fetch("/api/predict/", {
    method: "DELETE",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: JSON.stringify({ match_id: id }),
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.status === "deleted") {
        const box = document.querySelector(
          `.prediction-box[data-match-id="${id}"]`,
        );
        box.querySelector(".pred-home").value = "";
        box.querySelector(".pred-away").value = "";
        box.querySelector(".pred-stake").value = "";
        box.querySelector(".btn-del-pred").style.display = "none";
        updateBalance(data.new_balance);
      }
    });
}

document.addEventListener("DOMContentLoaded", () => {
  fetch("/api/predict/")
    .then((res) => res.json())
    .then((data) => {
      updateBalance(data.balance);

      if (data.predictions) {
        data.predictions.forEach((pred) => {
          const box = document.querySelector(
            `.prediction-box[data-match-id="${pred.match_id}"]`,
          );
          if (box) {
            box.querySelector(".pred-home").value = pred.home_score;
            box.querySelector(".pred-away").value = pred.away_score;
            box.querySelector(".pred-stake").value = pred.stake;
            box.querySelector(".btn-del-pred").style.display = "inline-block";
          }
        });
      }
    })
    .catch((err) => console.error("Błąd ładowania danych początkowych:", err));
});

/* ==========================================================================
   STREFA 3: MQTT / CZAT 
   ========================================================================== */

const mqtt_broker = "broker.hivemq.com";
const mqtt_port = 8000;
const chat_topic = "ekstraklasa/chat";
const clientID = "web_fan_" + Math.random().toString(16).substr(2, 8);

let client;

try {
  client = new Paho.MQTT.Client(mqtt_broker, mqtt_port, clientID);
} catch (e) {
  console.error("Błąd: Biblioteka Paho MQTT nie została załadowana.", e);
}

if (client) {
  client.onMessageArrived = function (message) {
    const topic = message.destinationName;
    try {
      const payload = JSON.parse(message.payloadString);

      if (topic === "ekstraklasa/notifications") {
        showToast(payload.text);
      } else if (topic === chat_topic) {
        appendChatMessage(payload);
      }
    } catch (e) {
      console.error("Błąd parsowania JSON z MQTT:", e);
    }
  };

  client.connect({
    onSuccess: function () {
      console.log("Połączono z MQTT");
      client.subscribe("ekstraklasa/notifications");
      client.subscribe(chat_topic);
    },
    useSSL: false,
  });
}

function sendMessage() {
  const input = document.getElementById("chat-input");
  const msgText = input.value.trim();
  const useHttp = document.getElementById("protocol-switch").checked;
  if (typeof currentUser === "undefined") {
    console.error("Błąd: Brak nazwy użytkownika.");
    return;
  }

  if (msgText) {
    if (useHttp) {
      console.log("HTTP");
      fetch("/api/chat/send/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({ text: msgText }),
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.status === "ok") {
            input.value = "";
            appendChatMessage({
              id: data.id,
              user: currentUser,
              text: msgText,
              time: new Date().toLocaleTimeString([], {
                hour: "2-digit",
                minute: "2-digit",
              }),
            });
          } else {
            alert("Błąd wysyłania HTTP: " + data.error);
          }
        })
        .catch((err) => console.error("Błąd API czatu:", err));
    } else {
      if (client) {
        console.log("WEB SOCKET");
        const messageData = {
          user: currentUser,
          text: msgText,
          time: new Date().toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          }),
        };

        const message = new Paho.MQTT.Message(JSON.stringify(messageData));
        message.destinationName = chat_topic;
        client.send(message);

        input.value = "";
      } else {
        alert("Błąd: Klient MQTT nie jest połączony.");
      }
    }
  }
}

const chatInput = document.getElementById("chat-input");
if (chatInput) {
  chatInput.addEventListener("keypress", function (e) {
    if (e.key === "Enter") sendMessage();
  });
}

function appendChatMessage(data) {
  const chatBox = document.getElementById("chat-box");
  const div = document.createElement("div");

  const isMe = typeof currentUser !== "undefined" && data.user === currentUser;
  div.className = "chat-msg" + (isMe ? " me" : "");

  div.dataset.id = data.id;
  let buttonsHtml = "";
  if (isMe && data.id) {
    buttonsHtml = `
        <div class="msg-actions">
            <button onclick="enableEditMode(this)" class="btn-edit" title="Edytuj">✏️</button>
            <button onclick="deleteMessage(this)" class="btn-delete" title="Usuń">🗑️</button>
        </div>
      `;
  }

  div.innerHTML = `
      <span class="msg-time">${data.time}</span> 
      <strong>${data.user}:</strong> 
      <span class="msg-content">${data.text}</span>
      ${buttonsHtml}
  `;

  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function deleteMessage(btn) {
  if (!confirm("Czy na pewno chcesz usunąć tę wiadomość?")) return;

  const msgDiv = btn.closest(".chat-msg");
  const msgId = msgDiv.dataset.id;

  fetch(`/api/chat/message/${msgId}/`, {
    method: "DELETE",
    headers: {
      "X-CSRFToken": getCookie("csrftoken"),
    },
  })
    .then((res) => {
      if (res.ok) {
        msgDiv.remove();
      } else {
        alert("Nie udało się usunąć wiadomości.");
      }
    })
    .catch((err) => console.error("Błąd usuwania:", err));
}

function enableEditMode(btn) {
  const msgDiv = btn.closest(".chat-msg");
  const contentSpan = msgDiv.querySelector(".msg-content");
  const currentText = contentSpan.innerText;
  const actionsDiv = msgDiv.querySelector(".msg-actions");

  actionsDiv.style.display = "none";

  const editInput = document.createElement("input");
  editInput.type = "text";
  editInput.value = currentText;
  editInput.className = "edit-input";

  const saveBtn = document.createElement("button");
  saveBtn.innerText = "Zapisz";
  saveBtn.onclick = () =>
    saveEdit(
      msgDiv,
      editInput.value,
      contentSpan,
      actionsDiv,
      editInput,
      saveBtn,
      cancelBtn,
    );

  const cancelBtn = document.createElement("button");
  cancelBtn.innerText = "Anuluj";
  cancelBtn.onclick = () => {
    contentSpan.style.display = "";
    editInput.remove();
    saveBtn.remove();
    cancelBtn.remove();
    actionsDiv.style.display = "";
  };

  contentSpan.style.display = "none";
  msgDiv.appendChild(editInput);
  msgDiv.appendChild(saveBtn);
  msgDiv.appendChild(cancelBtn);
}

function saveEdit(
  msgDiv,
  newText,
  contentSpan,
  actionsDiv,
  editInput,
  saveBtn,
  cancelBtn,
) {
  const msgId = msgDiv.dataset.id;

  fetch(`/api/chat/message/${msgId}/`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: JSON.stringify({ text: newText }),
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.status === "ok" || !data.error) {
        contentSpan.innerText = newText;

        contentSpan.style.display = "";
        editInput.remove();
        saveBtn.remove();
        cancelBtn.remove();
        actionsDiv.style.display = "";
      } else {
        alert("Błąd edycji: " + data.error);
      }
    })
    .catch((err) => console.error("Błąd edycji:", err));
}

/* ==========================================================================
   STREFA 4: WYSZUKIWARKA KLUBÓW
   ========================================================================== */

const searchInput = document.getElementById("club-search");
const resultsList = document.getElementById("search-results");

if (searchInput && resultsList) {
  searchInput.addEventListener("input", function () {
    const query = searchInput.value;

    if (query.length > 0) {
      fetch(`/api/search/?search=${query}`)
        .then((r) => r.json())
        .then((d) => {
          resultsList.innerHTML = "";
          if (d.results.length > 0) {
            resultsList.style.display = "block";
            d.results.forEach((club) => {
              const li = document.createElement("li");
              li.textContent = club.name;
              li.onclick = () =>
                (window.location.href = `/club/${club.id}/stats/`);
              resultsList.appendChild(li);
            });
          } else {
            resultsList.style.display = "none";
          }
        });
    } else {
      resultsList.style.display = "none";
    }
  });

  document.addEventListener("click", function (e) {
    if (!searchInput.contains(e.target) && !resultsList.contains(e.target)) {
      resultsList.style.display = "none";
    }
  });
}

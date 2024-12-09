console.log("Script js loaded");

// Функция для инициализации боковой панели и обработчиков событий
function initializeSidebar() {
    console.log("Initializing sidebar...");

    const sidebar = document.getElementById("sidebar");
    const toggleSidebar = document.getElementById("toggleSidebar");
    const closeSidebar = document.getElementById("closeSidebar");

    console.log("Sidebar element:", sidebar);
    console.log("ToggleSidebar button:", toggleSidebar);
    console.log("CloseSidebar button:", closeSidebar);

    if (!sidebar || !toggleSidebar || !closeSidebar) {
        console.error("One or more required elements not found!");
        return;
    }

    // Логика открытия боковой панели
    toggleSidebar.addEventListener("click", function () {
        console.log("ToggleSidebar button clicked");
        sidebar.classList.add("active");
        console.log("Sidebar state: active");
    });

    // Логика закрытия боковой панели
    closeSidebar.addEventListener("click", function () {
        sidebar.classList.remove("active");
        console.log("Sidebar state: inactive");
    });

    // Закрытие боковой панели при клике вне её области
    document.addEventListener("click", function (event) {
        if (!sidebar.contains(event.target) && event.target !== toggleSidebar) {
            sidebar.classList.remove("active");
            console.log("Sidebar state: inactive (outside click)");
        }
    });

}

// Инициализация при начальной загрузке страницы
document.addEventListener("DOMContentLoaded", function () {
    console.log("Script loaded");
    initializeSidebar();
});

function initializeChat() {
    console.log("Initializing chat...");

    const chat = document.getElementById("chat");
    const chatButton = document.querySelector(".chat-button");
    const closeChat = document.getElementById("closeChat");
    const chatUserSelect = document.getElementById("chatUserSelect");
    const chatInput = document.getElementById("chatInput");
    const sendMessage = document.getElementById("sendMessage");
    const chatTabs = document.getElementById("chatTabs");
    const chatContent = document.getElementById("chatContent");
    const userList = document.getElementById("userList");
    const toggleUserList = document.getElementById("toggleUserList");

    if (!chat || !chatButton || !closeChat || !chatUserSelect || !chatInput || !sendMessage || !chatTabs || !chatContent || !userList || !toggleUserList) {
        console.error("One or more chat elements are missing!");
        return;
    }

    const socket = new WebSocket("ws://localhost:8000/ws");

    socket.addEventListener("open", () => {
        console.log("WebSocket connection established");
    });

    socket.addEventListener("message", (event) => {
        const message = JSON.parse(event.data);
        const { sender, content } = message;

        const activeTab = document.querySelector(".tab.active");
        const tabContent = document.getElementById(`chatContent-${sender}`);
        if (tabContent) {
            const messageElement = document.createElement("div");
            messageElement.classList.add("message", "other-user");
            messageElement.textContent = `${sender}: ${content}`;
            tabContent.appendChild(messageElement);
            tabContent.scrollTop = tabContent.scrollHeight;
        }

        console.log("Received message:", message);
    });

    socket.addEventListener("close", () => {
        console.log("WebSocket connection closed");
    });

    socket.addEventListener("error", (error) => {
        console.error("WebSocket error:", error);
    });

    chatButton.addEventListener("click", () => {
        chat.style.display = "flex";
        loadUsers();
        console.log("Chat opened");
    });

    closeChat.addEventListener("click", () => {
        chat.style.display = "none";
        console.log("Chat closed");
    });

    toggleUserList.addEventListener("click", () => {
        userList.style.display = userList.style.display === "none" ? "block" : "none";
    });

    chatUserSelect.addEventListener("change", async () => {
        const selectedUserOption = chatUserSelect.selectedOptions[0];
        const selectedUserId = selectedUserOption.value;
        const selectedUsername = selectedUserOption.textContent;

        if (selectedUserId && !document.getElementById(`tab-${selectedUserId}`)) {
            const tabButton = document.createElement("div");
            tabButton.id = `tab-${selectedUserId}`;
            tabButton.classList.add("tab");
            tabButton.innerHTML = `
                ${selectedUsername}
                <button class="close-tab">✕</button>
            `;

            tabButton.querySelector(".close-tab").addEventListener("click", (event) => {
                event.stopPropagation();
                document.getElementById(`chatContent-${selectedUserId}`).remove();
                tabButton.remove();
                console.log(`Closed chat with ${selectedUsername}`);
            });

            tabButton.addEventListener("click", async () => {
                document.querySelectorAll(".tab").forEach(tab => tab.classList.remove("active"));
                tabButton.classList.add("active");

                document.querySelectorAll(".tab-content").forEach(content => content.style.display = "none");
                const tabContent = document.getElementById(`chatContent-${selectedUserId}`);
                if (tabContent) {
                    tabContent.style.display = "block";
                    const messages = await fetchMessageHistory(selectedUserId);

                    tabContent.innerHTML = "";
                    messages.forEach(msg => {
                        const messageElement = document.createElement("div");
                        messageElement.classList.add("message", msg.sender === "me" ? "my-message" : "other-user");
                        messageElement.textContent = `${msg.sender}: ${msg.content}`;
                        tabContent.appendChild(messageElement);
                    });

                    tabContent.scrollTop = tabContent.scrollHeight;
                }
            });

            chatTabs.appendChild(tabButton);

            const tabContent = document.createElement("div");
            tabContent.id = `chatContent-${selectedUserId}`;
            tabContent.classList.add("tab-content");
            tabContent.style.display = "none";
            chatContent.appendChild(tabContent);

            tabButton.click();
        }

        userList.style.display = "none";
    });

    sendMessage.addEventListener("click", async () => {
        console.log("Send button clicked"); // Лог при клике
        const activeTab = document.querySelector(".tab.active");
        if (!activeTab) {
            alert("Please select a user to chat with.");
            return;
        }

        const selectedUserId = activeTab.id.replace("tab-", "");
        const message = chatInput.value.trim();

        if (!message) {
            alert("Please enter a message.");
            return;
        }

        console.log(`Sending message to user ID: ${selectedUserId}`);

        // Отправляем сообщение через WebSocket
        try {
            socket.send(JSON.stringify({ receiver: selectedUserId, content: message }));
            console.log(`Message sent via WebSocket to user ID: ${selectedUserId}`);
        } catch (error) {
            console.error("WebSocket error while sending message:", error);
        }

        // Отправляем сообщение через API
        try {
            const response = await sendMessageToServer(selectedUserId, message);
            if (response) {
                console.log(`Message sent via API to user ID: ${selectedUserId}`);
            } else {
                console.error("Failed to send message via API.");
            }
        } catch (error) {
            console.error("API error while sending message:", error);
        }

        // Добавляем сообщение в текущий UI
        const tabContent = document.getElementById(`chatContent-${selectedUserId}`);
        if (tabContent) {
            const messageElement = document.createElement("div");
            messageElement.classList.add("message", "my-message");
            messageElement.textContent = `You: ${message}`;
            tabContent.appendChild(messageElement);
            tabContent.scrollTop = tabContent.scrollHeight;
        }

        // Очищаем поле ввода
        chatInput.value = "";
    });

    console.log("Chat initialized successfully.");
}

//// Загрузка пользователей
//async function loadUsers() {
//    const response = await fetch("/api/chat/users", { method: "GET" });
//    if (!response.ok) {
//        console.error("Failed to load users");
//        return;
//    }
//
//    const users = await response.json();
//    const chatUserSelect = document.getElementById("chatUserSelect");
//    chatUserSelect.innerHTML = "";
//
//    users.forEach(user => {
//        const option = document.createElement("option");
//        option.value = user.id;
//        option.textContent = user.username;
//        chatUserSelect.appendChild(option);
//    });
//}

// Загрузка истории сообщений
async function fetchMessageHistory(userId) {
    try {
        const response = await fetch(`/api/chat/messages/${userId}`, {
            method: "GET",
            credentials: "include",
        });

        if (!response.ok) {
            console.error("Failed to fetch message history");
            return [];
        }

        return await response.json();
    } catch (error) {
        console.error("Error fetching message history:", error);
        return [];
    }
}

async function loadUsers() {
    try {
        const response = await fetch('/api/chat/users'); // Маршрут для получения пользователей
        if (!response.ok) {
            throw new Error(`Error fetching users: ${response.status}`);
        }

        const users = await response.json(); // Преобразуем ответ в JSON
        const userSelect = document.getElementById('chatUserSelect'); // Найти select-элемент

        if (!userSelect) {
            console.error("User select element not found!");
            return;
        }

        // Очищаем текущий список пользователей (если есть)
        userSelect.innerHTML = "";

        // Заполняем список пользователей
        users.forEach(user => {
            const option = document.createElement('option');
            option.value = user.id; // ID пользователя
            option.textContent = user.username; // Имя пользователя
            userSelect.appendChild(option);
        });

        console.log("Users loaded:", users);
    } catch (error) {
        console.error("Error loading users:", error);
    }
}


// Отправка сообщения через API
async function sendMessageToServer(receiverId, content) {
    try {
        const response = await fetch(`/api/chat/send-message`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({ receiver_id: receiverId, content: content }),
        });

        if (!response.ok) {
            console.error("Failed to send message");
            return null;
        }

        return await response.json();
    } catch (error) {
        console.error("Error sending message:", error);
        return null;
    }
}

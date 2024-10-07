// Функция для проверки и обновления access токена
async function refreshToken() {
    const refresh_token = localStorage.getItem('refresh_token');
    if (!refresh_token) {
        console.log("No refresh token found");
        return false; // Нет refresh токена, нужно заново авторизоваться
    }

    try {
        const response = await fetch('/refresh_token', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh_token: refresh_token })
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('access_token', data.access_token);
            console.log("Access token refreshed");
            return true; // Токен обновлен
        } else {
            console.log("Failed to refresh token");
            return false; // Не удалось обновить токен
        }
    } catch (error) {
        console.error('Error during token refresh:', error);
        return false; // Произошла ошибка при обновлении токена
    }
}

// Функция для выполнения защищенных запросов с автоматическим обновлением токена
async function fetchWithAuth(url, options = {}) {
    // Проверяем и обновляем токен
    const tokenUpdated = await refreshToken();

    // Если токен не удалось обновить, перенаправляем на страницу входа
    if (!tokenUpdated) {
        window.location.href = '/login';
        return;
    }

    const access_token = localStorage.getItem('access_token');

    // Добавляем токен в заголовки запроса
    options.headers = {
        ...options.headers,
        'Authorization': `Bearer ${access_token}`
    };

    // Выполняем запрос
    const response = await fetch(url, options);

    if (response.status === 401) {
        // Если запрос отклонен, перенаправляем пользователя на страницу входа
        window.location.href = '/login';
    }

    return response;
}

// Обработчик события для формы входа пользователя
document.addEventListener("DOMContentLoaded", function() {
    const loginForm = document.getElementById('login-form');

    if (loginForm) {
        loginForm.addEventListener('submit', async function (e) {
            e.preventDefault(); // Предотвращаем отправку формы по умолчанию

            // Получаем значения полей username и password
            const username = document.getElementById('user').value;
            const password = document.getElementById('pass').value;

            console.log("Login attempt:", username);  // Логируем попытку входа

            try {
                // Отправляем POST-запрос на сервер для получения токенов
                const response = await fetch('/token', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body: new URLSearchParams({
                        'username': username,
                        'password': password
                    })
                });

                if (response.ok) {
                    const data = await response.json();
                    localStorage.setItem('access_token', data.access_token); // Сохраняем access токен
                    localStorage.setItem('refresh_token', data.refresh_token); // Сохраняем refresh токен
                    window.location.href = '/dashboard'; // Перенаправляем на защищённую страницу
                    console.log("Login successful");
                } else {
                    const data = await response.json();
                    document.getElementById('error-message').textContent = data.detail; // Выводим ошибку
                    console.log("Login failed:", data.detail);  // Логируем ошибку
                }
            } catch (error) {
                console.error('Error during login:', error);
                alert('An error occurred during login. Please try again.');
            }
        });
    }
});

// Обработчик события для формы регистрации пользователя
document.addEventListener("DOMContentLoaded", function() {
    const registerForm = document.getElementById('register-form');

    if (registerForm) {
        registerForm.addEventListener('submit', async function (e) {
            e.preventDefault(); // Предотвращаем отправку формы по умолчанию

            // Получаем значения полей формы
            const username = document.getElementById('new-user').value;
            const password = document.getElementById('new-pass').value;
            const role = document.getElementById('role').value;

            try {
                // Отправляем POST-запрос на сервер для регистрации пользователя
                const response = await fetch('/register/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username: username, password: password, role: role })
                });

                if (response.ok) {
                    alert('Registration successful');
                    window.location.href = '/login'; // Перенаправляем на страницу входа после регистрации
                } else {
                    const data = await response.json();
                    alert(data.detail); // Показываем ошибку
                }
            } catch (error) {
                console.error('Error during registration:', error);
                alert('An error occurred during registration. Please try again.');
            }
        });
    }
});

// Пример использования fetchWithAuth для защищенного запроса
async function getDashboardData() {
    const response = await fetchWithAuth('/dashboard', {
        method: 'GET'
    });

    if (response.ok) {
        const data = await response.json();
        console.log('Dashboard data:', data);
    } else {
        console.error('Failed to fetch dashboard data');
    }
}

// Пример использования WebSocket
const socket = new WebSocket('ws://localhost:8000/ws');

socket.addEventListener('open', function (event) {
    console.log('WebSocket connection opened');
});

socket.addEventListener('message', function (event) {
    console.log('Message from server: ', event.data);
});

socket.addEventListener('close', function (event) {
    console.log('WebSocket connection closed');
});


socket.addEventListener('error', function (event) {
    console.error('WebSocket error:', event);
});

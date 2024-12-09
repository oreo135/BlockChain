// Проверка загрузки main.js
console.log('main.js загружен');

// Функция для выполнения защищённых запросов
async function fetchWithAuth(url, options = {}) {
    console.log('fetchWithAuth вызван для URL:', url);
    const response = await fetch(url, {
        ...options,
        credentials: 'include', // Гарантирует передачу куков с запросом
    });

    if (response.status === 401) {
        console.error('Unauthorized, redirecting to login');
        window.location.href = '/login'; // Перенаправление на страницу логина
    }

    return response;
}

// Функция для загрузки защищённых страниц
async function fetchProtectedPage(url) {
    try {
        const response = await fetchWithAuth(url, { method: 'GET' });

        if (response.ok) {
            const pageContent = await response.text();
            document.body.innerHTML = pageContent; // Загрузка содержимого страницы

            // Повторная инициализация скриптов после динамической загрузки
            initializeSidebar();
            initializeChat();
            console.log(`${url} loaded successfully.`);
        } else {
            console.error(`Failed to load ${url}`);
        }
    } catch (error) {
        console.error('Error loading page:', error);
    }
}

// Обработчик для формы входа
document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById('loginForm');

    if (loginForm) {
        loginForm.addEventListener('submit', async function (event) {
            event.preventDefault(); // Предотвращаем отправку формы

            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;

            try {
                const response = await fetch('/auth/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ username, password }),
                    credentials: 'include', // Передача куков
                });

                if (response.ok) {
                    alert('Login successful');
                    window.location.href = '/dashboard'; // Перенаправляем пользователя
                } else {
                    const errorData = await response.json();
                    alert(`Error: ${errorData.detail || 'Login failed'}`);
                }
            } catch (error) {
                console.error('Error during login:', error);
                alert('An error occurred. Please try again.');
            }
        });
    }
});

// Пример загрузки dashboard
document.addEventListener("DOMContentLoaded", function () {
    if (window.location.pathname === '/dashboard') {
        fetchProtectedPage('/dashboard');
    }
});

// Обработчик для формы регистрации
document.addEventListener("DOMContentLoaded", function () {
    const registerForm = document.getElementById('registerForm');

    if (registerForm) {
        registerForm.addEventListener('submit', async function (event) {
            event.preventDefault(); // Предотвращаем отправку формы

            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;

            try {
                const response = await fetch('/auth/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ username, password }),
                    credentials: 'include', // Гарантирует передачу куков
                });

                if (response.ok) {
                    alert('Registration successful');
                    window.location.href = '/login'; // Перенаправляем после успешной регистрации
                } else {
                    const errorData = await response.json();
                    alert(`Error: ${errorData.detail[0]?.msg || 'Registration failed'}`);
                }
            } catch (error) {
                console.error('Error during registration:', error);
                alert('An error occurred. Please try again later.');
            }
        });
    }
});

// Функция для загрузки admin_page
async function getAdminPageData() {
    console.log('getAdminPageData вызван');
    const response = await fetchWithAuth('/admin_page', { method: 'GET' });

    if (response.ok) {
        const data = await response.text();
        document.documentElement.innerHTML = data;
        console.log('Admin page loaded');
    } else {
        console.error('Failed to load admin page');
    }
}

// Функция для загрузки user_page
async function getUserPageData() {
    console.log('getUserPageData вызван');
    const response = await fetchWithAuth('/user_page', { method: 'GET' });

    if (response.ok) {
        const data = await response.text();
        document.documentElement.innerHTML = data;
        console.log('User page loaded');
    } else {
        console.error('Failed to load user page');
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

// Функция для проверки и обновления access токена
async function refreshToken() {
    const refresh_token = localStorage.getItem('refresh_token');
    if (!refresh_token) {
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
            return true; // Токен обновлен
        } else {
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
document.getElementById('login-form').addEventListener('submit', async function (e) {
    e.preventDefault(); // Предотвращаем отправку формы по умолчанию

    // Получаем значения полей username и password
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

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
        } else {
            const data = await response.json();
            document.getElementById('error-message').textContent = data.detail; // Выводим ошибку
        }
    } catch (error) {
        console.error('Error during login:', error);
        alert('An error occurred during login. Please try again.');
    }
});

// Обработчик события для всплывающего окна регистрации
document.getElementById('register-form').addEventListener('submit', async function (e) {
    e.preventDefault(); // Предотвращаем отправку формы по умолчанию

    // Получаем значения полей формы
    const username = document.getElementById('new-username').value;
    const password = document.getElementById('new-password').value;
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
            window.location.href = '/'; // Перенаправляем на главную страницу
        } else {
            const data = await response.json();
            alert(data.detail); // Показываем ошибку
        }
    } catch (error) {
        console.error('Error during registration:', error);
        alert('An error occurred during registration. Please try again.');
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

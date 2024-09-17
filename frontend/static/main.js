// Обработчик события для формы входа пользователя
document.getElementById('login-form').addEventListener('submit', async function (e) {
    e.preventDefault(); // Предотвращаем отправку формы по умолчанию

    // Получаем значения полей username и password
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    try {
        // Отправляем POST-запрос на сервер для получения токена
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
            localStorage.setItem('access_token', data.access_token); // Сохраняем токен в локальном хранилище
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

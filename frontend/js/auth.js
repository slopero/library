// ─────────────────────────────────────────────
// auth.js — общая логика авторизации.
// Подключается на ВСЕХ страницах сайта.
// Отвечает за:
//   - хранение токена авторизации
//   - обновление шапки (Войти / логин пользователя)
//   - добавление токена к запросам на бэк
// ─────────────────────────────────────────────

// Токен — это строка которую сервер выдаёт после успешного входа.
// Мы храним его в localStorage — он сохраняется между перезагрузками страницы.
// Ключи для localStorage
const TOKEN_KEY = "auth_token";
const USER_KEY  = "auth_user";   // логин пользователя


// ── Работа с токеном ─────────────────────────

/**
 * Сохранить токен и данные пользователя после входа.
 * Вызывается на странице login.html после успешного ответа от бэка.
 */
function saveAuth(token, username) {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, username);
}

/**
 * Получить токен. Возвращает строку или null если не авторизован.
 */
function getToken() {
    return localStorage.getItem(TOKEN_KEY);
}

/**
 * Проверить авторизован ли пользователь.
 */
function isLoggedIn() {
    return getToken() !== null;
}

/**
 * Выйти из аккаунта — удалить токен и перейти на главную.
 */
function logout() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    window.location.href = "index.html";
}


// ── Обёртка над fetch ─────────────────────────

/**
 * apiFetch — замена стандартному fetch для запросов к бэкенду.
 * Автоматически:
 *   - подставляет API_URL перед путём
 *   - добавляет токен в заголовок Authorization если он есть
 *   - добавляет Content-Type: application/json
 *
 * Использование:
 *   const data = await apiFetch("/books/");
 *   const data = await apiFetch("/cart/", { method: "POST", body: JSON.stringify({book_id: 1}) });
 */
async function apiFetch(path, options = {}) {
    const token = getToken();

    const headers = {
        "Content-Type": "application/json",
        // Если токен есть — добавляем заголовок Authorization.
        // Бэк будет проверять этот заголовок чтобы понять кто делает запрос.
        ...(token ? { "Authorization": `Bearer ${token}` } : {}),
        ...(options.headers || {}),
    };

    const response = await fetch(`${API_URL}${path}`, {
        ...options,
        headers,
    });

    // Если сервер вернул 401 (не авторизован) — токен устарел, выходим
    if (response.status === 401) {
        logout();
        return null;
    }

    // Если ответ не OK (не 2xx) — бросаем ошибку с текстом от сервера
    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: "Неизвестная ошибка" }));
        throw new Error(error.detail || "Ошибка сервера");
    }

    return response.json();
}


// ── Обновление шапки ─────────────────────────

/**
 * Обновить кнопку в шапке в зависимости от состояния авторизации.
 * Вызывается при загрузке каждой страницы.
 *
 * Если не авторизован — показывает кнопку "Войти".
 * Если авторизован — показывает логин пользователя и кнопку выхода.
 */
function updateNavbar() {
    const authContainer = document.getElementById("navbar-auth");
    if (!authContainer) return;

    if (isLoggedIn()) {
        const username = localStorage.getItem(USER_KEY) || "Профиль";
        const isAdmin  = localStorage.getItem("is_admin") === "true";
        // Ссылка на кабинет зависит от роли
        const cabinetUrl = isAdmin ? "admin_cabinet.html" : "user_cabinet.html";
        authContainer.innerHTML = `
            <a href="${cabinetUrl}" class="navbar__link" style="color: var(--accent-light)">
                👤 ${username}
            </a>
            <button class="navbar__btn" onclick="logout()">Выйти</button>
        `;
    } else {
        authContainer.innerHTML = `
            <a href="login.html" class="navbar__btn">Войти</a>
        `;
    }
}

// Обновляем шапку сразу при загрузке скрипта
document.addEventListener("DOMContentLoaded", updateNavbar);


// ── Бейдж корзины ─────────────────────────────

/**
 * Обновить счётчик товаров в корзине в шапке.
 * Количество храним в localStorage чтобы не делать лишний запрос к бэку
 * при каждой загрузке страницы.
 */
function updateCartBadge(count) {
    const badge = document.getElementById("cart-badge");
    if (!badge) return;
    if (count > 0) {
        badge.textContent = count;
        badge.style.display = "flex";
    } else {
        badge.style.display = "none";
    }
}

function getCartCount() {
    return parseInt(localStorage.getItem("cart_count") || "0");
}

function setCartCount(count) {
    localStorage.setItem("cart_count", count);
    updateCartBadge(count);
}
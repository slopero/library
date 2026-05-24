// ─────────────────────────────────────────────
// index.js — логика главной страницы.
// Отвечает за:
//   - получение книг с бэка
//   - отрисовку карточек
//   - фильтры и поиск
//   - пагинацию
//   - добавление в корзину и избранное
// ─────────────────────────────────────────────

// Текущее состояние страницы — все параметры запроса в одном объекте.
// Когда что-то меняется (фильтр, поиск, страница) — обновляем нужное
// поле и вызываем loadBooks() заново.
const state = {
    page:      1,
    search:    "",
    genre:     "",
    language:  "",
    year_from: "",
    year_to:   "",
    sort:      "title",
};


// ── Загрузка книг ─────────────────────────────

/**
 * Основная функция — строит URL с параметрами и запрашивает книги у бэка.
 */
async function loadBooks() {
    showSpinner();

    try {
        // Собираем параметры запроса — берём только непустые значения
        const params = new URLSearchParams();
        params.set("page", state.page);
        params.set("sort", state.sort);
        if (state.search)    params.set("search",    state.search);
        if (state.genre)     params.set("genre",     state.genre);
        if (state.language)  params.set("language",  state.language);
        if (state.year_from) params.set("year_from", state.year_from);
        if (state.year_to)   params.set("year_to",   state.year_to);

        // apiFetch из auth.js — автоматически подставляет API_URL и токен
        const data = await apiFetch(`/books/?${params.toString()}`);

        renderBooks(data.items);
        renderPagination(data.page, data.pages, data.total);

    } catch (err) {
        showError(err.message);
    }
}


// ── Отрисовка карточек ────────────────────────

const COLORS = ["c1", "c2", "c3", "c4", "c5", "c6", "c7", "c8"];

/**
 * Выбрать цвет обложки на основе id книги.
 * Один и тот же id всегда даёт один и тот же цвет.
 */
function pickColor(id) {
    return COLORS[id % COLORS.length];
}

/**
 * Отрисовать список карточек книг в сетку.
 */
function renderBooks(books) {
    const grid = document.getElementById("books-grid");

    if (books.length === 0) {
        grid.innerHTML = `
            <div class="empty-state" style="grid-column: 1 / -1">
                <div class="empty-state__icon">📚</div>
                <div class="empty-state__text">Книги не найдены</div>
                <div class="empty-state__sub">Попробуйте изменить параметры поиска</div>
            </div>`;
        return;
    }

    grid.innerHTML = books.map(book => {
        const color   = pickColor(book.id);
        // Проверяем есть ли книга в избранном (храним список id в localStorage)
        const favList = getFavoriteIds();
        const isFav   = favList.includes(book.id);

        return `
        <div class="book-card" onclick="goToBook(${book.id})">
            <div class="book-card__cover book-card__cover--${color}">
                <span style="opacity:0.2; font-size:48px">📖</span>
                <button
                    class="book-card__fav-btn ${isFav ? "book-card__fav-btn--active" : ""}"
                    onclick="toggleFavorite(event, ${book.id})"
                    title="${isFav ? "Убрать из избранного" : "В избранное"}"
                >${isFav ? "♥" : "♡"}</button>
                <div class="book-card__cover-title">${escapeHtml(book.title)}</div>
            </div>
            <div class="book-card__body">
                <div class="book-card__title">${escapeHtml(book.title)}</div>
                <div class="book-card__author">${escapeHtml(book.authors)}, ${book.year}</div>
                <div class="book-card__price">${formatPrice(book.price)} ₽</div>
                <button
                    class="book-card__cart-btn"
                    onclick="addToCart(event, ${book.id})"
                >+ В корзину</button>
            </div>
        </div>`;
    }).join("");
}


// ── Пагинация ─────────────────────────────────

/**
 * Отрисовать кнопки пагинации и строку с информацией о результатах.
 */
function renderPagination(page, pages, total) {
    // Обновляем строку "Показано N книг"
    document.getElementById("results-info").textContent =
        `Найдено: ${total} ${declension(total, "книга", "книги", "книг")}`;

    const container = document.getElementById("pagination");
    if (pages <= 1) { container.innerHTML = ""; return; }

    let html = "";

    // Кнопка "назад"
    html += `<button class="pagination__btn" ${page === 1 ? "disabled" : ""}
        onclick="changePage(${page - 1})">‹</button>`;

    // Номера страниц — показываем не все, а только вокруг текущей
    for (let i = 1; i <= pages; i++) {
        // Показываем первую, последнюю и страницы вокруг текущей
        if (i === 1 || i === pages || (i >= page - 2 && i <= page + 2)) {
            html += `<button class="pagination__btn ${i === page ? "pagination__btn--active" : ""}"
                onclick="changePage(${i})">${i}</button>`;
        } else if (i === page - 3 || i === page + 3) {
            // Многоточие когда страниц много
            html += `<span style="color: var(--text-muted); padding: 0 4px">…</span>`;
        }
    }

    // Кнопка "вперёд"
    html += `<button class="pagination__btn" ${page === pages ? "disabled" : ""}
        onclick="changePage(${page + 1})">›</button>`;

    container.innerHTML = html;
}

function changePage(page) {
    state.page = page;
    // Прокручиваем наверх при смене страницы
    window.scrollTo({ top: 0, behavior: "smooth" });
    loadBooks();
}


// ── Поиск и фильтры ───────────────────────────

// Задержка поиска — чтобы не отправлять запрос при каждом введённом символе.
// Пользователь печатает, и только через 400мс после последнего символа
// отправляется запрос. Это называется debounce.
let searchTimer = null;

function onSearchInput(value) {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => {
        state.search = value.trim();
        state.page = 1;
        loadBooks();
    }, 400);
}

function onFilterChange() {
    state.genre    = document.getElementById("filter-genre").value.trim();
    state.language = document.getElementById("filter-language").value;
    state.year_from = document.getElementById("filter-year-from").value;
    state.year_to   = document.getElementById("filter-year-to").value;
    state.page = 1;
    loadBooks();
}

function onSortChange(value) {
    state.sort = value;
    state.page = 1;
    loadBooks();
}

function resetFilters() {
    state.search   = "";
    state.genre    = "";
    state.language = "";
    state.year_from = "";
    state.year_to   = "";
    state.page     = 1;

    document.getElementById("search-input").value     = "";
    document.getElementById("filter-genre").value     = "";
    document.getElementById("filter-language").value  = "";
    document.getElementById("filter-year-from").value = "";
    document.getElementById("filter-year-to").value   = "";

    loadBooks();
}


// ── Корзина ───────────────────────────────────

async function addToCart(event, bookId) {
    // stopPropagation — чтобы клик по кнопке не открывал страницу книги
    event.stopPropagation();

    if (!isLoggedIn()) {
        window.location.href = "login.html";
        return;
    }

    try {
        await apiFetch("/cart/", {
            method: "POST",
            body: JSON.stringify({ book_id: bookId }),
        });

        // Обновляем счётчик корзины в шапке
        setCartCount(getCartCount() + 1);

        // Визуальная обратная связь — меняем кнопку
        const btn = event.target;
        btn.textContent = "✓ Добавлено";
        btn.classList.add("book-card__cart-btn--added");
        btn.disabled = true;

    } catch (err) {
        alert(err.message);
    }
}


// ── Избранное ─────────────────────────────────

// Список id книг в избранном храним локально для быстрой проверки
function getFavoriteIds() {
    return JSON.parse(localStorage.getItem("favorites") || "[]");
}

function setFavoriteIds(ids) {
    localStorage.setItem("favorites", JSON.stringify(ids));
}

async function toggleFavorite(event, bookId) {
    event.stopPropagation();

    if (!isLoggedIn()) {
        window.location.href = "login.html";
        return;
    }

    const btn    = event.target;
    const favIds = getFavoriteIds();
    const isFav  = favIds.includes(bookId);

    try {
        if (isFav) {
            await apiFetch(`/favorites/${bookId}`, { method: "DELETE" });
            setFavoriteIds(favIds.filter(id => id !== bookId));
            btn.textContent = "♡";
            btn.classList.remove("book-card__fav-btn--active");
        } else {
            await apiFetch("/favorites/", {
                method: "POST",
                body: JSON.stringify({ book_id: bookId }),
            });
            setFavoriteIds([...favIds, bookId]);
            btn.textContent = "♥";
            btn.classList.add("book-card__fav-btn--active");
        }
    } catch (err) {
        alert(err.message);
    }
}


// ── Навигация ─────────────────────────────────

function goToBook(bookId) {
    window.location.href = `book.html?id=${bookId}`;
}


// ── Вспомогательные функции ───────────────────

function showSpinner() {
    document.getElementById("books-grid").innerHTML =
        `<div class="spinner" style="grid-column: 1 / -1"><div class="spinner__circle"></div></div>`;
    document.getElementById("pagination").innerHTML = "";
}

function showError(message) {
    document.getElementById("books-grid").innerHTML =
        `<div class="error-message" style="grid-column: 1 / -1">⚠️ ${message}</div>`;
}

// Защита от XSS — экранируем спецсимволы HTML перед вставкой в DOM.
// Без этого злоумышленник мог бы вставить в название книги
// тег <script> и выполнить произвольный JS код.
function escapeHtml(str) {
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
}

function formatPrice(price) {
    return Number(price).toLocaleString("ru-RU");
}

// Правильные окончания для числительных
function declension(n, one, few, many) {
    const mod10  = n % 10;
    const mod100 = n % 100;
    if (mod10 === 1 && mod100 !== 11) return `${n} ${one}`;
    if ([2,3,4].includes(mod10) && ![12,13,14].includes(mod100)) return `${n} ${few}`;
    return `${n} ${many}`;
}


// ── Запуск ────────────────────────────────────

document.addEventListener("DOMContentLoaded", () => {
    updateCartBadge(getCartCount());
    loadBooks();
});
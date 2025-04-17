const API_URL = 'http://localhost:5000';
let authToken = localStorage.getItem('token') || '';

async function makeRequest(endpoint, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
            'Authorization': authToken ? `Bearer ${authToken}` : ''
        }
    };

    if (data) options.body = JSON.stringify(data);

    try {
        const response = await fetch(`${API_URL}${endpoint}`, options);
        const result = await response.json();

        if (endpoint === '/login' && result.token) {
            authToken = result.token;
            localStorage.setItem('token', authToken);
        }

        if (endpoint === '/logout') {
            authToken = '';
            localStorage.removeItem('token');
        }

        return result;
    } catch (error) {
        console.error('Ошибка:', error);
        return { error: error.message };
    }
}

// Товары
async function createProducts() {
    const result = await makeRequest('/create_products', 'POST');
    document.getElementById('products-output').innerHTML = formatOutput(result);
}

async function getProducts() {
    const result = await makeRequest('/products');
    document.getElementById('products-output').innerHTML = formatOutput(result);
}

// Пользователи
async function registerUser() {
    const result = await makeRequest('/register', 'POST', {
        username: 'testuser',
        email: 'test@example.com',
        password: 'test123'
    });
    document.getElementById('auth-output').innerHTML = formatOutput(result);
}

async function loginUser() {
    const result = await makeRequest('/login', 'POST', {
        email: 'test@example.com',
        password: 'test123'
    });
    document.getElementById('auth-output').innerHTML = formatOutput(result);
}

async function getProfile() {
    const result = await makeRequest('/profile');
    document.getElementById('auth-output').innerHTML = formatOutput(result);
}

async function logoutUser() {
    const result = await makeRequest('/logout', 'POST');
    document.getElementById('auth-output').innerHTML = formatOutput(result);
}

// Корзина
async function addToCart(productId) {
    const result = await makeRequest('/cart/add', 'POST', { product_id: productId });
    document.getElementById('cart-output').innerHTML = formatOutput(result);
}

async function viewCart() {
    const result = await makeRequest('/cart');
    document.getElementById('cart-output').innerHTML = formatOutput(result);
}

// Заказы
async function createOrder() {
    const result = await makeRequest('/order', 'POST');
    document.getElementById('orders-output').innerHTML = formatOutput(result);
}

async function getOrders() {
    const result = await makeRequest('/orders');
    document.getElementById('orders-output').innerHTML = formatOutput(result);
}

// Вспомогательная функция
function formatOutput(data) {
    return `<pre>${JSON.stringify(data, null, 2)}</pre>`;
}
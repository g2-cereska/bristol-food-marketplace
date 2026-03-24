const categoriesEl = document.getElementById("categories");
const productsEl = document.getElementById("products");
const categoryTitleEl = document.getElementById("current-category-title");
const searchEl = document.getElementById("search");

const cartItemsEl = document.getElementById("cart-items");
const cartTotalEl = document.getElementById("cart-total");
const checkoutBtn = document.getElementById("checkout-btn");
const clearCartBtn = document.getElementById("clear-cart-btn");
const checkoutMessageEl = document.getElementById("checkout-message");

let categories = [];
let currentCategoryId = null;
let currentProducts = [];
let cart = [];

function addToCart(product, quantity) {
    const qty = parseInt(quantity, 10);

    if (!qty || qty < 1) {
        alert("Please enter a valid quantity.");
        return;
    }

    const existing = cart.find(item => item.product_id === product.id);

    if (existing) {
        existing.quantity += qty;
    } else {
        cart.push({
            product_id: product.id,
            name: product.name,
            price: parseFloat(product.price),
            quantity: qty,
        });
    }

    renderCart();
}

function removeFromCart(productId) {
    cart = cart.filter(item => item.product_id !== productId);
    renderCart();
}

function clearCart() {
    cart = [];
    renderCart();
    checkoutMessageEl.textContent = "";
}

function renderCart() {
    cartItemsEl.innerHTML = "";

    if (cart.length === 0) {
        cartItemsEl.innerHTML = `<div class="empty">Your cart is empty.</div>`;
        cartTotalEl.textContent = "0.00";
        return;
    }

    let total = 0;

    cart.forEach(item => {
        const lineTotal = item.price * item.quantity;
        total += lineTotal;

        const div = document.createElement("div");
        div.className = "cart-item";
        div.innerHTML = `
            <strong>${item.name}</strong><br>
            Qty: ${item.quantity} × £${item.price.toFixed(2)}<br>
            Line total: £${lineTotal.toFixed(2)}<br>
            <button class="small-button remove-btn" data-id="${item.product_id}">Remove</button>
        `;
        cartItemsEl.appendChild(div);
    });

    cartTotalEl.textContent = total.toFixed(2);

    cartItemsEl.querySelectorAll(".remove-btn").forEach(button => {
        button.addEventListener("click", () => {
            removeFromCart(parseInt(button.dataset.id, 10));
        });
    });
}

function renderCategories() {
    categoriesEl.innerHTML = "";

    const allItem = document.createElement("li");
    allItem.textContent = "All";
    allItem.classList.toggle("active", currentCategoryId === null);
    allItem.addEventListener("click", async () => {
        currentCategoryId = null;
        categoryTitleEl.textContent = "All Products";
        searchEl.value = "";
        renderCategories();
        await loadProducts();
    });
    categoriesEl.appendChild(allItem);

    categories.forEach(category => {
        const li = document.createElement("li");
        li.textContent = category.name;
        li.classList.toggle("active", currentCategoryId === category.id);

        li.addEventListener("click", async () => {
            currentCategoryId = category.id;
            categoryTitleEl.textContent = category.name;
            searchEl.value = "";
            renderCategories();
            await loadProducts(category.id);
        });

        categoriesEl.appendChild(li);
    });
}

function renderProducts(products) {
    const searchText = searchEl.value.trim().toLowerCase();

    const filtered = products.filter(product => {
        const name = (product.name || "").toLowerCase();
        const desc = (product.description || "").toLowerCase();
        return name.includes(searchText) || desc.includes(searchText);
    });

    productsEl.innerHTML = "";

    const info = document.createElement("div");
    info.className = "muted";
    info.style.marginBottom = "1rem";
    info.textContent = `Loaded ${products.length} product(s), showing ${filtered.length}.`;
    productsEl.appendChild(info);

    if (filtered.length === 0) {
        const empty = document.createElement("div");
        empty.className = "empty";
        empty.textContent = "No products found.";
        productsEl.appendChild(empty);
        return;
    }

    filtered.forEach(product => {
        const card = document.createElement("div");
        card.className = "product-card";

        const availableClass = product.is_available ? "available" : "unavailable";
        const availableText = product.is_available ? "Available" : "Unavailable";

        card.innerHTML = `
            <h3>${product.name}</h3>
            <p class="muted">${product.description || "No description provided."}</p>
            <p><strong>Price:</strong> £${product.price}</p>
            <p><strong>Stock:</strong> ${product.total_stock}</p>
            <p><strong>Producer:</strong> ${product.producer?.name || "Unknown"}</p>
            <p><strong>Category:</strong> ${product.category?.name || "Uncategorised"}</p>
            <span class="badge ${availableClass}">${availableText}</span>
            <div style="margin-top: 1rem;">
                <input
                    type="number"
                    min="1"
                    value="1"
                    class="quantity-input"
                    id="qty-${product.id}"
                    ${product.is_available ? "" : "disabled"}
                >
                <button
                    class="button add-to-cart-btn"
                    data-id="${product.id}"
                    ${product.is_available ? "" : "disabled"}
                >
                    Add to Cart
                </button>
            </div>
        `;

        productsEl.appendChild(card);
    });

    document.querySelectorAll(".add-to-cart-btn").forEach(button => {
        button.addEventListener("click", () => {
            const productId = parseInt(button.dataset.id, 10);
            const product = currentProducts.find(p => p.id === productId);
            const qtyInput = document.getElementById(`qty-${productId}`);
            addToCart(product, qtyInput.value);
        });
    });
}

async function loadCategories() {
    categoriesEl.innerHTML = `<li class="loading">Loading categories...</li>`;

    try {
        const response = await fetch("/api/categories/");
        if (!response.ok) {
            throw new Error(`Failed to load categories: ${response.status}`);
        }

        categories = await response.json();
        renderCategories();
    } catch (error) {
        categoriesEl.innerHTML = `<li class="empty">Could not load categories.</li>`;
        console.error(error);
    }
}

async function loadProducts(categoryId = null) {
    productsEl.innerHTML = `<p class="loading">Loading products...</p>`;

    try {
        let url = "/api/products/";
        if (categoryId !== null) {
            url += `?category=${encodeURIComponent(categoryId)}`;
        }

        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`Failed to load products: ${response.status}`);
        }

        const data = await response.json();

        if (!Array.isArray(data)) {
            throw new Error("Products response is not an array.");
        }

        currentProducts = data;
        renderProducts(currentProducts);
    } catch (error) {
        productsEl.innerHTML = `<div class="empty">Could not load products.</div>`;
        console.error(error);
    }
}

async function checkout() {
    if (cart.length === 0) {
        checkoutMessageEl.textContent = "Your cart is empty.";
        return;
    }

    checkoutBtn.disabled = true;
    checkoutMessageEl.textContent = "Submitting order...";

    const payload = {
        items: cart.map(item => ({
            product_id: item.product_id,
            quantity: item.quantity,
        }))
    };

    try {
        const response = await fetch("/api/orders/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(payload),
        });

        const data = await response.json();

        if (!response.ok) {
            checkoutMessageEl.textContent = data.detail || JSON.stringify(data);
            return;
        }

        clearCart();
        checkoutMessageEl.textContent = `Order #${data.id} created successfully.`;

        if (currentCategoryId !== null) {
            await loadProducts(currentCategoryId);
        } else {
            await loadProducts();
        }
    } catch (error) {
        console.error(error);
        checkoutMessageEl.textContent = "Checkout failed. Please try again.";
    } finally {
        checkoutBtn.disabled = false;
    }
}

checkoutBtn.addEventListener("click", checkout);
clearCartBtn.addEventListener("click", clearCart);

searchEl.addEventListener("input", () => {
    renderProducts(currentProducts);
});

async function init() {
    renderCart();
    await loadCategories();
    await loadProducts();
}

init();
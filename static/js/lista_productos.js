// static/js/lista_productos.js

// ============================================================
// FAVORITOS
// ============================================================
function getFavorites() {
    try {
        return JSON.parse(localStorage.getItem('angelow_favorites') || '[]');
    } catch (e) {
        return [];
    }
}

function saveFavorites(favs) {
    localStorage.setItem('angelow_favorites', JSON.stringify(favs));
    updateFavBadge();
}

function updateFavBadge() {
    var favs = getFavorites();
    var badge = document.getElementById('favBadgeHeader');
    if (badge) {
        badge.textContent = favs.length;
        badge.style.display = favs.length > 0 ? 'flex' : 'none';
    }
}

function toggleFavorite(productId, event) {
    if (event) {
        event.stopPropagation();
    }
    
    var favs = getFavorites();
    var index = favs.indexOf(productId);
    var btn = document.querySelector('.product-card .btn-fav[data-id="' + productId + '"]');
    
    if (index > -1) {
        favs.splice(index, 1);
        if (btn) {
            btn.classList.remove('active');
            var icon = btn.querySelector('i');
            if (icon) icon.style.color = '';
        }
        showToast('Eliminado de favoritos', 'info');
    } else {
        favs.push(productId);
        if (btn) {
            btn.classList.add('active');
            var icon = btn.querySelector('i');
            if (icon) icon.style.color = '#ef4444';
        }
        showToast('Agregado a favoritos ', 'success');
    }
    saveFavorites(favs);
    updateHeaderBadges();
    window.dispatchEvent(new Event('storage'));
}

// ============================================================
// CARRITO
// ============================================================
function getCart() {
    try {
        return JSON.parse(localStorage.getItem('angelow_cart') || '[]');
    } catch (e) {
        return [];
    }
}

function saveCart(cart) {
    localStorage.setItem('angelow_cart', JSON.stringify(cart));
    updateCartBadge();
}

function updateCartBadge() {
    var cart = getCart();
    var total = 0;
    for (var i = 0; i < cart.length; i++) {
        total = total + (cart[i].quantity || 1);
    }
    var badge = document.getElementById('cartBadgeHeader');
    if (badge) {
        badge.textContent = total;
        badge.style.display = total > 0 ? 'flex' : 'none';
    }
}

function addToCart(productId, event) {
    if (event) {
        event.stopPropagation();
    }
    
    var card = document.querySelector('.product-card[data-id="' + productId + '"]');
    if (!card) {
        showToast('Producto no encontrado', 'error');
        return;
    }
    
    var nameEl = card.querySelector('.product-name');
    var priceEl = card.querySelector('.product-price');
    var imgEl = card.querySelector('.product-card-img');
    
    var name = nameEl ? nameEl.textContent : 'Producto';
    var priceText = priceEl ? priceEl.textContent.replace(/[^0-9.]/g, '') : '0';
    var price = parseFloat(priceText) || 0;
    var imagen = imgEl ? imgEl.src : '';
    
    var cart = getCart();
    var existing = null;
    for (var i = 0; i < cart.length; i++) {
        if (cart[i].id === productId) {
            existing = cart[i];
            break;
        }
    }
    
    if (existing) {
        existing.quantity = (existing.quantity || 1) + 1;
    } else {
        cart.push({
            id: productId,
            name: name,
            price: price,
            quantity: 1,
            imagen: imagen
        });
    }
    
    saveCart(cart);
    showToast(name + ' agregado al carrito 🛒', 'success');
    updateHeaderBadges();
}

// ============================================================
// TOAST NOTIFICATIONS
// ============================================================
function showToast(message, type) {
    type = type || 'info';
    var container = document.getElementById('toastContainer');
    if (!container) {
        // Crear container si no existe
        container = document.createElement('div');
        container.id = 'toastContainer';
        container.style.cssText = 'position: fixed; top: 80px; right: 20px; z-index: 9999; display: flex; flex-direction: column; gap: 10px;';
        document.body.appendChild(container);
    }
    
    var colors = {
        success: '#10b981',
        error: '#ef4444',
        warning: '#f59e0b',
        info: '#5E9DE6'
    };
    
    var icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };
    
    var toast = document.createElement('div');
    toast.style.cssText = 'background: white; border-radius: 12px; padding: 14px 20px; box-shadow: 0 8px 25px rgba(0,0,0,0.15); display: flex; align-items: center; gap: 12px; border-left: 4px solid ' + (colors[type] || colors.info) + '; animation: slideIn 0.3s ease; min-width: 260px; max-width: 380px;';
    toast.innerHTML = '<i class="fas ' + (icons[type] || icons.info) + '" style="color: ' + (colors[type] || colors.info) + '; font-size: 18px;"></i><span style="color: #1E3A8A; font-size: 14px; font-weight: 500;">' + message + '</span><button onclick="this.parentElement.remove()" style="background:none; border:none; font-size:18px; cursor:pointer; color:#94a3b8; margin-left:auto;">×</button>';
    
    container.appendChild(toast);
    setTimeout(function() { toast.remove(); }, 3500);
}

// ============================================================
// INICIALIZACIÓN
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
    var favs = getFavorites();
    for (var i = 0; i < favs.length; i++) {
        var btn = document.querySelector('.product-card .btn-fav[data-id="' + favs[i] + '"]');
        if (btn) {
            btn.classList.add('active');
            var icon = btn.querySelector('i');
            if (icon) icon.style.color = '#ef4444';
        }
    }
    updateCartBadge();
});
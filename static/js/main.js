// static/js/main.js

// ============================================================
// FUNCIONES GLOBALES COMUNES
// ============================================================

// Actualizar badges del header desde localStorage
function updateHeaderBadges() {
    try {
        var favs = JSON.parse(localStorage.getItem('angelow_favorites') || '[]');
        var count = favs.length;
        
        var favBadge = document.getElementById('favBadgeHeader');
        if (favBadge) {
            favBadge.textContent = count;
            favBadge.style.display = count > 0 ? 'flex' : 'none';
        }
        
        var favBadgeDropdown = document.getElementById('favBadgeDropdown');
        if (favBadgeDropdown) {
            favBadgeDropdown.textContent = count;
            favBadgeDropdown.style.display = count > 0 ? 'inline' : 'none';
        }
    } catch(e) {}
    
    try {
        var cart = JSON.parse(localStorage.getItem('angelow_cart') || '[]');
        var total = 0;
        for (var i = 0; i < cart.length; i++) {
            total = total + (cart[i].quantity || 1);
        }
        var cartBadge = document.getElementById('cartBadgeHeader');
        if (cartBadge) {
            cartBadge.textContent = total;
            cartBadge.style.display = total > 0 ? 'flex' : 'none';
        }
    } catch(e) {}
}

// ============================================================
// INICIALIZACIÓN GLOBAL
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
    updateHeaderBadges();
});

// Escuchar cambios en localStorage desde otras pestañas
window.addEventListener('storage', function(e) {
    if (e.key === 'angelow_favorites' || e.key === 'angelow_cart') {
        updateHeaderBadges();
    }
});
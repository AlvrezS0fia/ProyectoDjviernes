// static/js/main.js

// ============================================================
// FUNCIONES GLOBALES COMUNES
// ============================================================

// Actualizar badges del header desde localStorage
function updateHeaderBadges(count) {
    try {
        var favCount = count !== undefined ? count : JSON.parse(localStorage.getItem('angelow_favorites') || '[]').length;
        
        var favBadge = document.getElementById('favBadgeHeader');
        if (favBadge) {
            favBadge.textContent = favCount;
            favBadge.style.display = favCount > 0 ? 'flex' : 'none';
        }
        
        var favBadgeDropdown = document.getElementById('favBadgeDropdown');
        if (favBadgeDropdown) {
            favBadgeDropdown.textContent = favCount;
            favBadgeDropdown.style.display = favCount > 0 ? 'inline' : 'none';
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
// static/js/favorites.js

// ============================================================
// PRODUCTOS (inyectados desde Django)
// ============================================================
var allProducts = [];

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
    var count = favs.length;
    var badge = document.getElementById('favBadgeHeader');
    if (badge) {
        badge.textContent = count;
        badge.style.display = count > 0 ? 'flex' : 'none';
    }
    var favCount = document.getElementById('favCount');
    if (favCount) {
        favCount.textContent = count + ' productos';
    }
}

function removeFavorite(productId) {
    if (confirm('¿Quieres eliminar este producto de tus favoritos?')) {
        var favs = getFavorites();
        var index = favs.indexOf(productId);
        if (index > -1) {
            favs.splice(index, 1);
            saveFavorites(favs);
            renderFavorites();
            showToast('Eliminado de favoritos', 'info');
        }
    }
}

function renderFavorites() {
    var favs = getFavorites();
    var grid = document.getElementById('favoritesGrid');
    var empty = document.getElementById('emptyFavorites');
    
    if (favs.length === 0) {
        grid.innerHTML = '';
        grid.classList.add('d-none');
        empty.classList.remove('d-none');
        updateFavBadge();
        return;
    }
    
    grid.classList.remove('d-none');
    empty.classList.add('d-none');
    
    var html = '';
    var count = 0;
    for (var i = 0; i < allProducts.length; i++) {
        var p = allProducts[i];
        if (favs.indexOf(p.id) !== -1) {
            count++;
            var stockClass = p.stock > 10 ? 'text-success' : (p.stock > 0 ? 'text-warning' : 'text-danger');
            var stockText = p.stock > 10 ? 'En stock' : (p.stock > 0 ? 'Últimas unidades' : 'Sin stock');
            
            html += '<div class="col-lg-3 col-md-4 col-6">';
            html += '<div class="card h-100 shadow-sm product-card" onclick="window.location.href=\'/tienda/producto/' + p.slug + '/\'">';
            html += '<div class="card-img-top" style="height: 180px; overflow: hidden; background: #EDF4FC; position: relative;">';
            html += '<img src="' + p.imagen + '" class="img-fluid w-100 h-100" style="object-fit: cover;" alt="' + p.nombre + '" loading="lazy">';
            html += '<span class="badge bg-danger position-absolute top-0 end-0 m-2" style="background: #FF6B6B !important;"><i class="fas fa-heart"></i></span>';
            html += '</div>';
            html += '<div class="card-body">';
            html += '<h6 class="card-title text-truncate" style="font-weight: 600; color: #1E3A8A;">' + p.nombre + '</h6>';
            html += '<p class="card-text text-muted small">' + p.categoria + '</p>';
            html += '<div class="d-flex justify-content-between align-items-center">';
            html += '<span class="fw-bold" style="color: #5E9DE6; font-size: 18px;">$' + p.precio.toLocaleString() + '</span>';
            html += '<button class="btn btn-sm btn-outline-danger btn-remove-fav" onclick="event.stopPropagation(); removeFavorite(' + p.id + ')" data-product-id="' + p.id + '"><i class="fas fa-trash-alt"></i></button>';
            html += '</div>';
            html += '<div class="mt-2 small ' + stockClass + '"><i class="fas fa-circle" style="font-size: 8px;"></i> ' + stockText + '</div>';
            html += '</div>';
            html += '</div>';
            html += '</div>';
        }
    }
    
    grid.innerHTML = html;
    updateFavBadge(count);
}

// ============================================================
// TOAST NOTIFICATIONS
// ============================================================
function showToast(message, type) {
    type = type || 'info';
    var container = document.getElementById('toastContainer');
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
    renderFavorites();
    updateFavBadge();
});
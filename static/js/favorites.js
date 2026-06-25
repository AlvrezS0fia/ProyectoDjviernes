// static/js/favorites.js

// Variable global para almacenar productos
var allProducts = [];

function loadFavorites() {
    console.log('=== loadFavorites() ejecutado ===');
    console.log('allProducts:', allProducts);
    
    var favorites = JSON.parse(localStorage.getItem('angelow_favorites') || '[]');
    console.log('Favoritos desde localStorage:', favorites);
    
    var grid = document.getElementById('favoritesGrid');
    var empty = document.getElementById('emptyFavorites');
    var countSpan = document.getElementById('favCount');

    if (countSpan) {
        countSpan.textContent = favorites.length;
    }

    // Si no hay favoritos, mostrar estado vacío
    if (favorites.length === 0) {
        console.log('No hay favoritos');
        if (grid) {
            grid.innerHTML = '';
            grid.classList.add('d-none');
        }
        if (empty) {
            empty.classList.remove('d-none');
        }
        return;
    }

    // Ocultar estado vacío
    if (grid) {
        grid.classList.remove('d-none');
    }
    if (empty) {
        empty.classList.add('d-none');
    }

    // Filtrar productos que están en favoritos
    var favProducts = allProducts.filter(function(p) {
        return favorites.includes(p.id);
    });
    
    console.log('Productos favoritos encontrados:', favProducts.length);

    if (favProducts.length === 0) {
        console.log('No se encontraron productos favoritos en la lista de productos');
        if (grid) {
            grid.innerHTML = '';
            grid.classList.add('d-none');
        }
        if (empty) {
            empty.classList.remove('d-none');
        }
        return;
    }

    // Generar HTML
    var html = '';
    for (var i = 0; i < favProducts.length; i++) {
        var product = favProducts[i];
        var price = product.precio_oferta || product.precio;
        var oldPrice = product.precio_oferta ? product.precio : null;
        
        var stockHtml = '';
        if (product.stock > 10) {
            stockHtml = '<span class="in-stock"><i class="fas fa-check-circle"></i> En stock</span>';
        } else if (product.stock > 0) {
            stockHtml = '<span class="low-stock"><i class="fas fa-exclamation-circle"></i> Solo ' + product.stock + ' unidades</span>';
        } else {
            stockHtml = '<span class="out-of-stock"><i class="fas fa-times-circle"></i> Sin stock</span>';
        }

        var oldPriceHtml = oldPrice ? '<span class="old-price">$' + oldPrice.toLocaleString() + '</span>' : '';

        html += '<div class="fav-product-card" data-id="' + product.id + '" style="animation-delay: ' + (i * 0.05) + 's">';
        html += '<img src="' + product.imagen + '" class="card-img-top" alt="' + product.nombre + '" loading="lazy" onerror="this.src=\'/static/img/productos/default.jpg\'">';
        html += '<div class="card-body">';
        html += '<h3 class="product-name">' + product.nombre + '</h3>';
        html += '<p class="product-category">' + product.categoria + '</p>';
        html += '<div class="product-price">' + oldPriceHtml + '$' + price.toLocaleString() + '</div>';
        html += '<div class="product-stock">' + stockHtml + '</div>';
        html += '<div class="card-actions">';
        html += '<button class="btn-cart" onclick="addToCart(' + product.id + ', event)" ' + (product.stock === 0 ? 'disabled' : '') + '>';
        html += '<i class="fas fa-shopping-cart"></i> Agregar';
        html += '</button>';
        html += '<button class="btn-remove-fav" onclick="removeFavorite(' + product.id + ', \'' + product.nombre + '\', event)" title="Quitar de favoritos">';
        html += '<i class="fas fa-heart-broken"></i>';
        html += '<span class="remove-text">Quitar</span>';
        html += '</button>';
        html += '</div>';
        html += '<div style="position:absolute; inset:0; cursor:pointer; z-index:1;" onclick="window.location.href=\'/tienda/producto/' + product.slug + '/\'"></div>';
        html += '</div>';
        html += '</div>';
    }
    
    console.log('HTML generado, insertando en grid...');
    grid.innerHTML = html;
    console.log('Favoritos cargados correctamente');
}

function removeFavorite(productId, productName, event) {
    if (event) event.stopPropagation();

    var card = event.target.closest('.fav-product-card');
    var btn = event.target.closest('.btn-remove-fav');

    if (btn) {
        btn.classList.add('removing');
    }

    if (card) {
        card.classList.add('removing');
    }

    setTimeout(function() {
        var favorites = JSON.parse(localStorage.getItem('angelow_favorites') || '[]');
        var index = favorites.indexOf(productId);

        if (index !== -1) {
            favorites.splice(index, 1);
            localStorage.setItem('angelow_favorites', JSON.stringify(favorites));
        }

        var isAuthenticated = window.ANGELOW && window.ANGELOW.isAuthenticated;
        if (isAuthenticated) {
            fetch(window.ANGELOW.apiToggleFavorito, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({producto_id: productId}),
            })
            .then(function(response) { return response.json(); })
            .then(function(data) {
                if (data.success) {
                    showToast('success', 'fa-heart', '"' + productName + '" eliminado de favoritos');
                    loadFavorites();
                    updateHeaderBadges();
                    window.dispatchEvent(new Event('storage'));
                } else {
                    showToast('error', 'fa-exclamation-circle', data.message || 'Error');
                }
            })
            .catch(function() {
                showToast('error', 'fa-exclamation-circle', 'Error al eliminar favorito');
            });
        } else {
            showToast('success', 'fa-heart', '"' + productName + '" eliminado de favoritos');
            loadFavorites();
            updateHeaderBadges();
            window.dispatchEvent(new Event('storage'));
        }
    }, 400);
}

function addToCart(productId, event) {
    if (event) event.stopPropagation();
    showToast('success', 'fa-shopping-cart', 'Producto agregado al carrito');
}

function showToast(type, icon, message) {
    var container = document.getElementById('toastContainer');
    if (!container) return;
    
    var toast = document.createElement('div');
    toast.className = 'toast-item ' + type;
    toast.innerHTML = '<i class="fas ' + icon + '"></i><span style="flex:1;">' + message + '</span><button class="toast-close" onclick="this.parentElement.remove()">&times;</button>';
    
    container.appendChild(toast);
    
    setTimeout(function() {
        if (toast.parentElement) {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            toast.style.transition = 'all 0.3s ease';
            setTimeout(function() {
                if (toast.parentElement) toast.remove();
            }, 300);
        }
    }, 3000);
}

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
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    console.log('=== DOM cargado ===');
    
    var productosScript = document.getElementById('productos-data');
    if (productosScript) {
        console.log('Script productos-data encontrado');
        try {
            allProducts = JSON.parse(productosScript.textContent);
            console.log('Productos cargados correctamente:', allProducts.length);
        } catch(e) {
            console.error('Error parsing productos data:', e);
            allProducts = [];
        }
    } else {
        console.error('Script con id "productos-data" NO encontrado');
    }
    
    loadFavorites();
    updateHeaderBadges();
});

// Escuchar cambios desde otras pestañas
window.addEventListener('storage', function(e) {
    if (e.key === 'angelow_favorites') {
        console.log('Storage event detected: favoritos cambiados');
        loadFavorites();
        updateHeaderBadges();
    }
});
// static/js/favorites.js

// Variable global para almacenar productos
var allProducts = [];

// ============================================================
// INICIALIZACIÓN
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
    console.log('=== favorites.js inicializado ===');
    
    // Cargar datos de productos desde el script embebido
    var scriptElement = document.getElementById('productos-data');
    if (scriptElement) {
        try {
            allProducts = JSON.parse(scriptElement.textContent);
            console.log('Productos cargados:', allProducts.length);
        } catch(e) {
            console.error('Error al parsear JSON de productos:', e);
            allProducts = [];
        }
    }
    
    // Cargar favoritos
    loadFavorites();
});

// ============================================================
// CARGAR FAVORITOS
// ============================================================
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

    if (grid) {
        grid.classList.remove('d-none');
    }
    if (empty) {
        empty.classList.add('d-none');
    }

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
        html += '</div>';
        html += '</div>';
    }
    
    if (grid) {
        grid.innerHTML = html;
    }
}

// ============================================================
// ELIMINAR FAVORITO
// ============================================================
function removeFavorite(productId, productName, event) {
    if (event) {
        event.stopPropagation();
        event.preventDefault();
    }
    
    console.log('=== removeFavorite() ejecutado para:', productName, '===');
    
    var isAuthenticated = window.ANGELOW && window.ANGELOW.isAuthenticated;
    
    if (isAuthenticated) {
        // Usuario autenticado: usar API
        fetch(window.ANGELOW.apiToggleFavorito, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({producto_id: productId})
        })
        .then(function(response) {
            return response.json();
        })
        .then(function(data) {
            if (data.success) {
                var card = document.querySelector('.fav-product-card[data-id="' + productId + '"]');
                if (card) {
                    card.classList.add('removing');
                    setTimeout(function() {
                        card.remove();
                        updateFavCount();
                        checkEmptyState();
                    }, 400);
                }
                showToast('success', 'fa-heart-broken', '"' + productName + '" eliminado de favoritos');
                updateHeaderBadges();
                window.dispatchEvent(new Event('storage'));
            } else {
                showToast('error', 'fa-exclamation-circle', data.message || 'Error');
            }
        })
        .catch(function(error) {
            showToast('error', 'fa-exclamation-circle', 'Error al procesar favorito');
        });
    } else {
        // Usuario no autenticado: usar localStorage
        var favorites = JSON.parse(localStorage.getItem('angelow_favorites') || '[]');
        var index = favorites.indexOf(productId);
        
        if (index > -1) {
            favorites.splice(index, 1);
        }
        
        localStorage.setItem('angelow_favorites', JSON.stringify(favorites));
        
        var card = document.querySelector('.fav-product-card[data-id="' + productId + '"]');
        if (card) {
            card.classList.add('removing');
            setTimeout(function() {
                card.remove();
                updateFavCount();
                checkEmptyState();
            }, 400);
        }
        
        showToast('success', 'fa-heart-broken', '"' + productName + '" eliminado de favoritos');
        updateHeaderBadges();
        window.dispatchEvent(new Event('storage'));
    }
}

// ============================================================
// ACTUALIZAR CONTADOR DE FAVORITOS
// ============================================================
function updateFavCount() {
    var favorites = JSON.parse(localStorage.getItem('angelow_favorites') || '[]');
    var countSpan = document.getElementById('favCount');
    if (countSpan) {
        countSpan.textContent = favorites.length;
    }
}

// ============================================================
// VERIFICAR ESTADO VACÍO
// ============================================================
function checkEmptyState() {
    var grid = document.getElementById('favoritesGrid');
    var empty = document.getElementById('emptyFavorites');
    
    if (grid && grid.children.length === 0) {
        grid.classList.add('d-none');
        if (empty) {
            empty.classList.remove('d-none');
        }
    }
}

// ============================================================
// AGREGAR AL CARRITO
// ============================================================
function addToCart(productId, event) {
    if (event) {
        event.stopPropagation();
    }
    showToast('success', 'fa-shopping-cart', 'Producto agregado al carrito');
}

// ============================================================
// ACTUALIZAR BADGES DEL HEADER
// ============================================================
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

// ============================================================
// TOAST NOTIFICATIONS
// ============================================================
function showToast(type, icon, message) {
    var container = document.getElementById('toastContainer');
    if (!container) {
        // Crear container si no existe
        container = document.createElement('div');
        container.id = 'toastContainer';
        container.style.position = 'fixed';
        container.style.top = '80px';
        container.style.right = '20px';
        container.style.zIndex = '9999';
        container.style.display = 'flex';
        container.style.flexDirection = 'column';
        container.style.gap = '10px';
        document.body.appendChild(container);
    }
    
    var toast = document.createElement('div');
    toast.className = 'toast-item ' + type;
    toast.innerHTML = '<i class="fas ' + icon + '"></i><span style="flex:1;">' + message + '</span><button class="toast-close" onclick="this.parentElement.remove()">×</button>';
    
    container.appendChild(toast);
    
    setTimeout(function() {
        if (toast.parentNode) {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            toast.style.transition = 'all 0.3s ease';
            setTimeout(function() {
                if (toast.parentNode) toast.parentNode.removeChild(toast);
            }, 300);
        }
    }, 3000);
}

// ============================================================
// CLICK EN TARJETA - REDIRIGIR AL DETALLE
// ============================================================
document.addEventListener('click', function(e) {
    var card = e.target.closest('.fav-product-card');
    if (card && !e.target.closest('button')) {
        var productId = card.getAttribute('data-id');
        if (productId) {
            window.location.href = '/tienda/producto/' + productId + '/';
        }
    }
});
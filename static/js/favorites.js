// static/js/favorites.js

// ============================================================
// OBTENER FAVORITOS DEL SERVIDOR
// ============================================================
function getFavoritesFromServer(callback) {
    if (!window.ANGELOW || !window.ANGELOW.isAuthenticated) {
        if (callback) callback([]);
        return;
    }

    var url = window.ANGELOW.apiFavoritos;
    var csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    var token = csrfToken ? csrfToken.value : '';

    console.log('🔍 Obteniendo favoritos del servidor...', url);

    fetch(url, {
        method: 'GET',
        headers: {
            'X-CSRFToken': token,
            'Content-Type': 'application/json'
        }
    })
    .then(function(response) {
        if (!response.ok) {
            throw new Error('Error al obtener favoritos: ' + response.status);
        }
        return response.json();
    })
    .then(function(data) {
        console.log('📦 Datos recibidos del servidor:', data);
        if (data.success && data.favoritos !== undefined) {
            localStorage.setItem('angelow_favorites', JSON.stringify(data.favoritos));
            if (callback) callback(data.favoritos);
        } else {
            console.error('❌ Error en la respuesta:', data);
            if (callback) callback([]);
        }
    })
    .catch(function(error) {
        console.error('❌ Error al obtener favoritos:', error);
        if (callback) callback([]);
    });
}

// ============================================================
// GUARDAR FAVORITO EN EL SERVIDOR
// ============================================================
function saveFavoriteOnServer(productId, callback) {
    if (!window.ANGELOW || !window.ANGELOW.isAuthenticated) {
        if (callback) callback(true);
        return;
    }

    var url = window.ANGELOW.apiToggleFavorito;
    var csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    var token = csrfToken ? csrfToken.value : '';

    console.log('💾 Guardando favorito en el servidor...', url, productId);

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': token
        },
        body: JSON.stringify({
            producto_id: productId
        })
    })
    .then(function(response) {
        return response.json();
    })
    .then(function(data) {
        console.log('📦 Respuesta del servidor:', data);
        if (data.success) {
            if (callback) callback(true, data);
        } else {
            console.error('❌ Error del servidor:', data.message);
            if (callback) callback(false);
        }
    })
    .catch(function(error) {
        console.error('❌ Error en la petición:', error);
        if (callback) callback(false);
    });
}

// ============================================================
// TOGGLE FAVORITO
// ============================================================
function toggleFavorite(productId, productName, button) {
    console.log('🔄 Toggle favorito:', productId, productName);

    var favorites = JSON.parse(localStorage.getItem('angelow_favorites') || '[]');

    // Si el usuario está autenticado, guardar en el servidor
    if (window.ANGELOW && window.ANGELOW.isAuthenticated) {
        if (button) {
            button.disabled = true;
            button.style.opacity = '0.6';
        }

        saveFavoriteOnServer(productId, function(success, data) {
            if (success) {
                if (data && data.es_favorito !== undefined) {
                    if (data.es_favorito) {
                        if (favorites.indexOf(productId) === -1) {
                            favorites.push(productId);
                        }
                        showToast('success', 'fa-heart', '"' + productName + '" agregado a favoritos');
                        if (button) button.classList.add('active');
                        createHeartParticles(button);
                    } else {
                        var idx = favorites.indexOf(productId);
                        if (idx !== -1) {
                            favorites.splice(idx, 1);
                        }
                        showToast('success', 'fa-heart', '"' + productName + '" eliminado de favoritos');
                        if (button) {
                            button.classList.remove('active');
                            var card = button.closest('.fav-product-card');
                            if (card) {
                                card.classList.add('removing');
                                setTimeout(function() {
                                    card.remove();
                                    renderFavorites();
                                }, 400);
                            }
                        }
                    }
                }

                localStorage.setItem('angelow_favorites', JSON.stringify(favorites));

                if (button) {
                    var textSpan = button.querySelector('.fav-text');
                    if (textSpan) {
                        textSpan.textContent = button.classList.contains('active') ? 'Favorito' : 'Favoritos';
                    }
                    button.disabled = false;
                    button.style.opacity = '1';
                }

                updateHeaderBadges();
                window.dispatchEvent(new Event('storage'));
            } else {
                showToast('error', 'fa-exclamation-triangle', 'Error al procesar favorito');
                if (button) {
                    button.disabled = false;
                    button.style.opacity = '1';
                }
            }
        });
    } else {
        var isFavorite = favorites.indexOf(productId) !== -1;
        if (isFavorite) {
            favorites.splice(favorites.indexOf(productId), 1);
            showToast('success', 'fa-heart', '"' + productName + '" eliminado de favoritos');
            if (button) {
                button.classList.remove('active');
                var textSpan = button.querySelector('.fav-text');
                if (textSpan) {
                    textSpan.textContent = 'Favoritos';
                }
                var card = button.closest('.fav-product-card');
                if (card) {
                    card.classList.add('removing');
                    setTimeout(function() {
                        card.remove();
                        renderFavorites();
                    }, 400);
                }
            }
        } else {
            favorites.push(productId);
            showToast('success', 'fa-heart', '"' + productName + '" agregado a favoritos');
            if (button) button.classList.add('active');
            createHeartParticles(button);
        }

        localStorage.setItem('angelow_favorites', JSON.stringify(favorites));

        if (button) {
            var textSpan = button.querySelector('.fav-text');
            if (textSpan) {
                textSpan.textContent = button.classList.contains('active') ? 'Favorito' : 'Favoritos';
            }
        }

        updateHeaderBadges();
        window.dispatchEvent(new Event('storage'));
    }
}

// ============================================================
// PARTÍCULAS DE CORAZÓN
// ============================================================
function createHeartParticles(button) {
    if (!button) return;

    var rect = button.getBoundingClientRect();
    var centerX = rect.left + rect.width / 2;
    var centerY = rect.top + rect.height / 2;

    var emojis = ['❤️', '💖', '💗', '💕', '♥️'];

    for (var i = 0; i < 8; i++) {
        var particle = document.createElement('div');
        particle.className = 'particle-heart';
        particle.textContent = emojis[i % emojis.length];

        var angle = (Math.PI * 2 * i) / 8 + (Math.random() - 0.5) * 0.5;
        var distance = 60 + Math.random() * 40;
        var x = Math.cos(angle) * distance;
        var y = Math.sin(angle) * distance - 30;

        particle.style.position = 'fixed';
        particle.style.left = (centerX + x) + 'px';
        particle.style.top = (centerY + y) + 'px';
        particle.style.fontSize = (14 + Math.random() * 10) + 'px';
        particle.style.color = '#ef4444';
        particle.style.pointerEvents = 'none';
        particle.style.zIndex = '9999';
        particle.style.animation = 'particleFloat 0.8s ease-out forwards';

        document.body.appendChild(particle);

        setTimeout(function(p) {
            if (p.parentNode) p.parentNode.removeChild(p);
        }, 1000, particle);
    }
}

// ============================================================
// TOAST NOTIFICATIONS
// ============================================================
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

// ============================================================
// CARRITO
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
            favBadge.innerHTML = '<i class="fas fa-heart"></i> <span>' + count + '</span> productos';
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
// RENDERIZAR PRODUCTOS FAVORITOS
// ============================================================
function renderFavorites() {
    var grid = document.getElementById('favoritesGrid');
    var emptyState = document.getElementById('emptyFavorites');
    var favCountSpan = document.getElementById('favCount');
    
    if (!grid) return;
    
    var productsData = [];
    var scriptElement = document.getElementById('productos-data');
    
    if (scriptElement) {
        try {
            productsData = JSON.parse(scriptElement.textContent);
            console.log('📦 Productos favoritos cargados:', productsData.length);
        } catch(e) {
            console.error('❌ Error al parsear productos:', e);
        }
    }
    
    if (favCountSpan) {
        favCountSpan.textContent = productsData.length;
    }
    
    if (productsData.length === 0) {
        grid.innerHTML = '';
        if (emptyState) {
            emptyState.classList.remove('d-none');
        }
        return;
    }
    
    if (emptyState) {
        emptyState.classList.add('d-none');
    }

    var html = '';
    for (var i = 0; i < productsData.length; i++) {
        var p = productsData[i];
        var stockClass = p.stock > 10 ? 'in-stock' : (p.stock > 0 ? 'low-stock' : 'out-of-stock');
        var stockText = p.stock > 10 ? 'En stock' : (p.stock > 0 ? 'Solo ' + p.stock + ' unidades' : 'Sin stock');

        html += '<div class="fav-product-card" data-id="' + p.id + '">';
        html += '<img src="' + (p.imagen || '/static/img/productos/default.jpg') + '" class="card-img-top" alt="' + p.nombre + '" onerror="this.src=\'/static/img/productos/default.jpg\'">';
        html += '<div class="card-body" style="cursor:pointer;" onclick="window.location.href=\'/producto/' + p.slug + '\'">';
        html += '<h3 class="product-name">' + p.nombre + '</h3>';
        html += '<p class="product-category">' + p.categoria + '</p>';
        html += '<div class="product-price">';
        if (p.precio_oferta) {
            html += '<span class="old-price">$' + Math.round(p.precio) + '</span>';
            html += '$' + Math.round(p.precio_oferta);
        } else {
            html += '$' + Math.round(p.precio);
        }
        html += '</div>';
        html += '<div class="product-stock">';
        html += '<span class="' + stockClass + '"><i class="fas fa-check-circle"></i> ' + stockText + '</span>';
        html += '</div>';
        html += '</div>';
        html += '<div class="card-actions">';
        html += '<button class="btn-cart" onclick="addToCart(' + p.id + ', event)" ' + (p.stock === 0 ? 'disabled' : '') + '>';
        html += '<i class="fas fa-shopping-cart"></i> Agregar';
        html += '</button>';
        html += '<button class="btn-remove-fav" onclick="toggleFavorite(' + p.id + ', \'' + p.nombre.replace(/'/g, "\\'").replace(/'/g, "\\'") + '\', this)">';
        html += '<i class="fas fa-times"></i> <span class="remove-text">Quitar</span>';
        html += '</button>';
        html += '</div>';
        html += '</div>';
    }

    grid.innerHTML = html;
}

// ============================================================
// INICIALIZAR
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Inicializando favorites.js...');

    updateHeaderBadges();
    
    if (window.ANGELOW && window.ANGELOW.isAuthenticated) {
        getFavoritesFromServer(function(favoritos) {
            console.log('✅ Favoritos sincronizados desde el servidor:', favoritos);
            updateHeaderBadges();
            renderFavorites();
        });
    } else {
        renderFavorites();
    }
});

// ============================================================
// ESCUCHAR CAMBIOS DESDE OTRAS PESTAÑAS
// ============================================================
window.addEventListener('storage', function(e) {
    if (e.key === 'angelow_favorites') {
        console.log('📢 Storage event: favoritos cambiados');
        updateHeaderBadges();
        renderFavorites();
    }
});

// ============================================================
// ESTILOS PARA PARTÍCULAS
// ============================================================
var style = document.createElement('style');
style.textContent = `
    @keyframes particleFloat {
        0% { opacity: 1; transform: translateY(0) scale(1) rotate(0deg); }
        100% { opacity: 0; transform: translateY(-60px) scale(0) rotate(45deg); }
    }
`;
document.head.appendChild(style);
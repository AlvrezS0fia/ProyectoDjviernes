// static/js/detalle_producto.js

// ============================================================
// VARIABLE GLOBAL
// ============================================================
var productData = {};

// ============================================================
// CAMBIAR IMAGEN PRINCIPAL
// ============================================================
function changeImage(element, src) {
    var mainImage = document.getElementById('mainImage');
    if (mainImage) {
        mainImage.src = src;
    }
    var thumbnails = document.querySelectorAll('.thumbnail');
    for (var i = 0; i < thumbnails.length; i++) {
        thumbnails[i].classList.remove('active');
    }
    element.classList.add('active');
}

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
    var isFavorite = favorites.indexOf(productId) !== -1;
    
    console.log('📌 Estado actual:', isFavorite ? 'Favorito' : 'No favorito');
    console.log('🔑 Usuario autenticado:', window.ANGELOW && window.ANGELOW.isAuthenticated);
    
    // Si el usuario está autenticado, guardar en el servidor
    if (window.ANGELOW && window.ANGELOW.isAuthenticated) {
        // Deshabilitar botón temporalmente
        if (button) {
            button.disabled = true;
            button.style.opacity = '0.6';
        }
        
        saveFavoriteOnServer(productId, function(success, data) {
            if (success) {
                // Actualizar localStorage basado en la respuesta del servidor
                var favs = JSON.parse(localStorage.getItem('angelow_favorites') || '[]');
                
                if (data && data.es_favorito !== undefined) {
                    if (data.es_favorito) {
                        // Agregado a favoritos
                        if (favs.indexOf(productId) === -1) {
                            favs.push(productId);
                        }
                        showToast('success', 'fa-heart', '"' + productName + '" agregado a favoritos ❤️');
                        if (button) button.classList.add('active');
                        createHeartParticles(button);
                    } else {
                        // Eliminado de favoritos
                        var idx = favs.indexOf(productId);
                        if (idx !== -1) {
                            favs.splice(idx, 1);
                        }
                        showToast('success', 'fa-heart', '"' + productName + '" eliminado de favoritos');
                        if (button) button.classList.remove('active');
                    }
                }
                
                localStorage.setItem('angelow_favorites', JSON.stringify(favs));
                
                // Actualizar texto del botón
                if (button) {
                    var textSpan = button.querySelector('.fav-text');
                    if (textSpan) {
                        var isFav = favs.indexOf(productId) !== -1;
                        textSpan.textContent = isFav ? 'Favorito' : 'Favoritos';
                    }
                    button.disabled = false;
                    button.style.opacity = '1';
                }
                
                updateHeaderBadges();
                window.dispatchEvent(new Event('storage'));
            } else {
                showToast('error', 'fa-exclamation-triangle', '❌ Error al procesar favorito');
                if (button) {
                    button.disabled = false;
                    button.style.opacity = '1';
                }
            }
        });
    } else {
        // Usuario no autenticado - solo localStorage
        console.log('📌 Usuario no autenticado, usando solo localStorage');
        
        if (isFavorite) {
            favorites.splice(favorites.indexOf(productId), 1);
            showToast('success', 'fa-heart', '"' + productName + '" eliminado de favoritos');
            if (button) button.classList.remove('active');
        } else {
            favorites.push(productId);
            showToast('success', 'fa-heart', '"' + productName + '" agregado a favoritos ❤️');
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
function addToCart(productId) {
    showToast('success', 'fa-shopping-cart', '🛒 Producto agregado al carrito');
}

function buyNow(productId) {
    showToast('info', 'fa-bolt', '⚡ Redirigiendo al checkout...');
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
    } catch(e) {}
}

// ============================================================
// SINCRONIZAR FAVORITOS AL CARGAR LA PÁGINA
// ============================================================
function syncFavorites() {
    console.log('🔄 Sincronizando favoritos...');
    console.log('🔑 Usuario autenticado:', window.ANGELOW && window.ANGELOW.isAuthenticated);
    
    if (window.ANGELOW && window.ANGELOW.isAuthenticated) {
        getFavoritesFromServer(function(favoritos) {
            console.log('✅ Favoritos sincronizados desde el servidor:', favoritos);
            
            // Actualizar el botón de favoritos
            var btn = document.getElementById('favBtn-' + productData.id);
            if (btn) {
                var isFav = favoritos.indexOf(productData.id) !== -1;
                console.log('📌 Producto en favoritos:', isFav);
                
                if (isFav) {
                    btn.classList.add('active');
                    var textSpan = btn.querySelector('.fav-text');
                    if (textSpan) {
                        textSpan.textContent = 'Favorito';
                    }
                } else {
                    btn.classList.remove('active');
                    var textSpan = btn.querySelector('.fav-text');
                    if (textSpan) {
                        textSpan.textContent = 'Favoritos';
                    }
                }
            }
            
            updateHeaderBadges();
        });
    } else {
        console.log('⚠️ Usuario no autenticado, usando localStorage');
        // Usuario no autenticado - verificar localStorage
        var favs = JSON.parse(localStorage.getItem('angelow_favorites') || '[]');
        var btn = document.getElementById('favBtn-' + productData.id);
        if (btn) {
            var isFav = favs.indexOf(productData.id) !== -1;
            if (isFav) {
                btn.classList.add('active');
                var textSpan = btn.querySelector('.fav-text');
                if (textSpan) {
                    textSpan.textContent = 'Favorito';
                }
            }
        }
        updateHeaderBadges();
    }
}

// ============================================================
// INICIALIZAR
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Inicializando detalle_producto.js...');
    
    var productScript = document.getElementById('producto-data');
    if (productScript) {
        try {
            productData = JSON.parse(productScript.textContent);
            console.log('📦 Producto cargado:', productData.nombre);
            console.log('📦 ID del producto:', productData.id);
        } catch(e) {
            console.error('❌ Error parsing product data:', e);
        }
    } else {
        console.error('❌ Script "producto-data" no encontrado');
    }
    
    // Primero actualizar badges desde localStorage
    updateHeaderBadges();
    
    // Luego sincronizar con el servidor si está autenticado
    setTimeout(function() {
        syncFavorites();
    }, 300);
});

// ============================================================
// ESCUCHAR CAMBIOS DESDE OTRAS PESTAÑAS
// ============================================================
window.addEventListener('storage', function(e) {
    if (e.key === 'angelow_favorites') {
        console.log('📢 Storage event: favoritos cambiados');
        updateHeaderBadges();
        var favs = JSON.parse(e.newValue || '[]');
        var btn = document.getElementById('favBtn-' + productData.id);
        if (btn) {
            var isFav = favs.includes(productData.id);
            if (isFav) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
            var textSpan = btn.querySelector('.fav-text');
            if (textSpan) {
                textSpan.textContent = isFav ? 'Favorito' : 'Favoritos';
            }
        }
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

console.log('✅ detalle_producto.js cargado correctamente');
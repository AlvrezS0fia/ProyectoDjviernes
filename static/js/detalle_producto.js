// static/js/detalle_producto.js

// Variable global para datos del producto
var productData = {};

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

function toggleFavorite(productId, productName, button) {
    var isAuthenticated = window.ANGELOW && window.ANGELOW.isAuthenticated;

    if (isAuthenticated) {
        fetch("{% url 'tienda:api_toggle_favorito' %}", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({producto_id: productId}),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                if (data.es_favorito) {
                    showToast('success', 'fa-heart', '"' + productName + '" agregado a favoritos');
                    if (button) button.classList.add('active');
                } else {
                    showToast('success', 'fa-heart', '"' + productName + '" eliminado de favoritos');
                    if (button) button.classList.remove('active');
                }
                if (button) {
                    var textSpan = button.querySelector('.fav-text');
                    if (textSpan) {
                        textSpan.textContent = data.es_favorito ? 'Favorito' : 'Favoritos';
                    }
                }
                updateHeaderBadges();
                window.dispatchEvent(new Event('storage'));
            } else {
                showToast('error', 'fa-exclamation-circle', data.message || 'Error');
            }
        })
        .catch(error => {
            showToast('error', 'fa-exclamation-circle', 'Error al procesar favorito');
        });
    } else {
        var favorites = JSON.parse(localStorage.getItem('angelow_favorites') || '[]');
        var index = favorites.indexOf(productId);
        var isFavorite = index !== -1;

        if (isFavorite) {
            favorites.splice(index, 1);
            showToast('success', 'fa-heart', '"' + productName + '" eliminado de favoritos');
            if (button) button.classList.remove('active');
        } else {
            favorites.push(productId);
            showToast('success', 'fa-heart', '"' + productName + '" agregado a favoritos');
            createHeartParticles(button);
            if (button) button.classList.add('active');
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

function showToast(type, icon, message) {
    var container = document.getElementById('toastContainer');
    if (!container) return;
    
    var toast = document.createElement('div');
    toast.className = 'toast-item ' + type;
    toast.innerHTML = '<i class="fas ' + icon + '"></i><span style="flex:1;">' + message + '</span><button class="toast-close" onclick="this.parentElement.remove()">&times;</button>';
    
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

function addToCart(productId) {
    showToast('success', 'fa-shopping-cart', 'Producto agregado al carrito');
}

function buyNow(productId) {
    showToast('info', 'fa-bolt', 'Redirigiendo al checkout...');
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

// Inicializar
document.addEventListener('DOMContentLoaded', function() {
    var productScript = document.getElementById('producto-data');
    if (productScript) {
        try {
            productData = JSON.parse(productScript.textContent);
        } catch(e) {
            console.error('Error parsing product data:', e);
        }
    }
    updateHeaderBadges();
});

// Escuchar cambios desde otras pestañas
window.addEventListener('storage', function(e) {
    if (e.key === 'angelow_favorites') {
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

// Agregar estilo para las partículas
var style = document.createElement('style');
style.textContent = `
    @keyframes particleFloat {
        0% { opacity: 1; transform: translateY(0) scale(1) rotate(0deg); }
        100% { opacity: 0; transform: translateY(-60px) scale(0) rotate(45deg); }
    }
`;
document.head.appendChild(style);
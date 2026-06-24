// static/js/home.js

// ============================================================
// BUSCADOR EN TIEMPO REAL
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
    var searchInput = document.getElementById('searchInput');
    var searchBtn = document.getElementById('searchBtn');
    var clearBtn = document.getElementById('clearSearchBtn');
    var resultsCount = document.getElementById('resultsCount');
    var cards = document.querySelectorAll('.product-card');
    
    function filterProducts() {
        var query = searchInput.value.toLowerCase().trim();
        var visibleCount = 0;
        
        for (var i = 0; i < cards.length; i++) {
            var card = cards[i];
            var nombre = card.dataset.nombre || '';
            var subcategoria = card.dataset.subcategoria || '';
            var categoria = card.dataset.categoria || '';
            var text = nombre + ' ' + subcategoria + ' ' + categoria;
            
            if (query === '' || text.indexOf(query) !== -1) {
                card.style.display = 'flex';
                visibleCount++;
            } else {
                card.style.display = 'none';
            }
        }
        
        if (query === '') {
            resultsCount.textContent = 'Mostrando todos los productos';
        } else {
            resultsCount.textContent = visibleCount + ' producto' + (visibleCount !== 1 ? 's' : '') + ' encontrado' + (visibleCount !== 1 ? 's' : '') + ' para "' + query + '"';
        }
    }
    
    if (searchInput) {
        searchInput.addEventListener('input', filterProducts);
    }
    if (searchBtn) {
        searchBtn.addEventListener('click', filterProducts);
    }
    if (clearBtn) {
        clearBtn.addEventListener('click', function() {
            searchInput.value = '';
            filterProducts();
            searchInput.focus();
        });
    }
    if (searchInput) {
        searchInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                filterProducts();
            }
        });
    }
    if (searchInput && searchInput.value) {
        filterProducts();
    }
});

// ============================================================
// HERO CAROUSEL
// ============================================================
(function() {
    var cardsData = [
        { amount: "$140.000", bg: "linear-gradient(135deg, #1E40AF, #3B82F6)", label: "#BAE6FD", val: "#FFFFFF" },
        { amount: "$120.000", bg: "linear-gradient(135deg, #FFFFFF, #EFF6FF)", label: "#1E40AF", val: "#0A1628" },
        { amount: "$200.000", bg: "linear-gradient(135deg, #3B82F6, #60A5FA)", label: "#FFFFFF", val: "#FFFFFF" },
        { amount: "$80.000",  bg: "linear-gradient(135deg, #DBEAFE, #F0F9FF)", label: "#1E40AF", val: "#0A1628" }
    ];

    var slides = [
        { type: "cards", title: "Tarjetas de Regalo", sub: "El regalo perfecto para cada ocasión" },
        { type: "promo", badge: "Nueva colección", title: "Color Dreamers", subtitle: "Viste la temporada con estilo, comodidad y color", btnText: "Explorar colección", link: "/tienda/" },
        { type: "promo", badge: "Bebés felices", title: "20% OFF + envío", subtitle: "Comodidad suave para los más pequeños", btnText: "Ver bebés", link: "/tienda/?categoria=bebes" },
        { type: "promo", badge: "Escolar listo", title: "Accesorios escolares", subtitle: "Mochilas, loncheras y detalles para el regreso", btnText: "Ver accesorios", link: "/tienda/" },
        { type: "shipping", badge: "Envío gratis", title: "Sin mínimo de compra", subtitle: "Válido durante las próximas 24 horas", btnText: "Comprar ahora", link: "/tienda/" }
    ];

    var currentIndex = 0;
    var autoInterval;
    var isPaused = false;
    var slideDuration = 6500;
    var progressBar = null;
    var wrapper = null;
    var carouselSection = null;
    var totalSlides = slides.length;

    function createGiftCard(card) {
        var el = document.createElement("div");
        el.className = "gift-card";
        el.style.background = card.bg;
        el.style.color = card.val;
        el.innerHTML = '<div class="gift-card-top"><span>ANGELOW</span><span class="gift-icon">★</span></div><div><div class="gift-label">BONO REGALO</div><div class="gift-amount">' + card.amount + '</div></div>';
        return el;
    }

    function buildSlides() {
        var fragment = document.createDocumentFragment();
        for (var i = 0; i < slides.length; i++) {
            var slide = slides[i];
            var slideDiv = document.createElement("div");
            slideDiv.className = "slide-base";

            if (slide.type === "cards") {
                slideDiv.innerHTML = '<div class="slide-copy"><span class="promo-badge">AngeLow gift</span><h2 class="carousel-title">' + slide.title + '</h2><p class="promo-subtitle">' + slide.sub + '</p></div>';
                var grid = document.createElement("div");
                grid.className = "cards-grid";
                for (var j = 0; j < cardsData.length; j++) {
                    grid.appendChild(createGiftCard(cardsData[j]));
                }
                slideDiv.appendChild(grid);
            } else {
                slideDiv.innerHTML = '<div class="promo-content"><span class="promo-badge">' + slide.badge + '</span><h2 class="promo-title">' + slide.title + '</h2><p class="promo-subtitle">' + slide.subtitle + '</p><a href="' + slide.link + '" class="btn-gold slide-action">' + slide.btnText + '</a></div>';
            }

            fragment.appendChild(slideDiv);
        }
        return fragment;
    }

    function goToSlide(index) {
        if (!wrapper) return;
        if (index < 0) index = 0;
        if (index >= totalSlides) index = totalSlides - 1;
        currentIndex = index;
        wrapper.style.transform = "translateX(-" + (currentIndex * 100) + "%)";
        var dots = document.querySelectorAll(".dot");
        for (var d = 0; d < dots.length; d++) {
            if (d === currentIndex) {
                dots[d].classList.add("active");
            } else {
                dots[d].classList.remove("active");
            }
        }
        if (!isPaused) resetProgressBar();
        if (autoInterval && !isPaused) {
            clearInterval(autoInterval);
            autoInterval = setInterval(autoSlide, slideDuration);
        }
    }

    function resetProgressBar() {
        if (!progressBar) return;
        progressBar.style.transition = "none";
        progressBar.style.width = "0%";
        setTimeout(function() {
            progressBar.style.transition = "width " + slideDuration + "ms linear";
            if (!isPaused) progressBar.style.width = "100%";
        }, 20);
    }

    function autoSlide() {
        if (!isPaused) goToSlide((currentIndex + 1) % totalSlides);
    }

    function pauseCarousel() {
        if (isPaused) return;
        isPaused = true;
        if (autoInterval) clearInterval(autoInterval);
        if (progressBar) progressBar.style.transition = "none";
        if (carouselSection) carouselSection.classList.add("paused");
    }

    function resumeCarousel() {
        if (!isPaused) return;
        isPaused = false;
        autoInterval = setInterval(autoSlide, slideDuration);
        resetProgressBar();
        if (carouselSection) carouselSection.classList.remove("paused");
    }

    function initHeroCarousel() {
        var container = document.getElementById("heroCarouselContainer");
        if (!container) return;

        carouselSection = document.getElementById("heroCarouselSection");
        var viewport = document.createElement("div");
        viewport.className = "slides-viewport";

        wrapper = document.createElement("div");
        wrapper.className = "slide-wrapper";
        wrapper.appendChild(buildSlides());
        viewport.appendChild(wrapper);

        progressBar = document.createElement("div");
        progressBar.className = "carousel-progress";
        viewport.appendChild(progressBar);

        var btnLeft = document.createElement("button");
        btnLeft.className = "nav-btn nav-btn-left";
        btnLeft.type = "button";
        btnLeft.innerHTML = "‹";
        btnLeft.setAttribute("aria-label", "Diapositiva anterior");

        var btnRight = document.createElement("button");
        btnRight.className = "nav-btn nav-btn-right";
        btnRight.type = "button";
        btnRight.innerHTML = "›";
        btnRight.setAttribute("aria-label", "Siguiente diapositiva");

        viewport.appendChild(btnLeft);
        viewport.appendChild(btnRight);

        var dotsDiv = document.createElement("div");
        dotsDiv.className = "dots-container";
        dotsDiv.setAttribute("aria-label", "Navegación del carrusel");
        for (var d = 0; d < totalSlides; d++) {
            var dot = document.createElement("button");
            dot.type = "button";
            dot.className = "dot" + (d === 0 ? " active" : "");
            dot.setAttribute("aria-label", "Ir a la diapositiva " + (d + 1));
            (function(index) {
                dot.addEventListener("click", function() {
                    pauseCarousel();
                    goToSlide(index);
                    resumeCarousel();
                });
            })(d);
            dotsDiv.appendChild(dot);
        }
        viewport.appendChild(dotsDiv);

        container.appendChild(viewport);

        btnLeft.addEventListener("click", function() {
            pauseCarousel();
            goToSlide(currentIndex - 1);
            resumeCarousel();
        });

        btnRight.addEventListener("click", function() {
            pauseCarousel();
            goToSlide(currentIndex + 1);
            resumeCarousel();
        });

        if (carouselSection) {
            carouselSection.addEventListener("mouseenter", pauseCarousel);
            carouselSection.addEventListener("mouseleave", resumeCarousel);
        }

        var touchStartX = 0;
        viewport.addEventListener("touchstart", function(e) {
            touchStartX = e.changedTouches[0].clientX;
            pauseCarousel();
        }, { passive: true });

        viewport.addEventListener("touchend", function(e) {
            var diff = e.changedTouches[0].clientX - touchStartX;
            if (Math.abs(diff) > 40) {
                goToSlide(currentIndex + (diff > 0 ? -1 : 1));
            }
            resumeCarousel();
        }, { passive: true });

        autoInterval = setInterval(autoSlide, slideDuration);
        resetProgressBar();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initHeroCarousel);
    } else {
        initHeroCarousel();
    }
})();

// ============================================================
// FAVORITOS - Con corazón rojo y contador
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
    updateFavBadges();
}

function updateFavBadges() {
    var favs = getFavorites();
    var count = favs.length;
    
    var headerBadge = document.getElementById('favBadgeHeader');
    if (headerBadge) {
        headerBadge.textContent = count;
        headerBadge.style.display = count > 0 ? 'flex' : 'none';
    }
    
    var favCount = document.getElementById('favCount');
    if (favCount) {
        favCount.textContent = count + ' productos';
    }
    
    var favBtns = document.querySelectorAll('.btn-fav');
    for (var i = 0; i < favBtns.length; i++) {
        var btn = favBtns[i];
        var id = parseInt(btn.getAttribute('data-id'));
        if (favs.indexOf(id) !== -1) {
            btn.classList.add('active');
            btn.querySelector('i').style.color = '#ef4444';
        } else {
            btn.classList.remove('active');
            btn.querySelector('i').style.color = '';
        }
    }
}

function toggleFavorite(productId, event) {
    if (event) event.stopPropagation();
    
    var favs = getFavorites();
    var index = favs.indexOf(productId);
    var btn = document.querySelector('.btn-fav[data-id="' + productId + '"]');
    
    if (index > -1) {
        favs.splice(index, 1);
        if (btn) {
            btn.classList.remove('active');
            btn.querySelector('i').style.color = '';
        }
        showToast('Eliminado de favoritos', 'info');
    } else {
        favs.push(productId);
        if (btn) {
            btn.classList.add('active');
            btn.querySelector('i').style.color = '#ef4444';
        }
        showToast('Agregado a favoritos ❤️', 'success');
    }
    
    saveFavorites(favs);
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
    if (event) event.stopPropagation();
    
    var card = document.querySelector('.product-card[data-id="' + productId + '"]');
    if (!card) {
        showToast('Producto no encontrado', 'error');
        return;
    }
    
    var name = card.querySelector('.product-name').textContent;
    var priceText = card.querySelector('.product-price').textContent.replace(/[^0-9.]/g, '');
    var price = parseFloat(priceText) || 0;
    var imagen = card.querySelector('.product-card-img').src;
    
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
}

// ============================================================
// CATEGORÍAS - FILTRO
// ============================================================
var activeCategory = 'todos';

function filterByCategory(category) {
    activeCategory = category;
    
    var pills = document.querySelectorAll('.category-pill');
    for (var i = 0; i < pills.length; i++) {
        if (pills[i].dataset.categoria === category) {
            pills[i].classList.add('active');
        } else {
            pills[i].classList.remove('active');
        }
    }
    
    var cards = document.querySelectorAll('.product-card');
    for (var j = 0; j < cards.length; j++) {
        var cardCat = cards[j].dataset.categoria || '';
        if (category === 'todos') {
            cards[j].style.display = 'flex';
        } else {
            cards[j].style.display = cardCat.indexOf(category) !== -1 ? 'flex' : 'none';
        }
    }
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
    toast.className = 'toast-item ' + type;
    toast.innerHTML = '<i class="fas ' + (icons[type] || icons.info) + '" style="color: ' + (colors[type] || colors.info) + ';"></i><span style="color: #1E3A8A; font-size: 14px; font-weight: 500;">' + message + '</span><button class="toast-close" onclick="this.parentElement.remove()">×</button>';
    container.appendChild(toast);
    setTimeout(function() { toast.remove(); }, 3500);
}

// ============================================================
// INICIALIZACIÓN
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
    var favs = getFavorites();
    for (var i = 0; i < favs.length; i++) {
        var btn = document.querySelector('.btn-fav[data-id="' + favs[i] + '"]');
        if (btn) {
            btn.classList.add('active');
            btn.querySelector('i').style.color = '#ef4444';
        }
    }
    updateCartBadge();
    updateFavBadges();
    filterByCategory('todos');
});
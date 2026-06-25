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
        html
// Sepet İşlemleri
let cart = [];
const cartIcon = document.getElementById('cart-icon');
const cartSidebar = document.getElementById('cart-sidebar');
const cartItemsContainer = document.getElementById('cart-items');
const compareButton = document.getElementById('compare-button');
const cartCountElement = document.querySelector('.cart-count');
const clearCartButton = document.getElementById('clear-cart');

// Sepete ürün ekleme
document.querySelectorAll('.add-to-cart').forEach(button => {
    button.addEventListener('click', function() {
        const vehicleId = this.dataset.id;
        const vehicle = {
            id: vehicleId,
            name: this.dataset.name,
            price: parseFloat(this.dataset.price),
            quantity: 1
        };
        
        // Sepette aynı araç var mı kontrol et
        const existingItemIndex = cart.findIndex(item => item.id === vehicleId);
        
        if (existingItemIndex >= 0) {
            // Varsa mesaj göster
            showNotification(`${vehicle.name} zaten sepetinizde var`, 'info');
        } else if(cart.length < 5) {
            // Yoksa ve limit aşılmadıysa ekle
            cart.push(vehicle);
            updateCartUI();
            showCartNotification(`${vehicle.name} sepete eklendi`);
            
            // Sepet sayısını güncelle ve animasyon ekle
            updateCartCount();
        } else {
            showNotification('Maksimum 5 araç karşılaştırabilirsiniz', 'error');
        }
    });
});

// Sepetten ürün silme
function setupRemoveButtons() {
    document.querySelectorAll('.cart-item-remove').forEach(button => {
        button.addEventListener('click', function() {
            const cartItem = this.closest('.cart-item');
            const itemId = cartItem.dataset.id;
            
            // Sepetten ürünü kaldır
            const removedItem = cart.find(item => item.id === itemId);
            cart = cart.filter(item => item.id !== itemId);
            
            // Animasyonlu silme
            cartItem.classList.add('removing');
            setTimeout(() => {
                updateCartUI();
            }, 300);
            
            // Bildirim göster
            if (removedItem) {
                showNotification(`${removedItem.name} sepetten çıkarıldı`, 'info');
            }
            
            // Sepet sayısını güncelle
            updateCartCount();
        });
    });
}

// Sepeti temizle
clearCartButton.addEventListener('click', function() {
    if (cart.length === 0) return;
    
    if (confirm('Sepetinizdeki tüm araçları kaldırmak istediğinize emin misiniz?')) {
        cart = [];
        updateCartUI();
        updateCartCount();
        showNotification('Sepet temizlendi', 'info');
    }
});

// Karşılaştırma Butonu
compareButton.addEventListener('click', async () => {
    if(cart.length < 2) {
        showNotification('Karşılaştırma için en az 2 araç seçmelisiniz', 'error');
        return;
    }

    try {
        const response = await fetch('/compare', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                vehicles: cart,
                user_preference: "4 kişilik aile için" // Kullanıcıdan alınabilir
            })
        });

        const result = await response.json();
        showComparisonResults(result);
    } catch (error) {
        console.error('Karşılaştırma hatası:', error);
        showNotification('Karşılaştırma sırasında bir hata oluştu', 'error');
    }
});

// Sepet sayısını güncelle
function updateCartCount() {
    const count = cart.length;
    cartCountElement.textContent = count;
    
    // Animasyon ekle
    cartCountElement.classList.add('pulse');
    setTimeout(() => cartCountElement.classList.remove('pulse'), 500);
    
    // Sıfır olduğunda görünürlüğü ayarla
    if (count === 0) {
        cartCountElement.classList.add('hidden');
    } else {
        cartCountElement.classList.remove('hidden');
    }
}

// Animasyonlu sepet bildirimi
function showCartNotification(message) {
    const notification = document.getElementById('cart-notification');
    const messageElement = document.getElementById('cart-notification-message');
    
    messageElement.textContent = message;
    notification.classList.add('show');
    
    setTimeout(() => {
        notification.classList.remove('show');
    }, 2000);
}

// UI Güncelleme Fonksiyonları
function updateCartUI() {
    const cartItems = document.getElementById('cart-items');
    const totalPrice = cart.reduce((sum, item) => sum + item.price, 0);
    
    // Sepet boşsa boş mesajı göster
    if (cart.length === 0) {
        cartItems.innerHTML = `
            <div class="empty-cart">
                <i class="fas fa-shopping-cart"></i>
                <p>Sepetiniz boş</p>
            </div>
        `;
        compareButton.disabled = true;
        compareButton.classList.add('disabled');
    } else {
        // Template kullanarak sepet öğelerini oluştur
        cartItems.innerHTML = '';
        
        cart.forEach(item => {
            const template = document.getElementById('cart-item-template');
            const clone = document.importNode(template.content, true);
            
            const cartItem = clone.querySelector('.cart-item');
            cartItem.dataset.id = item.id;
            
            const img = clone.querySelector('.cart-item-img');
            img.src = `/static/uploads/${item.id}.jpg`;
            img.alt = item.name;
            
            clone.querySelector('.cart-item-title').textContent = item.name;
            clone.querySelector('.cart-item-price').textContent = `${item.price.toLocaleString()} TL`;
            
            cartItems.appendChild(clone);
        });
        
        setupRemoveButtons();
        compareButton.disabled = cart.length < 2;
        compareButton.classList.toggle('disabled', cart.length < 2);
    }

    document.querySelector('.total-price').textContent = `${totalPrice.toLocaleString()} TL`;
}

function showNotification(message, type = 'success') {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = `notification ${type} show`;
    setTimeout(() => notification.classList.remove('show'), 3000);
}

// Modal Kontrolleri
document.getElementById('cart-close').addEventListener('click', () => {
    cartSidebar.classList.remove('active');
});

cartIcon.addEventListener('click', () => {
    cartSidebar.classList.add('active');
});

// Sayfa yüklendiğinde sepet sayısını sıfırla
document.addEventListener('DOMContentLoaded', function() {
    updateCartCount();
    updateCartUI();
});

// Karşılaştırma Sonuçlarını Göster
function showComparisonResults(data) {
    const resultsContainer = document.getElementById('comparison-results');
    resultsContainer.innerHTML = `
        <div class="vehicle-comparison">
            ${data.recommendations.map(item => `
                <div class="comparison-item">
                    <h4>${item.vehicle}</h4>
                    <ul>
                        ${item.reasons.map(reason => `<li>${reason}</li>`).join('')}
                    </ul>
                    ${item.alternative ? `
                        <div class="alternative">
                            <h5>Alternatif: ${item.alternative.vehicle}</h5>
                            <p>Tahmini Fiyat: ${item.alternative.price} TL</p>
                            <ul>
                                ${item.alternative.reasons.map(reason => `<li>${reason}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                </div>
            `).join('')}
        </div>
    `;
    document.getElementById('compare-modal').classList.add('active');
}

document.addEventListener('DOMContentLoaded', function () {
    const detailButtons = document.querySelectorAll('.btn-details');
    
    // Modal HTML'ini sayfaya ekle
    const modalHTML = `
        <div id="vehicleModal" class="vehicle-modal">
            <div class="vehicle-modal-content">
                <span class="close-modal">&times;</span>
                <h2 id="modal-title">Araç Detayları</h2>
                <div class="vehicle-info-container">
                    <div class="vehicle-image">
                        <img id="modal-image" src="/static/images/default-car.jpg" alt="Araç Görseli">
                    </div>
                    <div class="vehicle-details">
                        <div class="detail-row">
                            <h3>Temel Bilgiler</h3>
                            <p><strong>Marka:</strong> <span id="modal-marka"></span></p>
                            <p><strong>Model:</strong> <span id="modal-model"></span></p>
                            <p><strong>Üretim Yılı:</strong> <span id="modal-yil"></span></p>
                            <p><strong>Kilometre:</strong> <span id="modal-km"></span> km</p>
                            <p><strong>Fiyat:</strong> <span id="modal-fiyat"></span> TL</p>
                            <p><strong>Renk:</strong> <span id="modal-renk"></span></p>
                        </div>
                        <div class="detail-row">
                            <h3>Teknik Özellikler</h3>
                            <p><strong>Yakıt Türü:</strong> <span id="modal-yakit"></span></p>
                            <p><strong>Motor Hacmi:</strong> <span id="modal-motor-hacmi"></span></p>
                            <p><strong>Motor Gücü:</strong> <span id="modal-motor-gucu"></span> HP</p>
                            <p><strong>Vites Türü:</strong> <span id="modal-vites"></span></p>
                            <p><strong>Kasa Türü:</strong> <span id="modal-kasa"></span></p>
                        </div>
                        <div class="detail-row">
                            <h3>Diğer Özellikler</h3>
                            <p><strong>Kapı Sayısı:</strong> <span id="modal-kapi"></span></p>
                            <p><strong>Yolcu Kapasitesi:</strong> <span id="modal-yolcu"></span></p>
                            <p><strong>Bagaj Hacmi:</strong> <span id="modal-bagaj"></span> lt</p>
                            <p><strong>Hasar Durumu:</strong> <span id="modal-hasar"></span></p>
                            <p><strong>Hasar Maliyeti:</strong> <span id="modal-hasar-maliyet"></span> TL</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Modal HTML'ini sayfaya ekle
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    const modal = document.getElementById('vehicleModal');
    const closeBtn = document.querySelector('.close-modal');
    
    // Modal kapatma işlevi
    closeBtn.onclick = function() {
        modal.style.display = "none";
    }
    
    // Modal dışına tıklandığında kapatma
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }
    
    // Detay butonlarına tıklama olayı ekle
    detailButtons.forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            const vehicleId = button.getAttribute('href').split('/').pop();
            console.log("Vehicle ID:", vehicleId);
            
            fetch(`/vehicle-details/${vehicleId}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Sunucu hatası: ' + response.status);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.error) {
                        alert(data.error);
                    } else {
                        // Modal içeriğini doldur
                        document.getElementById('modal-marka').textContent = data.Marka || 'Belirtilmemiş';
                        document.getElementById('modal-model').textContent = data.Model || 'Belirtilmemiş';
                        document.getElementById('modal-yil').textContent = data.UretimYili || 'Belirtilmemiş';
                        document.getElementById('modal-km').textContent = data.Kilometre ? data.Kilometre.toLocaleString() : 'Belirtilmemiş';
                        document.getElementById('modal-fiyat').textContent = data.Fiyat ? data.Fiyat.toLocaleString() : 'Belirtilmemiş';
                        document.getElementById('modal-renk').textContent = data.Renk || 'Belirtilmemiş';
                        document.getElementById('modal-yakit').textContent = data.YakitTuru || 'Belirtilmemiş';
                        document.getElementById('modal-motor-hacmi').textContent = data.MotorHacmi || 'Belirtilmemiş';
                        document.getElementById('modal-motor-gucu').textContent = data.MotorGucu || 'Belirtilmemiş';
                        document.getElementById('modal-vites').textContent = data.VitesTuru || 'Belirtilmemiş';
                        document.getElementById('modal-kasa').textContent = data.KasaTuru || 'Belirtilmemiş';
                        document.getElementById('modal-kapi').textContent = data.KapiSayisi || 'Belirtilmemiş';
                        document.getElementById('modal-yolcu').textContent = data.YolcuKapasitesi || 'Belirtilmemiş';
                        document.getElementById('modal-bagaj').textContent = data.BagajHacmi || 'Belirtilmemiş';
                        document.getElementById('modal-hasar').textContent = data.HasarDurumu || 'Belirtilmemiş';
                        document.getElementById('modal-hasar-maliyet').textContent = data.HasarMaliyeti ? data.HasarMaliyeti.toLocaleString() : 'Belirtilmemiş';
                        
                        // Modal başlığını güncelle
                        document.getElementById('modal-title').textContent = `${data.Marka} ${data.Model} (${data.UretimYili})`;
                        
                        // Modalı göster
                        modal.style.display = "block";
                    }
                })
                .catch(error => {
                    console.error('Hata:', error);
                    alert('Araç bilgileri alınırken bir hata oluştu. Lütfen tekrar deneyin.');
                });
        });
    });
});
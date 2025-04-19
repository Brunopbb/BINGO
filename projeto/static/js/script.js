let currentImageIndex = 0;
let images = [];

function fetchImages() {
    fetch('/plot')
        .then(response => response.json())
        .then(data => {
            if (data.images && data.images.length > 0) {
                images = data.images;
                updateDisplayedImage();
            }
        })
        .catch(error => console.error('Erro ao carregar imagens:', error));
}

function updateDisplayedImage() {
    if (images.length > 0) {
        document.getElementById('spectrum-image').src = images[currentImageIndex];
        document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
    }
}

function nextImage() {
    currentImageIndex = (currentImageIndex + 1) % images.length;
    updateDisplayedImage();
}

function previousImage() {
    currentImageIndex = (currentImageIndex - 1 + images.length) % images.length;
    updateDisplayedImage();
}

setInterval(fetchImages, 3000);
fetchImages();

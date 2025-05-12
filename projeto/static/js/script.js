let currentImageIndex = 0;
let images = [];
const captions = ["Sinais de rádio CG", "Uirapuru"];

function fetchImages() {
    fetch('/plot')
        .then(response => response.json())
        .then(data => {
            if (data.images && data.images.length > 0) {
                images = data.images;
                currentImageIndex = currentImageIndex % images.length;
                updateDisplayedImage();
            }
        })
        .catch(error => console.error('Erro ao carregar imagens:', error));
}

function updateDisplayedImage() {
    if (images.length > 0) {
        const imageElement = document.getElementById('spectrum-image');
        const captionElement = document.getElementById('image-caption');
        const updateTimeElement = document.getElementById('last-update');

        imageElement.src = images[currentImageIndex];
        captionElement.textContent = captions[currentImageIndex] || 'Sem legenda';
        updateTimeElement.textContent = new Date().toLocaleTimeString();
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

// Inicia o carregamento periódico
setInterval(fetchImages, 2000);
fetchImages();

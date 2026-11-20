// ==========================================
// sw.js - Service Worker do BioQuest PWA
// ==========================================

const cacheName = 'bioquest-v3';
const assets = [
  '/bioquest/',
  '/bioquest/index.html',
  '/bioquest/manifest.json',
  '/bioquest/css/style.css',
  '/bioquest/js/app.js',
  '/bioquest/js/data.js',
  '/bioquest/icons/android-chrome-192x192.png',
  '/bioquest/icons/android-chrome-512x512.png',
  '/bioquest/icons/favicon.ico',
  '/bioquest/icons/apple-touch-icon.png',
  '/bioquest/icons/favicon-16x16.png',
  '/bioquest/images/estufa_de_alface.png',
  '/bioquest/images/vertical_farming.png',
  '/bioquest/images/cyberpunk_agriculture.png',
  '/bioquest/audio/success.mp3',
  '/bioquest/audio/error.mp3',
  '/bioquest/audio/click.mp3',
  '/bioquest/audio/ambience.mp3'
];

// 1. Instalação: Salva todos os arquivos no cache do navegador
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(cacheName).then((cache) => {
      console.log('PWA: Arquivos em cache para modo offline.');
      return cache.addAll(assets);
    })
  );
});

// 2. Ativação: Limpa caches antigos se houver atualização de versão
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((key) => key !== cacheName).map((key) => caches.delete(key))
      );
    })
  );
});

// 3. Estratégia Fetch: Tenta buscar no Cache primeiro, se não tiver, vai na Rede
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request);
    })
  );
});
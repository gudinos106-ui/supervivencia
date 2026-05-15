const CACHE_NAME = 'supervivencia-cache-v1';
const urlsToCache = [
  '/',
  'https://tu-app-de-supervivencia.streamlit.app/'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});

const CACHE_NAME = 'selexia-travel-v1.0.0'
const STATIC_CACHE = 'static-v1.0.0'
const DYNAMIC_CACHE = 'dynamic-v1.0.0'

// Файлы для предварительного кэширования
const STATIC_FILES = [
  '/',
  '/static/dist/assets/index.css',
  '/static/dist/assets/index.js',
  '/static/dist/assets/vendor.js',
  '/static/dist/assets/bootstrap.js',
  '/static/dist/assets/fontawesome.js'
]

// Установка Service Worker
self.addEventListener('install', (event) => {
  console.log('Service Worker: Installing...')
  
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then((cache) => {
        console.log('Service Worker: Caching static files')
        return cache.addAll(STATIC_FILES)
      })
      .then(() => {
        console.log('Service Worker: Static files cached')
        return self.skipWaiting()
      })
      .catch((error) => {
        console.error('Service Worker: Error caching static files', error)
      })
  )
})

// Активация Service Worker
self.addEventListener('activate', (event) => {
  console.log('Service Worker: Activating...')
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
              console.log('Service Worker: Deleting old cache', cacheName)
              return caches.delete(cacheName)
            }
          })
        )
      })
      .then(() => {
        console.log('Service Worker: Activated')
        return self.clients.claim()
      })
  )
})

// Перехват сетевых запросов
self.addEventListener('fetch', (event) => {
  const { request } = event
  const url = new URL(request.url)
  
  // Пропускаем API запросы
  if (url.pathname.startsWith('/api/')) {
    return
  }
  
  // Пропускаем запросы к Django admin
  if (url.pathname.startsWith('/admin/')) {
    return
  }
  
  // Стратегия кэширования для статических файлов
  if (request.destination === 'style' || 
      request.destination === 'script' || 
      request.destination === 'image' ||
      request.destination === 'font') {
    
    event.respondWith(
      caches.match(request)
        .then((response) => {
          if (response) {
            return response
          }
          
          return fetch(request)
            .then((fetchResponse) => {
              // Кэшируем успешные ответы
              if (fetchResponse && fetchResponse.status === 200) {
                const responseClone = fetchResponse.clone()
                caches.open(DYNAMIC_CACHE)
                  .then((cache) => {
                    cache.put(request, responseClone)
                  })
              }
              return fetchResponse
            })
        })
    )
    return
  }
  
  // Стратегия "Network First" для HTML страниц
  if (request.destination === 'document') {
    event.respondWith(
      fetch(request)
        .then((response) => {
          // Кэшируем успешные ответы
          if (response && response.status === 200) {
            const responseClone = response.clone()
            caches.open(DYNAMIC_CACHE)
              .then((cache) => {
                cache.put(request, responseClone)
              })
          }
          return response
        })
        .catch(() => {
          // Возвращаем кэшированную версию при ошибке сети
          return caches.match(request)
        })
    )
    return
  }
  
  // Для остальных запросов используем "Cache First"
  event.respondWith(
    caches.match(request)
      .then((response) => {
        if (response) {
          return response
        }
        
        return fetch(request)
          .then((fetchResponse) => {
            // Кэшируем успешные ответы
            if (fetchResponse && fetchResponse.status === 200) {
              const responseClone = fetchResponse.clone()
              caches.open(DYNAMIC_CACHE)
                .then((cache) => {
                  cache.put(request, responseClone)
                })
            }
            return fetchResponse
          })
      })
  )
})

// Обработка push уведомлений
self.addEventListener('push', (event) => {
  console.log('Service Worker: Push received')
  
  const options = {
    body: event.data ? event.data.text() : 'Новое уведомление от Selexia Travel',
    icon: '/static/images/logo.png',
    badge: '/static/images/badge.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: 'Открыть',
        icon: '/static/images/checkmark.png'
      },
      {
        action: 'close',
        title: 'Закрыть',
        icon: '/static/images/xmark.png'
      }
    ]
  }
  
  event.waitUntil(
    self.registration.showNotification('Selexia Travel', options)
  )
})

// Обработка кликов по уведомлениям
self.addEventListener('notificationclick', (event) => {
  console.log('Service Worker: Notification clicked')
  
  event.notification.close()
  
  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/')
    )
  }
})

// Обработка синхронизации в фоне
self.addEventListener('sync', (event) => {
  console.log('Service Worker: Background sync', event.tag)
  
  if (event.tag === 'background-sync') {
    event.waitUntil(
      // Здесь можно добавить логику синхронизации данных
      console.log('Background sync completed')
    )
  }
})

// Обработка ошибок
self.addEventListener('error', (event) => {
  console.error('Service Worker: Error', event.error)
})

// Обработка необработанных отклонений промисов
self.addEventListener('unhandledrejection', (event) => {
  console.error('Service Worker: Unhandled promise rejection', event.reason)
})

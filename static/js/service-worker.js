// Service Worker para Notificações Push - service-worker.js

self.addEventListener('push', event => {
    const data = event.data.json();

    const options = {
        body: data.body,
        icon: '/static/images/icon-192x192.png', // Ícone da notificação
        badge: '/static/images/badge-72x72.png', // Ícone menor (barra de status do Android)
        data: {
            url: data.url // URL para abrir ao clicar
        }
    };

    event.waitUntil(
        self.registration.showNotification(data.title, options)
    );
});

self.addEventListener('notificationclick', event => {
    event.notification.close(); // Fecha a notificação

    // Abre a URL associada ou a página principal
    event.waitUntil(
        clients.openWindow(event.notification.data.url || '/')
    );
}); 
// Lógica para registrar Service Worker e pedir permissão - push-notifications.js

const VAPID_PUBLIC_KEY = 'BKtH7i2z36di5PKVc30HP5qyhQAm_0B7Pf3A6nQkM0YgM-YLmFIY86UbPisTrJZe_uBCR3KhWn7MnCOl54_jr7M';

function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}

async function registerServiceWorker() {
    if ('serviceWorker' in navigator) {
        try {
            const registration = await navigator.serviceWorker.register('/static/js/service-worker.js');
            console.log('Service Worker registrado com sucesso:', registration);
            
            // Após o login, verificar o status da permissão
            if (document.getElementById('ask-push-permission')) {
                document.getElementById('ask-push-permission').addEventListener('click', askForPushPermission);
            }

        } catch (error) {
            console.error('Falha ao registrar Service Worker:', error);
        }
    }
}

async function askForPushPermission() {
    if ('PushManager' in window) {
        try {
            const permission = await Notification.requestPermission();
            if (permission === 'granted') {
                console.log('Permissão para notificações concedida.');
                await subscribeUserToPush();
            } else {
                console.warn('Permissão para notificações negada.');
            }
        } catch (error) {
            console.error('Erro ao solicitar permissão para push:', error);
        }
    }
}

async function subscribeUserToPush() {
    try {
        const registration = await navigator.serviceWorker.ready;
        const existingSubscription = await registration.pushManager.getSubscription();

        if (existingSubscription) {
            console.log('Usuário já está inscrito.');
            return;
        }

        const subscription = await registration.pushManager.subscribe({
            userVisibleOnly: true,
            applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY)
        });

        console.log('Nova inscrição:', subscription);
        await sendSubscriptionToServer(subscription);

    } catch (error) {
        console.error('Erro ao inscrever usuário:', error);
    }
}

async function sendSubscriptionToServer(subscription) {
    try {
        const response = await fetch('/subscribe_push', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(subscription),
        });

        if (response.ok) {
            console.log('Inscrição enviada ao servidor com sucesso.');
            // Opcional: esconder o botão de pedir permissão
            const button = document.getElementById('ask-push-permission');
            if (button) button.style.display = 'none';
        } else {
            console.error('Falha ao enviar inscrição ao servidor.');
        }
    } catch (error) {
        console.error('Erro ao enviar inscrição ao servidor:', error);
    }
}

// Inicia o processo
registerServiceWorker(); 
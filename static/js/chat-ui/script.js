import { ChatManager } from './chat-utils.js';

document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chatMessages');
    const textInput = document.getElementById('textInput');
    const sendButton = document.getElementById('sendButton');
    const startVoice = document.getElementById('startVoice');
    const voiceStatus = document.getElementById('voiceStatus');

    // Initialize chat manager
    const chatManager = new ChatManager(chatMessages);

    let recognition = null;
    let isListening = false;

    // Verificar si el navegador soporta reconocimiento de voz
    if ('webkitSpeechRecognition' in window) {
        recognition = new webkitSpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = 'es-ES'; // Configurar el idioma a español

        recognition.onstart = () => {
            voiceStatus.textContent = 'Escuchando...';
            startVoice.classList.add('active');
            isListening = true;
        };

        recognition.onend = () => {
            voiceStatus.textContent = '';
            startVoice.classList.remove('active');
            isListening = false;
        };

        recognition.onresult = (event) => {
            const transcript = Array.from(event.results)
                .map(result => result[0])
                .map(result => result.transcript)
                .join('');

            textInput.value = transcript;
        };

        recognition.onerror = (event) => {
            voiceStatus.textContent = 'Error: ' + event.error;
            startVoice.classList.remove('active');
            isListening = false;
        };
    } else {
        startVoice.style.display = 'none';
        voiceStatus.textContent = 'El reconocimiento de voz no está soportado en este navegador.';
    }

    // Función para enviar mensaje
    async function sendMessage() {
        const text = textInput.value.trim();
        if (text) {
            try {
                textInput.value = '';
                await chatManager.sendMessage(text);
            } catch (error) {
                console.error('Error:', error);
            }
        }
    }

    // Event listeners
    sendButton.addEventListener('click', sendMessage);

    textInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    startVoice.addEventListener('click', () => {
        if (!recognition) return;

        if (isListening) {
            recognition.stop();
        } else {
            textInput.value = '';
            recognition.start();
        }
    });
});

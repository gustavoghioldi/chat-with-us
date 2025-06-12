document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chatMessages');
    const textInput = document.getElementById('textInput');
    const sendButton = document.getElementById('sendButton');
    const startVoice = document.getElementById('startVoice');
    const voiceStatus = document.getElementById('voiceStatus');

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

    // Función para agregar mensajes al chat
    function addMessage(text, isSent = true) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', isSent ? 'sent' : 'received');
        messageDiv.textContent = text;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Función para enviar mensaje
    async function sendMessage() {
        const text = textInput.value.trim();
        if (text) {
            addMessage(text);
            textInput.value = '';

            try {
                const response = await fetch('/api/v1/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    body: JSON.stringify(
                        { message: text,
                          agent: "Rosaura"
                        }
                    )
                });

                if (!response.ok) {
                    throw new Error('Error en la respuesta del servidor');
                }

                const data = await response.json();

                addMessage(data.response, false);
            } catch (error) {
                console.error('Error:', error);
                addMessage('Error al enviar el mensaje: ' + error.message, false);
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

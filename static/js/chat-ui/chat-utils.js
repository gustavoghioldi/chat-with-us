export class ChatManager {
    constructor(chatMessagesElement) {
        this.chatMessages = chatMessagesElement;
    }

    addMessage(text, isSent = true) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', isSent ? 'sent' : 'received');
        messageDiv.textContent = text;
        this.chatMessages.appendChild(messageDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    async sendMessage(text, agent = "rosaura") {
        if (!text.trim()) return;

        this.addMessage(text);

        try {
            const response = await fetch('/api/v1/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({
                    message: text,
                    agent: agent
                })
            });

            if (!response.ok) {
                throw new Error('Error en la respuesta del servidor');
            }

            const data = await response.json();
            this.addMessage(data.response, false);

            return data;
        } catch (error) {
            console.error('Error:', error);
            this.addMessage('Error al enviar el mensaje: ' + error.message, false);
            throw error;
        }
    }
}

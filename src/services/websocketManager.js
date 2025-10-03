const WebSocket = require('ws');
const authController = require('../controllers/authController');

class WebSocketManager {
    constructor(server) {
        this.wss = new WebSocket.Server({ server, path: '/ws/chat' });
        this.pharmacists = new Map();
        this.users = new Map();
        this.messageQueue = new Map();
        this.setupWebSocketServer();
        this.startHeartbeat();
    }

    setupWebSocketServer() {
        this.wss.on('connection', (ws, req) => {
            const clientId = Date.now() + '-' + Math.random().toString(36).substr(2);
            ws.clientId = clientId;
            ws.isAlive = true;

            ws.on('pong', () => {
                ws.isAlive = true;
            });

            ws.on('message', async (message) => {
                try {
                    const data = JSON.parse(message);
                    await this.handleMessage(ws, data);
                } catch (error) {
                    console.error('Message handling error:', error);
                    this.sendError(ws, 'Invalid message format');
                }
            });

            ws.on('close', () => {
                this.handleDisconnection(ws);
            });
        });
    }

    startHeartbeat() {
        setInterval(() => {
            this.wss.clients.forEach((ws) => {
                if (ws.isAlive === false) {
                    this.handleDisconnection(ws);
                    return ws.terminate();
                }

                ws.isAlive = false;
                ws.ping();
            });
        }, 30000);
    }

    async handleMessage(ws, data) {
        switch (data.type) {
            case 'auth':
                await this.handleAuth(ws, data.token);
                break;
            
            case 'message':
                await this.handleChatMessage(ws, data);
                break;
            
            case 'typing':
                this.handleTyping(ws, data);
                break;

            case 'read':
                this.handleReadReceipt(ws, data);
                break;

            default:
                this.sendError(ws, 'Unknown message type');
        }
    }

    async handleAuth(ws, token) {
        const user = authController.verifyToken(token);
        if (!user) {
            return this.sendError(ws, 'Invalid token');
        }

        ws.user = user;
        ws.authenticated = true;

        // Send pending messages if any
        const pendingMessages = this.messageQueue.get(user.id);
        if (pendingMessages) {
            pendingMessages.forEach(msg => {
                ws.send(JSON.stringify(msg));
            });
            this.messageQueue.delete(user.id);
        }

        // Update user/pharmacist maps
        if (user.isPharmacist) {
            this.pharmacists.set(ws.clientId, {
                ws,
                user,
                activeChats: new Set()
            });
        } else {
            this.users.set(ws.clientId, {
                ws,
                user,
                assignedPharmacist: null
            });
        }

        ws.send(JSON.stringify({
            type: 'auth_success',
            user: user
        }));
    }

    async handleChatMessage(ws, data) {
        if (!ws.authenticated) {
            return this.sendError(ws, 'Authentication required');
        }

        const message = {
            id: Date.now() + '-' + Math.random().toString(36).substr(2),
            from: ws.user,
            content: data.message,
            timestamp: new Date().toISOString(),
            status: 'sent'
        };

        if (ws.user.isPharmacist) {
            const pharmacist = this.pharmacists.get(ws.clientId);
            if (!pharmacist || !data.userId) {
                return this.sendError(ws, 'Invalid message routing');
            }

            // Find user's connection
            const targetUser = Array.from(this.users.values())
                .find(u => u.user.id === data.userId);

            if (targetUser) {
                if (targetUser.ws.readyState === WebSocket.OPEN) {
                    targetUser.ws.send(JSON.stringify({
                        type: 'message',
                        ...message
                    }));
                } else {
                    // Queue message if user is offline
                    if (!this.messageQueue.has(data.userId)) {
                        this.messageQueue.set(data.userId, []);
                    }
                    this.messageQueue.get(data.userId).push({
                        type: 'message',
                        ...message
                    });
                }
            }
        } else {
            const user = this.users.get(ws.clientId);
            if (!user || !user.assignedPharmacist) {
                return this.sendError(ws, 'No pharmacist assigned');
            }

            const pharmacist = this.pharmacists.get(user.assignedPharmacist);
            if (pharmacist && pharmacist.ws.readyState === WebSocket.OPEN) {
                pharmacist.ws.send(JSON.stringify({
                    type: 'message',
                    ...message
                }));
            }
        }

        // Send delivery confirmation
        ws.send(JSON.stringify({
            type: 'message_status',
            messageId: message.id,
            status: 'delivered'
        }));
    }

    handleTyping(ws, data) {
        if (!ws.authenticated) return;

        const user = ws.user;
        if (user.isPharmacist) {
            // Send typing indicator to specific user
            if (data.userId) {
                const targetUser = Array.from(this.users.values())
                    .find(u => u.user.id === data.userId);
                if (targetUser && targetUser.ws.readyState === WebSocket.OPEN) {
                    targetUser.ws.send(JSON.stringify({
                        type: 'typing',
                        userId: user.id
                    }));
                }
            }
        } else {
            // Send typing indicator to assigned pharmacist
            const userInfo = this.users.get(ws.clientId);
            if (userInfo && userInfo.assignedPharmacist) {
                const pharmacist = this.pharmacists.get(userInfo.assignedPharmacist);
                if (pharmacist && pharmacist.ws.readyState === WebSocket.OPEN) {
                    pharmacist.ws.send(JSON.stringify({
                        type: 'typing',
                        userId: user.id
                    }));
                }
            }
        }
    }

    handleReadReceipt(ws, data) {
        if (!ws.authenticated || !data.messageId) return;

        const user = ws.user;
        if (user.isPharmacist) {
            if (data.userId) {
                const targetUser = Array.from(this.users.values())
                    .find(u => u.user.id === data.userId);
                if (targetUser && targetUser.ws.readyState === WebSocket.OPEN) {
                    targetUser.ws.send(JSON.stringify({
                        type: 'read_receipt',
                        messageId: data.messageId,
                        userId: user.id
                    }));
                }
            }
        } else {
            const userInfo = this.users.get(ws.clientId);
            if (userInfo && userInfo.assignedPharmacist) {
                const pharmacist = this.pharmacists.get(userInfo.assignedPharmacist);
                if (pharmacist && pharmacist.ws.readyState === WebSocket.OPEN) {
                    pharmacist.ws.send(JSON.stringify({
                        type: 'read_receipt',
                        messageId: data.messageId,
                        userId: user.id
                    }));
                }
            }
        }
    }

    handleDisconnection(ws) {
        const clientId = ws.clientId;

        if (this.pharmacists.has(clientId)) {
            const pharmacist = this.pharmacists.get(clientId);
            // Notify users that pharmacist disconnected
            pharmacist.activeChats.forEach(userId => {
                const user = Array.from(this.users.values())
                    .find(u => u.user.id === userId);
                if (user && user.ws.readyState === WebSocket.OPEN) {
                    user.ws.send(JSON.stringify({
                        type: 'system',
                        message: 'Pharmacist disconnected. Please wait or try again later.'
                    }));
                }
            });
            this.pharmacists.delete(clientId);
        } else if (this.users.has(clientId)) {
            const user = this.users.get(clientId);
            if (user.assignedPharmacist) {
                const pharmacist = this.pharmacists.get(user.assignedPharmacist);
                if (pharmacist) {
                    pharmacist.activeChats.delete(user.user.id);
                    if (pharmacist.ws.readyState === WebSocket.OPEN) {
                        pharmacist.ws.send(JSON.stringify({
                            type: 'system',
                            message: `User ${user.user.name} disconnected`
                        }));
                    }
                }
            }
            this.users.delete(clientId);
        }
    }

    sendError(ws, message) {
        ws.send(JSON.stringify({
            type: 'error',
            message: message
        }));
    }
}

module.exports = WebSocketManager;
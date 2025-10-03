require('dotenv').config();
const express = require('express');
const cors = require('cors');
const http = require('http');
const { chatHandler } = require('./src/controllers/chatController');

// --- Helper function to format links ---
function formatLinks(text) {
    // Regex to find paths like /login, /products, /health-news, etc.
    // It avoids matching file paths like /image.png by not matching dots.
    const pathRegex = /(?<!\w)\/[a-zA-Z0-9-]+(?:\/[a-zA-Z0-9-]+)*/g;
    
    let processedText = text;
    const foundPaths = text.match(pathRegex);

    if (foundPaths) {
        const uniquePaths = [...new Set(foundPaths)]; // Process each unique path only once
        uniquePaths.forEach(path => {
            // Create a user-friendly name from the path
            const linkName = path.substring(1) // remove leading '/'
                               .replace(/-/g, ' ') // replace hyphens with spaces
                               .replace(/\b\w/g, char => char.toUpperCase()); // capitalize words
            
            const markdownLink = `[${linkName}](${path})`;
            
            // Replace the path only when it appears as a standalone word,
            // possibly surrounded by spaces, punctuation, or at the start/end of the string.
            const replacementRegex = new RegExp(`(\\s|^|\\()(${path})(\\s|$|\\.|\\,)`, 'g');
            processedText = processedText.replace(replacementRegex, `$1${markdownLink}$3`);
        });
    }
    return processedText;
}

const app = express();
const server = http.createServer(app);

const PORT = process.env.CHATBOT_SERVICE_PORT || 3001;

// --- Middleware ---
app.use(cors({
    origin: ['http://localhost:5173', 'http://127.0.0.1:5173'], // Allow main frontend
    methods: ['GET', 'POST'],
    credentials: true
}));
app.use(express.json({ limit: '1mb' }));

// --- Routes ---

// Middleware to intercept and format the AI chat response
const formatAiResponseMiddleware = (req, res, next) => {
    const originalJson = res.json;
    res.json = function (body) {
        if (body && body.message) {
            body.message = formatLinks(body.message);
        }
        return originalJson.call(this, body);
    };
    next();
};

app.post('/api/ai-chat', formatAiResponseMiddleware, chatHandler);

// Health check endpoint
app.get('/api/health', (req, res) => {
    res.json({ 
        status: 'OK',
        name: 'chatbot-service',
        timestamp: new Date().toISOString(),
    });
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({ error: 'Something went wrong!' });
});

// --- Server ---
server.listen(PORT, () => {
    console.log(`AI Chatbot service listening on port ${PORT}`);
});



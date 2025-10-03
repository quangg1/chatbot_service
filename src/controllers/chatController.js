const { getRagResponse } = require('../services/ragService');
const { HfInference } = require('@huggingface/inference');

const chatHandler = async (req, res) => {
    console.log('Received request body:', JSON.stringify(req.body, null, 2));

    const { message, userId, huggingFaceToken } = req.body;

    if (!message) {
        return res.status(400).json({ error: 'Message is required' });
    }

    // Use the user's token if provided, otherwise fall back to the server's default token
    const tokenToUse = huggingFaceToken || process.env.HUGGINGFACE_API_KEY;

    if (!tokenToUse) {
        return res.status(400).json({ error: 'Hugging Face token is missing. Please provide one in the chat settings.' });
    }

    try {
        // Initialize HfInference with the determined token for this specific request
        const hf = new HfInference(tokenToUse);
        
        // This is a simplified flow. Replace with your actual RAG logic.
        // For demonstration, we'll just call the inference API directly.
        const ragResponse = await getRagResponse(message, userId, hf);

        res.json({ message: ragResponse });
    } catch (error) {
        console.error('Error in chat handler:', error);
        res.status(500).json({
            error: 'Failed to get response from AI model',
            details: error.message
        });
    }
};

module.exports = { chatHandler };

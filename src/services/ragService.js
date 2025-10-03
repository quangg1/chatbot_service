const axios = require('axios');

const PYTHON_API_URL = process.env.PYTHON_API_URL || 'http://127.0.0.1:8003/chat';

async function getRagResponse(message, user_id, hf_token) {
  if (!message) {
    throw new Error('Message is required');
  }
  if (!hf_token) {
    throw new Error('Hugging Face token is required');
  }

  try {
    console.log('Sending request to Python API:', {
      url: PYTHON_API_URL,
      message,
      user_id
    });

    const response = await axios.post(PYTHON_API_URL, {
      message,
      user_id,
      hf_token
    }, {
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    });

    if (!response.data) {
      throw new Error('Empty response from Python service');
    }

    // Log successful response
    console.log('Python API response:', {
      status: response.status,
      data: response.data
    });

    return response.data;
  } catch (error) {
    console.error('Error details:', {
      name: error.name,
      message: error.message,
      code: error.code,
      status: error.response?.status,
      data: error.response?.data
    });

    // Handle different types of errors
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      if (error.response.status === 404) {
        throw new Error('Python API endpoint not found');
      }
      if (error.response.headers['content-type']?.includes('text/html')) {
        throw new Error('Invalid response type from Python service (received HTML)');
      }
      throw new Error(error.response.data?.error || 'Python service error');
    } else if (error.code === 'ECONNREFUSED') {
      throw new Error('Python service is not running');
    } else if (error.code === 'ECONNABORTED') {
      throw new Error('Request to Python service timed out');
    } else if (error.request) {
      // The request was made but no response was received
      throw new Error('No response from Python service');
    } else {
      // Something happened in setting up the request that triggered an Error
      throw new Error(`Failed to make request to Python service: ${error.message}`);
    }
  }
}

module.exports = { getRagResponse };

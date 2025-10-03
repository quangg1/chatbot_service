const { spawn } = require('child_process');
const path = require('path');

function runPythonChat(message, hfToken, sessionId, userId) {
  return new Promise((resolve, reject) => {
    const scriptPath = path.join(__dirname, 'chat_runner.py');
    const env = { ...process.env };
    if (hfToken && typeof hfToken === 'string') {
      env.HF_TOKEN = hfToken;
      env.HUGGINGFACE_TOKEN = hfToken;
    }
    const py = spawn(process.env.PYTHON_BIN || 'python', [scriptPath], {
      env,
      stdio: ['pipe', 'pipe', 'pipe']
    });

    let stdout = '';
    let stderr = '';

    py.stdout.on('data', (d) => (stdout += d.toString()));
    py.stderr.on('data', (d) => (stderr += d.toString()));

    py.on('close', (code) => {
      if (code !== 0) {
        return reject(new Error(stderr || `Python exited with code ${code}`));
      }
      // Lọc chỉ JSON cuối cùng
      const lines = stdout.split(/\r?\n/).filter(Boolean);
      let lastJson = lines.reverse().find(line => {
        try { JSON.parse(line); return true; } 
        catch { return false; }
      });

      if (!lastJson) {
        return reject(new Error('No valid JSON in Python stdout\n' + stdout));
      }

      try {
        const parsed = JSON.parse(lastJson);
        resolve(parsed.reply);
      } catch (e) {
        reject(new Error('Invalid JSON from Python: ' + e.message + '\n' + lastJson));
      }
    });

    py.stdin.write(JSON.stringify({ message: message || '', sessionId: sessionId || '', userId: userId || '' }));
    py.stdin.end();
  });
}

async function chatHandler(req, res) {
  try {
    const { message, hfToken, sessionId, userId } = req.body || {};
    if (!message || typeof message !== 'string') {
      return res.status(400).json({ error: 'message is required' });
    }
    const reply = await runPythonChat(message, hfToken, sessionId, userId);
    return res.json({ reply });
  } catch (e) {
    console.error('chatHandler error:', e);
    return res.status(500).json({ error: e?.message || 'internal error' });
  }
}

module.exports = { chatHandler };



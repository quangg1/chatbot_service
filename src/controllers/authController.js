const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');

class AuthController {
    constructor() {
        this.tokens = new Map(); // Store refresh tokens
    }

    async login(req, res) {
        try {
            const { username, password } = req.body;
            
            // TODO: Replace with actual database authentication
            // This is a mock authentication
            if (username === "test" && password === "test") {
                const user = {
                    id: "1",
                    username: username,
                    name: "Test User",
                    isPharmacist: username.includes("pharmacist")
                };

                const accessToken = this.generateAccessToken(user);
                const refreshToken = this.generateRefreshToken(user);
                
                // Store refresh token
                this.tokens.set(user.id, refreshToken);

                res.json({
                    token: accessToken,
                    refreshToken: refreshToken,
                    user: user
                });
            } else {
                res.status(401).json({ error: 'Invalid credentials' });
            }
        } catch (error) {
            console.error('Login error:', error);
            res.status(500).json({ error: 'Internal server error' });
        }
    }

    async refresh(req, res) {
        try {
            const { refreshToken } = req.body;
            if (!refreshToken) {
                return res.status(401).json({ error: 'Refresh token required' });
            }

            try {
                const decoded = jwt.verify(refreshToken, process.env.JWT_REFRESH_SECRET);
                const storedToken = this.tokens.get(decoded.id);

                if (storedToken !== refreshToken) {
                    return res.status(401).json({ error: 'Invalid refresh token' });
                }

                const accessToken = this.generateAccessToken({
                    id: decoded.id,
                    username: decoded.username,
                    name: decoded.name,
                    isPharmacist: decoded.isPharmacist
                });

                res.json({ token: accessToken });
            } catch (error) {
                return res.status(401).json({ error: 'Invalid refresh token' });
            }
        } catch (error) {
            console.error('Refresh token error:', error);
            res.status(500).json({ error: 'Internal server error' });
        }
    }

    generateAccessToken(user) {
        return jwt.sign(user, process.env.JWT_SECRET, { expiresIn: '1h' });
    }

    generateRefreshToken(user) {
        return jwt.sign(user, process.env.JWT_REFRESH_SECRET);
    }

    verifyToken(token) {
        try {
            return jwt.verify(token, process.env.JWT_SECRET);
        } catch (error) {
            return null;
        }
    }
}

module.exports = new AuthController();
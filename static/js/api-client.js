/**
 * Face Analysis API Client
 * Handles all API calls with error handling and performance optimizations
 */

class FaceAnalysisAPI {
    constructor(baseURL = '/api') {
        this.baseURL = baseURL;
        this.cache = new Map();
        this.requestQueue = [];
        this.isProcessing = false;
        this.retryAttempts = 3;
        this.retryDelay = 1000;
    }

    /**
     * Make API request with error handling and retries
     */
    async makeRequest(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        for (let attempt = 1; attempt <= this.retryAttempts; attempt++) {
            try {
                const response = await fetch(url, config);
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                const data = await response.json();
                return data;

            } catch (error) {
                console.error(`API request failed (attempt ${attempt}):`, error);
                
                if (attempt === this.retryAttempts) {
                    throw error;
                }

                // Wait before retrying
                await this.delay(this.retryDelay * attempt);
            }
        }
    }

    /**
     * Delay function for retries
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Analyze face for age, gender, and emotion
     */
    async analyzeFace(imageData) {
        try {
            const cacheKey = this.generateCacheKey(imageData);
            
            // Check cache first
            if (this.cache.has(cacheKey)) {
                console.log('Returning cached result');
                return this.cache.get(cacheKey);
            }

            const result = await this.makeRequest('/analyze', {
                method: 'POST',
                body: JSON.stringify({ image: imageData })
            });

            // Cache the result
            this.cache.set(cacheKey, result);
            
            return result;

        } catch (error) {
            console.error('Face analysis failed:', error);
            throw error;
        }
    }

    /**
     * Analyze emotion only
     */
    async analyzeEmotion(imageData) {
        try {
            const result = await this.makeRequest('/analyze-emotion', {
                method: 'POST',
                body: JSON.stringify({ image: imageData })
            });

            return result;

        } catch (error) {
            console.error('Emotion analysis failed:', error);
            throw error;
        }
    }

    /**
     * Face recognition
     */
    async faceRecognition(imageData) {
        try {
            const result = await this.makeRequest('/face-recognize', {
                method: 'POST',
                body: JSON.stringify({ image: imageData })
            });

            return result;

        } catch (error) {
            console.error('Face recognition failed:', error);
            throw error;
        }
    }

    /**
     * Driver monitoring
     */
    async driverMonitoring(imageData) {
        try {
            const result = await this.makeRequest('/driver-monitoring', {
                method: 'POST',
                body: JSON.stringify({ image: imageData })
            });

            return result;

        } catch (error) {
            console.error('Driver monitoring failed:', error);
            throw error;
        }
    }

    /**
     * Chat with AI chatbot
     */
    async chatWithBot(message) {
        try {
            const result = await this.makeRequest('/chatbot', {
                method: 'POST',
                body: JSON.stringify({ message })
            });

            return result;

        } catch (error) {
            console.error('Chatbot request failed:', error);
            throw error;
        }
    }

    /**
     * Upload file
     */
    async uploadFile(file) {
        try {
            const formData = new FormData();
            formData.append('file', file);

            const result = await fetch(`${this.baseURL}/upload`, {
                method: 'POST',
                body: formData
            });

            if (!result.ok) {
                throw new Error(`Upload failed: ${result.statusText}`);
            }

            return await result.json();

        } catch (error) {
            console.error('File upload failed:', error);
            throw error;
        }
    }

    /**
     * Get API statistics
     */
    async getStats() {
        try {
            const result = await this.makeRequest('/stats');
            return result;

        } catch (error) {
            console.error('Failed to get stats:', error);
            throw error;
        }
    }

    /**
     * Health check
     */
    async healthCheck() {
        try {
            const result = await this.makeRequest('/health');
            return result;

        } catch (error) {
            console.error('Health check failed:', error);
            throw error;
        }
    }

    /**
     * Clear cache
     */
    async clearCache() {
        try {
            const result = await this.makeRequest('/clear-cache', {
                method: 'POST'
            });

            // Clear local cache
            this.cache.clear();

            return result;

        } catch (error) {
            console.error('Failed to clear cache:', error);
            throw error;
        }
    }

    /**
     * Generate cache key from data
     */
    generateCacheKey(data) {
        if (typeof data === 'string') {
            return btoa(data).slice(0, 20);
        }
        return btoa(JSON.stringify(data)).slice(0, 20);
    }

    /**
     * Process image for API
     */
    processImage(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => {
                const img = new Image();
                img.onload = () => {
                    const canvas = document.createElement('canvas');
                    const ctx = canvas.getContext('2d');
                    
                    // Resize image if too large
                    const maxSize = 800;
                    let { width, height } = img;
                    
                    if (width > maxSize || height > maxSize) {
                        const ratio = Math.min(maxSize / width, maxSize / height);
                        width *= ratio;
                        height *= ratio;
                    }
                    
                    canvas.width = width;
                    canvas.height = height;
                    ctx.drawImage(img, 0, 0, width, height);
                    
                    const dataURL = canvas.toDataURL('image/jpeg', 0.8);
                    resolve(dataURL);
                };
                img.onerror = reject;
                img.src = e.target.result;
            };
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    }

    /**
     * Queue requests for better performance
     */
    async queueRequest(requestFn) {
        return new Promise((resolve, reject) => {
            this.requestQueue.push({ requestFn, resolve, reject });
            this.processQueue();
        });
    }

    /**
     * Process queued requests
     */
    async processQueue() {
        if (this.isProcessing || this.requestQueue.length === 0) {
            return;
        }

        this.isProcessing = true;

        while (this.requestQueue.length > 0) {
            const { requestFn, resolve, reject } = this.requestQueue.shift();
            
            try {
                const result = await requestFn();
                resolve(result);
            } catch (error) {
                reject(error);
            }

            // Small delay between requests
            await this.delay(100);
        }

        this.isProcessing = false;
    }

    /**
     * Get cached data
     */
    getCachedData(key) {
        return this.cache.get(key);
    }

    /**
     * Set cached data
     */
    setCachedData(key, data, ttl = 300000) { // 5 minutes default
        this.cache.set(key, data);
        
        // Auto-remove after TTL
        setTimeout(() => {
            this.cache.delete(key);
        }, ttl);
    }

    /**
     * Clear all cached data
     */
    clearAllCache() {
        this.cache.clear();
    }
}

// Global API instance
const api = new FaceAnalysisAPI();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FaceAnalysisAPI;
} 
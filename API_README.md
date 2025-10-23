# Face Analysis API

A high-performance REST API for face analysis, recognition, and monitoring built with Flask and OpenCV.

## 🚀 Features

- **Face Analysis**: Age, gender, and emotion detection
- **Face Recognition**: Biometric identification system
- **Driver Monitoring**: Drowsiness and distraction detection
- **AI Chatbot**: Intelligent conversation system
- **File Upload**: Secure file handling
- **Caching**: Performance optimization with Redis
- **Rate Limiting**: API protection and fair usage
- **Error Handling**: Comprehensive error management

## 📋 Requirements

- Python 3.8+
- OpenCV 4.8+
- TensorFlow 2.13+
- Flask 2.3+
- Redis (optional, for production caching)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Age-gender-detection
   ```

2. **Install dependencies**
   ```bash
   pip install -r api_requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run the API**
   ```bash
   python run_api.py
   ```

## 🌐 API Endpoints

### Health Check
```http
GET /api/health
```
Returns API status and model loading information.

### Face Analysis
```http
POST /api/analyze
Content-Type: application/json

{
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
}
```
Analyzes face for age, gender, and emotion.

### Emotion Analysis
```http
POST /api/analyze-emotion
Content-Type: application/json

{
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
}
```
Analyzes emotion only.

### Face Recognition
```http
POST /api/face-recognition
Content-Type: application/json

{
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
}
```
Performs face recognition (development).

### Driver Monitoring
```http
POST /api/driver-monitoring
Content-Type: application/json

{
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
}
```
Monitors driver for drowsiness and distraction.

### AI Chatbot
```http
POST /api/chatbot
Content-Type: application/json

{
  "message": "Hello, how can you help me?"
}
```
Chat with AI assistant.

### File Upload
```http
POST /api/upload
Content-Type: multipart/form-data

file: [image file]
```
Upload image files for processing.

### Statistics
```http
GET /api/stats
```
Get API usage statistics.

### Clear Cache
```http
POST /api/clear-cache
```
Clear all cached data.

## 📊 Response Format

### Success Response
```json
{
  "success": true,
  "faces_detected": 1,
  "results": [
    {
      "gender": "Male",
      "age": "25-32",
      "emotion": "happy",
      "confidence": 0.95,
      "region": {
        "x": 100,
        "y": 150,
        "w": 200,
        "h": 200
      }
    }
  ],
  "processing_time": 1640995200.123
}
```

### Error Response
```json
{
  "error": "No face detected in the image"
}
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Environment (development/production) | development |
| `PORT` | API port | 5001 |
| `HOST` | API host | 0.0.0.0 |
| `SECRET_KEY` | Flask secret key | auto-generated |
| `REDIS_URL` | Redis connection URL | None |
| `MAX_CONTENT_LENGTH` | Max file size (bytes) | 10485760 |

### Configuration Classes

- **DevelopmentConfig**: Debug mode, simple cache
- **ProductionConfig**: Production settings, Redis cache
- **TestingConfig**: Testing environment

## 🚀 Performance Optimizations

### Caching
- **Response Caching**: 5-minute cache for analysis results
- **Model Caching**: Pre-loaded AI models
- **Redis Support**: Production-ready caching

### Rate Limiting
- **Default**: 100 requests per minute
- **Analysis**: 30 requests per minute
- **Upload**: 20 requests per minute

### Image Processing
- **Auto-resize**: Large images are automatically resized
- **Format optimization**: JPEG compression for faster uploads
- **Batch processing**: Queue system for multiple requests

## 🔒 Security Features

- **CORS Support**: Cross-origin resource sharing
- **File Validation**: Secure file upload handling
- **Rate Limiting**: Protection against abuse
- **Input Validation**: Comprehensive input sanitization
- **Error Handling**: Secure error responses

## 📱 Frontend Integration

### JavaScript Client
```javascript
// Initialize API client
const api = new FaceAnalysisAPI('/api');

// Analyze face
const result = await api.analyzeFace(imageData);

// Chat with bot
const response = await api.chatWithBot('Hello');
```

### Example Usage
```html
<script src="/static/js/api-client.js"></script>
<script>
async function analyzeImage(file) {
    try {
        const imageData = await api.processImage(file);
        const result = await api.analyzeFace(imageData);
        displayResults(result);
    } catch (error) {
        console.error('Analysis failed:', error);
    }
}
</script>
```

## 🐳 Docker Support

### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5001

CMD ["python", "run_api.py"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "5001:5001"
    environment:
      - FLASK_ENV=production
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
  
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
```

## 📈 Monitoring

### Health Check
```bash
curl http://localhost:5001/api/health
```

### Logs
```bash
tail -f api.log
```

### Statistics
```bash
curl http://localhost:5001/api/stats
```

## 🧪 Testing

### Run Tests
```bash
python -m pytest tests/
```

### API Testing
```bash
# Test face analysis
curl -X POST http://localhost:5001/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"image": "data:image/jpeg;base64,..."}'

# Test chatbot
curl -X POST http://localhost:5001/api/chatbot \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
```

## 🚨 Troubleshooting

### Common Issues

1. **Models not loading**
   - Ensure all model files are in the project directory
   - Check file permissions

2. **Memory issues**
   - Reduce image size before processing
   - Increase system memory

3. **Performance issues**
   - Enable Redis caching
   - Optimize image quality

4. **CORS errors**
   - Check CORS configuration
   - Verify frontend URL

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the troubleshooting guide 
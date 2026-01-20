# Ollama Intelligent Router 🧠🔀

An intelligent proxy that automatically routes queries to the most appropriate Ollama model based on content analysis.

Perfect for use with Cursor, Continue, or any OpenAI-compatible AI client.

## ✨ Features

- **Intelligent Routing**: Automatically selects the best model for each query
- **OpenAI Compatible**: Works with any client that supports OpenAI API
- **Fast Responses**: Routes simple queries to smaller, faster models
- **Specialized Models**: Uses domain-specific models for coding, math, vision
- **Zero Configuration**: Works out of the box with sensible defaults
- **Cost Effective**: Maximize local LLM efficiency

## 🎯 How It Works

```
Your AI Client (Cursor/Continue/etc)
         ↓
Ollama Router (analyzes query)
         ↓
    ┌────┴────┬────────┬──────────┬─────────┐
    ↓         ↓        ↓          ↓         ↓
  Fast    Reasoning  Coding   Vision   General
 Model      Model    Model    Model     Model
```

**Routing Logic:**
- `"What is X?"` → Fast 3B model (quick answers)
- `"Solve this equation..."` → Reasoning model (deep thinking)
- `"Write a function..."` → Coding model (specialized)
- `"What's in this image?"` → Vision model (multimodal)
- Everything else → General 7B model (balanced)

## 🚀 Quick Start

### Prerequisites

1. **Install Ollama**: [ollama.ai](https://ollama.ai)
2. **Pull some models**:
   ```bash
   ollama pull qwen2.5:3b          # Fast model
   ollama pull qwen2.5:7b          # General model
   ollama pull qwen2.5-coder:7b    # Coding model
   ollama pull deepseek-r1:7b      # Reasoning model
   ollama pull llava:7b            # Vision model (optional)
   ```

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR-USERNAME/ollama-router.git
cd ollama-router

# Install Python dependencies
pip install fastapi uvicorn httpx

# Run the router
python router.py
```

The router will start on `http://localhost:4000`.

### Configure Your AI Client

**For Cursor:**
1. Open Settings (Cmd/Ctrl + ,)
2. Search for "OpenAI"
3. Set Base URL: `http://localhost:4000/v1`
4. Set API Key: `local` (any value works)
5. Restart Cursor

**For Continue:**
```json
{
  "models": [{
    "title": "Local Ollama",
    "provider": "openai",
    "model": "gpt-4",
    "apiBase": "http://localhost:4000/v1",
    "apiKey": "local"
  }]
}
```

**For OpenAI Python Client:**
```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:4000/v1",
    api_key="local"
)

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

## ⚙️ Configuration

Edit `router.py` to customize model assignments:

```python
MODELS = {
    "fast": "qwen2.5:3b",           # Quick answers
    "reasoning": "deepseek-r1:7b",   # Math & logic
    "coding": "qwen2.5-coder:7b",    # Programming
    "vision": "llava:7b",            # Images
    "general": "qwen2.5:7b"          # Default
}
```

Adjust to match your installed Ollama models!

## 📊 Routing Examples

### Example 1: Simple Query (→ Fast Model)
```
Query: "What is recursion?"
→ Routes to: qwen2.5:3b
→ Response time: ~2s
```

### Example 2: Complex Math (→ Reasoning Model)
```
Query: "Solve x^2 + 5x + 6 = 0 step by step"
→ Routes to: deepseek-r1:7b
→ Response time: ~40s (thorough reasoning)
```

### Example 3: Coding (→ Coding Model)
```
Query: "Write a Python function to sort a list"
→ Routes to: qwen2.5-coder:7b
→ Response time: ~5s
```

### Example 4: Image Analysis (→ Vision Model)
```
Query: "What's in this screenshot?"
→ Routes to: llava:7b
→ Response time: ~8s
```

### Example 5: General Discussion (→ General Model)
```
Query: "Explain machine learning concepts"
→ Routes to: qwen2.5:7b
→ Response time: ~10s
```

## 🔧 Advanced Usage

### Running as a Service (systemd)

Create `/etc/systemd/system/ollama-router.service`:

```ini
[Unit]
Description=Ollama Intelligent Router
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/ollama-router
ExecStart=/usr/bin/python3 /path/to/ollama-router/router.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable ollama-router
sudo systemctl start ollama-router
```

### Running as a Service (macOS)

Create `~/Library/LaunchAgents/com.user.ollama-router.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.ollama-router</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/path/to/ollama-router/router.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

Load it:
```bash
launchctl load ~/Library/LaunchAgents/com.user.ollama-router.plist
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY router.py .
RUN pip install fastapi uvicorn httpx

EXPOSE 4000
CMD ["python", "router.py"]
```

Build and run:
```bash
docker build -t ollama-router .
docker run -p 4000:4000 --network host ollama-router
```

### Environment Variables

```bash
# Change Ollama endpoint
export OLLAMA_BASE=http://localhost:11434

# Change router port
export PORT=4000
```

## 🧪 Testing

Test the router is working:

```bash
# Check health
curl http://localhost:4000/health

# Make a test request
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4",
    "messages": [{"role": "user", "content": "Hello!"}],
    "stream": false
  }'

# Watch routing decisions
tail -f router.log | grep "🔀"
```

## 📈 Performance

Based on benchmarks with Apple Silicon M4 (16GB RAM):

| Query Type | Model | Avg Time | Quality |
|------------|-------|----------|---------|
| Simple | 3B | 2s | Good |
| Coding | 7B | 5s | Excellent |
| Reasoning | 7B | 40s | Thorough |
| Vision | 7B | 8s | Good |
| General | 7B | 10s | Excellent |

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai) for making local LLMs accessible
- The open-source LLM community
- Model creators: Qwen, DeepSeek, Meta (Llama), and others

## ⚠️ Troubleshooting

### Router not starting
```bash
# Check if port 4000 is in use
lsof -i :4000

# Check if Ollama is running
curl http://localhost:11434/api/tags
```

### Models not found
```bash
# List installed models
ollama list

# Pull missing models
ollama pull qwen2.5:7b
```

### Slow responses
- Use smaller models for faster responses
- Adjust routing logic to prefer fast model
- Ensure Ollama has enough RAM

### Client connection errors
- Verify router is running: `curl http://localhost:4000/health`
- Check client base URL is set to `http://localhost:4000/v1`
- Try `127.0.0.1` instead of `localhost` if having DNS issues

## 🔗 Links

- [Ollama](https://ollama.ai)
- [Cursor](https://cursor.sh)
- [Continue](https://continue.dev)
- [FastAPI](https://fastapi.tiangolo.com)

---

**Made with ❤️ for the local LLM community**

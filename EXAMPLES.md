# Usage Examples

## Command Line Examples

### Using curl

#### Simple Query
```bash
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4",
    "messages": [
      {"role": "user", "content": "What is recursion?"}
    ]
  }'
```

#### Coding Query
```bash
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4",
    "messages": [
      {"role": "user", "content": "Write a Python function to reverse a string"}
    ]
  }'
```

#### Complex Reasoning
```bash
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4",
    "messages": [
      {"role": "user", "content": "Solve x^2 + 5x + 6 = 0 step by step"}
    ]
  }'
```

## Python Examples

### Using OpenAI Client

```python
from openai import OpenAI

# Initialize client pointing to local router
client = OpenAI(
    base_url="http://localhost:4000/v1",
    api_key="local"  # Any value works
)

# Simple query → Routes to fast model
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "What is Python?"}
    ]
)
print(response.choices[0].message.content)

# Coding query → Routes to coding model
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "Write a function to check if a number is prime"}
    ]
)
print(response.choices[0].message.content)

# Math query → Routes to reasoning model
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "Calculate the derivative of f(x) = x^3 + 2x^2 + x"}
    ]
)
print(response.choices[0].message.content)
```

### Streaming Responses

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:4000/v1",
    api_key="local"
)

# Stream response
stream = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Explain quantum computing"}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

### Multi-turn Conversation

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:4000/v1",
    api_key="local"
)

conversation = [
    {"role": "user", "content": "Write a simple web server in Python"},
    {"role": "assistant", "content": "Here's a simple Flask web server..."},
    {"role": "user", "content": "Now add authentication"}
]

response = client.chat.completions.create(
    model="gpt-4",
    messages=conversation
)

print(response.choices[0].message.content)
```

## LangChain Integration

```python
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

# Initialize LangChain with local router
chat = ChatOpenAI(
    openai_api_base="http://localhost:4000/v1",
    openai_api_key="local",
    model_name="gpt-4"
)

# Use it
messages = [
    SystemMessage(content="You are a helpful coding assistant"),
    HumanMessage(content="Write a function to find the largest element in a list")
]

response = chat(messages)
print(response.content)
```

## Cursor IDE Integration

### Setup
1. Open Cursor Settings (Cmd/Ctrl + ,)
2. Search for "OpenAI"
3. Set:
   - Base URL: `http://localhost:4000/v1`
   - API Key: `local`
4. Restart Cursor

### Usage

#### In-line Code Generation (Cmd+K)
```
Prompt: "Write a function to calculate fibonacci numbers"
→ Routes to: qwen2.5-coder:7b
→ Generates optimized code
```

#### Chat (Cmd+L)
```
You: "Explain how async/await works in JavaScript"
→ Routes to: qwen2.5:7b (general)
→ Provides detailed explanation
```

#### Complex Query
```
You: "Why does this algorithm have O(n log n) complexity?"
→ Routes to: deepseek-r1:7b (reasoning)
→ Provides step-by-step analysis
```

## Continue.dev Integration

Add to `~/.continue/config.json`:

```json
{
  "models": [
    {
      "title": "Local Ollama (Smart Routing)",
      "provider": "openai",
      "model": "gpt-4",
      "apiBase": "http://localhost:4000/v1",
      "apiKey": "local"
    }
  ]
}
```

Usage:
- Highlight code → Ask question → Routes to appropriate model
- `/edit` command → Routes to coding model automatically
- General questions → Routes to general model

## API Testing

### Check Health
```bash
curl http://localhost:4000/health
# {"status":"healthy"}
```

### List Models
```bash
curl http://localhost:4000/v1/models
# Returns OpenAI-compatible model list
```

### Check Routing
Watch the router logs to see routing decisions:
```bash
# Terminal 1: Start router
python router.py

# Terminal 2: Make requests
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4","messages":[{"role":"user","content":"test"}]}'

# Terminal 1 output:
# 🔀 Routing to: qwen2.5:3b
```

## Advanced Usage

### Custom Routing Override

You can force a specific model by modifying the router code or adding a custom header:

```python
# In router.py, add support for custom header
@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    # ... existing code ...
    
    # Check for override header
    force_model = request.headers.get("X-Force-Model")
    if force_model and force_model in MODELS.values():
        selected_model = force_model
    else:
        selected_model = select_model(messages)
```

Then use it:
```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:4000/v1", api_key="local")

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}],
    extra_headers={"X-Force-Model": "qwen2.5-coder:7b"}
)
```

### Load Balancing

For high-traffic scenarios, run multiple router instances:

```bash
# Terminal 1
python router.py --port 4000

# Terminal 2  
python router.py --port 4001

# Terminal 3
python router.py --port 4002
```

Then use a load balancer (nginx, HAProxy, etc.) to distribute requests.

### Monitoring

Add prometheus metrics:

```python
from prometheus_client import Counter, Histogram
import time

request_count = Counter('router_requests_total', 'Total requests')
request_duration = Histogram('router_request_duration_seconds', 'Request duration')

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    request_count.inc()
    start_time = time.time()
    
    # ... existing code ...
    
    request_duration.observe(time.time() - start_time)
```

## Troubleshooting Examples

### Test Each Model Individually

```bash
# Test fast model
curl -X POST http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen2.5:3b","messages":[{"role":"user","content":"test"}]}'

# Test coding model
curl -X POST http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen2.5-coder:7b","messages":[{"role":"user","content":"test"}]}'

# etc.
```

### Verify Ollama Connection

```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Check specific model
curl -X POST http://localhost:11434/api/show \
  -d '{"name":"qwen2.5:7b"}'
```

### Debug Router

Add debug logging to `router.py`:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    body = await request.json()
    logging.debug(f"Received request: {body}")
    
    selected_model = select_model(body["messages"])
    logging.debug(f"Selected model: {selected_model}")
    
    # ... rest of code ...
```

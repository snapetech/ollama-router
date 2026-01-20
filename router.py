#!/usr/bin/env python3
"""
Ollama Intelligent Router
==========================
An intelligent proxy that routes queries to different Ollama models based on content analysis.

Routes requests to specialized models:
- Simple queries → Fast small model
- Complex reasoning → Reasoning model
- Coding queries → Code-specialized model
- Visual queries → Vision model
- General queries → Balanced general model

Copyright (c) 2025
License: MIT
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
import httpx
import json
import re

app = FastAPI(title="Ollama Intelligent Router")

# Configuration - Customize these for your setup
OLLAMA_BASE = "http://localhost:11434"

# Model configuration - adjust to your installed models
MODELS = {
    "fast": "qwen2.5:3b",           # Small, fast model for simple queries
    "reasoning": "deepseek-r1:7b",   # Deep reasoning and math
    "coding": "qwen2.5-coder:7b",    # Code generation and debugging
    "vision": "llava:7b",            # Image analysis
    "general": "qwen2.5:7b"          # Balanced general-purpose
}

def select_model(messages: list) -> str:
    """
    Intelligently select the best model based on message content.
    
    Args:
        messages: List of message dictionaries with 'content' field
        
    Returns:
        str: Model name to use
    """
    # Combine all message content for analysis
    combined_text = " ".join([
        msg.get("content", "") 
        for msg in messages 
        if isinstance(msg.get("content"), str)
    ]).lower()
    
    # Check for images in messages (vision model)
    has_image = any(
        isinstance(msg.get("content"), list) and 
        any(isinstance(item, dict) and item.get("type") == "image_url" 
            for item in msg.get("content", []))
        for msg in messages
    )
    
    # Vision keywords
    vision_keywords = [
        'image', 'screenshot', 'picture', 'photo', 'diagram', 
        'visual', 'ui', 'design', 'chart', 'graph'
    ]
    if has_image or any(keyword in combined_text for keyword in vision_keywords):
        return MODELS["vision"]
    
    # Complex reasoning keywords
    reasoning_keywords = [
        'solve', 'proof', 'prove', 'calculate', 'compute', 'why does', 'why is',
        'because', 'reason', 'logic', 'theorem', 'equation', 'derivative',
        'integral', 'mathematical', 'mathematics', 'geometry', 'algebra',
        'explain why', 'how does', 'step by step', 'reasoning', 'analyze',
        'optimization', 'complexity', 'big o', 'time complexity'
    ]
    if any(keyword in combined_text for keyword in reasoning_keywords):
        return MODELS["reasoning"]
    
    # Fast model for simple/short queries
    simple_keywords = [
        'what is', 'what are', 'define', 'definition', 'meaning of', 
        'who is', 'when was', 'where is'
    ]
    if len(combined_text) < 100 or any(keyword in combined_text for keyword in simple_keywords):
        # But not if it's a coding or complex query
        coding_indicators = ['function', 'class', 'implement', 'code', 'algorithm']
        if not any(k in combined_text for k in coding_indicators):
            return MODELS["fast"]
    
    # Coding keywords
    coding_keywords = [
        'code', 'function', 'debug', 'implement', 'python', 'javascript',
        'typescript', 'java', 'rust', 'go', 'class', 'method', 'api',
        'bug', 'error', 'refactor', 'algorithm', 'sql', 'html', 'css',
        'react', 'component', 'import', 'export', 'async', 'await',
        'def ', 'const ', 'let ', 'var ', 'func ', '```', 'repository',
        'git', 'commit', 'pull request', 'npm', 'package', 'dependency',
        'compile', 'build', 'test', 'unittest', 'lint', 'syntax'
    ]
    if any(keyword in combined_text for keyword in coding_keywords):
        return MODELS["coding"]
    
    # Default to general model
    return MODELS["general"]

@app.get("/")
async def root():
    """Root endpoint with service info"""
    return {
        "service": "Ollama Intelligent Router",
        "version": "1.0.0",
        "models": MODELS
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.get("/v1/models")
async def list_models():
    """List available models (OpenAI-compatible endpoint)"""
    return {
        "object": "list",
        "data": [
            {
                "id": "gpt-4",
                "object": "model",
                "created": 1677610602,
                "owned_by": "local",
            },
            {
                "id": "gpt-4-turbo",
                "object": "model",
                "created": 1677610602,
                "owned_by": "local",
            },
            {
                "id": "gpt-3.5-turbo",
                "object": "model",
                "created": 1677610602,
                "owned_by": "local",
            },
            {
                "id": "claude-3-5-sonnet-20241022",
                "object": "model",
                "created": 1677610602,
                "owned_by": "local",
            }
        ]
    }

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    """
    Handle OpenAI-compatible chat completion requests.
    Routes to appropriate Ollama model based on content.
    """
    try:
        body = await request.json()
        messages = body.get("messages", [])
        stream = body.get("stream", False)
        
        # Select the best model for this query
        selected_model = select_model(messages)
        
        print(f"🔀 Routing to: {selected_model}")
        
        # Prepare request for Ollama
        ollama_body = {
            "model": selected_model,
            "messages": messages,
            "stream": stream,
            "options": body.get("options", {})
        }
        
        # Add temperature if specified
        if "temperature" in body:
            ollama_body["options"]["temperature"] = body["temperature"]
        
        # Forward request to Ollama
        async with httpx.AsyncClient(timeout=600.0) as client:
            if stream:
                # Handle streaming responses
                async def generate():
                    async with client.stream(
                        "POST",
                        f"{OLLAMA_BASE}/v1/chat/completions",
                        json=ollama_body
                    ) as response:
                        async for chunk in response.aiter_bytes():
                            yield chunk
                
                return StreamingResponse(
                    generate(),
                    media_type="text/event-stream"
                )
            else:
                # Handle non-streaming responses
                response = await client.post(
                    f"{OLLAMA_BASE}/v1/chat/completions",
                    json=ollama_body
                )
                
                # Check for errors
                if response.status_code != 200:
                    error_msg = f"Ollama returned {response.status_code}: {response.text[:500]}"
                    print(f"❌ Error: {error_msg}")
                    return JSONResponse(
                        {"error": error_msg},
                        status_code=response.status_code
                    )
                
                return JSONResponse(response.json())
                
    except httpx.TimeoutException as e:
        error_msg = f"Request timeout after 600s: {str(e)}"
        print(f"❌ Timeout Error: {error_msg}")
        return JSONResponse(
            {"error": error_msg},
            status_code=504
        )
    except Exception as e:
        import traceback
        error_msg = f"{type(e).__name__}: {str(e)}"
        print(f"❌ Error: {error_msg}")
        print(traceback.format_exc())
        return JSONResponse(
            {"error": error_msg},
            status_code=500
        )

@app.post("/v1/completions")
async def completions(request: Request):
    """Handle OpenAI-compatible text completion requests"""
    try:
        body = await request.json()
        prompt = body.get("prompt", "")
        
        # Route based on prompt
        selected_model = select_model([{"content": prompt}])
        
        print(f"🔀 Routing to: {selected_model}")
        
        # Forward to Ollama
        async with httpx.AsyncClient(timeout=600.0) as client:
            response = await client.post(
                f"{OLLAMA_BASE}/api/generate",
                json={
                    "model": selected_model,
                    "prompt": prompt,
                    "stream": False
                }
            )
            return JSONResponse(response.json())
            
    except Exception as e:
        import traceback
        error_msg = f"{type(e).__name__}: {str(e)}"
        print(f"❌ Error: {error_msg}")
        print(traceback.format_exc())
        return JSONResponse(
            {"error": error_msg},
            status_code=500
        )

if __name__ == "__main__":
    import uvicorn
    print("=" * 80)
    print("🧠 Ollama Intelligent Router")
    print("=" * 80)
    print(f"📍 Listening on: http://localhost:4000")
    print(f"🔗 Ollama endpoint: {OLLAMA_BASE}")
    print(f"")
    print(f"📊 Configured Models:")
    for category, model in MODELS.items():
        print(f"   {category:12} → {model}")
    print("")
    print("Set your AI client base URL to: http://localhost:4000/v1")
    print("=" * 80)
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=4000, log_level="info")

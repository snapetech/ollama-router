#!/bin/bash
# Quick setup script for Ollama Intelligent Router

set -e

echo "🚀 Ollama Intelligent Router Setup"
echo "=================================="
echo ""

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama not found. Please install from: https://ollama.ai"
    exit 1
fi

echo "✅ Ollama is installed"

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️  Ollama doesn't appear to be running"
    echo "   Start it with: ollama serve"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ Ollama is running"
fi

# Check installed models
echo ""
echo "📦 Checking installed models..."
INSTALLED_MODELS=$(ollama list 2>/dev/null | tail -n +2 | awk '{print $1}')

REQUIRED_MODELS=("qwen2.5:3b" "qwen2.5:7b" "qwen2.5-coder:7b" "deepseek-r1:7b")
MISSING_MODELS=()

for model in "${REQUIRED_MODELS[@]}"; do
    if echo "$INSTALLED_MODELS" | grep -q "^$model"; then
        echo "  ✅ $model"
    else
        echo "  ❌ $model (missing)"
        MISSING_MODELS+=("$model")
    fi
done

# Offer to install missing models
if [ ${#MISSING_MODELS[@]} -gt 0 ]; then
    echo ""
    echo "⚠️  Missing ${#MISSING_MODELS[@]} required model(s)"
    echo ""
    read -p "Download missing models now? This may take a while. (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        for model in "${MISSING_MODELS[@]}"; do
            echo "📥 Pulling $model..."
            ollama pull "$model"
        done
    else
        echo ""
        echo "⚠️  You can install them later with:"
        for model in "${MISSING_MODELS[@]}"; do
            echo "   ollama pull $model"
        done
    fi
fi

# Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
if command -v pip3 &> /dev/null; then
    pip3 install -r requirements.txt
elif command -v pip &> /dev/null; then
    pip install -r requirements.txt
else
    echo "❌ pip not found. Please install Python dependencies manually:"
    echo "   pip install fastapi uvicorn httpx"
    exit 1
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎯 Next steps:"
echo "   1. Start the router: python router.py"
echo "   2. Configure your AI client:"
echo "      Base URL: http://localhost:4000/v1"
echo "      API Key: local (any value works)"
echo "   3. Restart your AI client"
echo ""
echo "📚 For more info, see README.md"

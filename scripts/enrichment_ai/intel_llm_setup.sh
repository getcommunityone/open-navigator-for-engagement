#!/bin/bash
# Intel-Optimized LLM Setup for Arc Graphics + NPU
# For Intel Core Ultra 7 165H with 64GB RAM

set -e

echo "🚀 Setting up Intel-Optimized LLM Environment"
echo "Hardware: Intel Arc Graphics + NPU + 64GB RAM"
echo ""

# Check if running on Intel hardware
if ! lscpu | grep -q "Intel"; then
    echo "⚠️  Warning: This script is optimized for Intel hardware"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv-intel" ]; then
    echo "📦 Creating Intel-optimized virtual environment..."
    python3 -m venv .venv-intel
fi

source .venv-intel/bin/activate

# Install Intel Extension for PyTorch (IPEX-LLM)
echo "📥 Installing Intel Extension for PyTorch..."
pip install --upgrade pip setuptools wheel

# Install IPEX-LLM (Intel's optimized LLM library)
pip install intel-extension-for-pytorch
pip install oneccl_bind_pt --extra-index-url https://pytorch-extension.intel.com/release-whl/stable/cpu/us/

# Install LLM frameworks optimized for Intel
pip install transformers accelerate bitsandbytes optimum[openvino]

# Install DuckDB with extensions
echo "📥 Installing DuckDB with VSS extension..."
pip install duckdb
pip install duckdb-engine sqlalchemy

# Install Hugging Face datasets
pip install datasets huggingface_hub

# Install vector search libraries
pip install faiss-cpu sentence-transformers

# Install other dependencies
pip install loguru pandas pyarrow tqdm

echo ""
echo "✅ Intel-optimized environment ready!"
echo ""
echo "🎯 Performance Tips:"
echo "   1. Set environment variables before running:"
echo "      export ZES_ENABLE_SYSMAN=1"
echo "      export IPEX_LLM_NUM_GPU=1"
echo ""
echo "   2. Use OpenVINO backend for maximum Arc GPU performance:"
echo "      from optimum.intel import OVModelForCausalLM"
echo ""
echo "   3. For Ollama users, use Intel-optimized build:"
echo "      wget https://ollama.com/download/ollama-linux-amd64"
echo "      export OLLAMA_NUM_GPU=999"
echo ""
echo "📖 See scripts/legislative_analysis_intel.py for usage examples"

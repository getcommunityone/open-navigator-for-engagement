#!/bin/bash
set -e

echo "======================================================================"
echo "Installing Intel GPU Runtime for Arc Graphics"
echo "======================================================================"
echo ""
echo "This will install:"
echo "  1. Intel Compute Runtime (OpenCL + Level Zero)"
echo "  2. Intel Graphics Compiler"
echo "  3. oneAPI Level Zero Loader"
echo ""

# Check if running with sudo
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  This script needs sudo access to install system packages"
    echo "Please run: sudo ./scripts/enrichment_ai/setup_intel_gpu.sh"
    exit 1
fi

# Add Intel GPU repository
echo "📦 Adding Intel GPU package repository..."
wget -qO - https://repositories.intel.com/gpu/intel-graphics.key | \
    gpg --dearmor --output /usr/share/keyrings/intel-graphics.gpg

echo "deb [arch=amd64 signed-by=/usr/share/keyrings/intel-graphics.gpg] https://repositories.intel.com/gpu/ubuntu noble client" | \
    tee /etc/apt/sources.list.d/intel-gpu-noble.list

# Update package lists
echo "📦 Updating package lists..."
apt-get update

# Install Intel GPU runtime
echo "📦 Installing Intel Compute Runtime..."
apt-get install -y \
    intel-opencl-icd \
    intel-level-zero-gpu \
    level-zero \
    intel-media-va-driver-non-free \
    libmfx1 \
    libmfxgen1 \
    libvpl2

# Install development tools (optional but recommended)
echo "📦 Installing development tools..."
apt-get install -y \
    clinfo \
    vainfo

echo ""
echo "======================================================================"
echo "✅ Intel GPU Runtime Installed!"
echo "======================================================================"
echo ""

# Verify installation
echo "🔍 Verifying installation..."
echo ""

# Check OpenCL devices
if command -v clinfo &> /dev/null; then
    echo "OpenCL Devices:"
    clinfo -l || echo "No OpenCL devices found"
    echo ""
fi

# Check Level Zero devices
if [ -d "/dev/dri" ]; then
    echo "DRI Devices:"
    ls -la /dev/dri/
    echo ""
fi

# Check user groups
echo "Current user groups:"
groups $SUDO_USER
echo ""

# Add user to render and video groups if needed
if ! groups $SUDO_USER | grep -q render; then
    echo "📝 Adding user to 'render' group..."
    usermod -a -G render $SUDO_USER
    echo "✅ Added to render group (logout/login required)"
fi

if ! groups $SUDO_USER | grep -q video; then
    echo "📝 Adding user to 'video' group..."
    usermod -a -G video $SUDO_USER
    echo "✅ Added to video group (logout/login required)"
fi

echo ""
echo "======================================================================"
echo "🎯 Next Steps:"
echo "======================================================================"
echo ""
echo "1. Logout and login (or run: newgrp render)"
echo "2. Install XPU PyTorch:"
echo "   cd /home/developer/projects/open-navigator"
echo "   source .venv-intel/bin/activate"
echo "   ./scripts/enrichment_ai/install_xpu_pytorch.sh"
echo ""
echo "3. Test GPU access:"
echo "   python -c 'import torch; print(torch.xpu.is_available())'"
echo ""

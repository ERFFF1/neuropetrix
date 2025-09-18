#!/bin/bash

# NeuroPETrix v2.0 Installation Script
# Cross-platform installer for MONAI, PyTorch, and PyRadiomics

echo "🧠 NeuroPETrix v2.0 - AI Platform Kurulum Scripti"
echo "=================================================="
echo ""

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    echo "🖥️  Linux tespit edildi"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
    echo "🍎 macOS tespit edildi"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    OS="windows"
    echo "🪟 Windows tespit edildi"
else
    echo "❌ Desteklenmeyen işletim sistemi: $OSTYPE"
    exit 1
fi

# Check Python version
echo "🐍 Python versiyonu kontrol ediliyor..."
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
if [[ $? -ne 0 ]]; then
    echo "❌ Python3 bulunamadı. Lütfen Python 3.8+ kurun."
    exit 1
fi

echo "✅ Python $python_version bulundu"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🔧 Virtual environment oluşturuluyor..."
    python3 -m venv venv
    echo "✅ Virtual environment oluşturuldu"
else
    echo "✅ Virtual environment zaten mevcut"
fi

# Activate virtual environment
echo "🔌 Virtual environment aktifleştiriliyor..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  pip güncelleniyor..."
pip install --upgrade pip

# Install base requirements
echo "📦 Temel gereksinimler kuruluyor..."
pip install -r backend/requirements.txt

# OS-specific installations
echo "🔧 İşletim sistemi özel kurulumları..."

if [[ "$OS" == "linux" ]]; then
    echo "🐧 Linux özel kurulumları..."
    
    # Install system dependencies
    if command -v apt-get &> /dev/null; then
        echo "📦 apt paketleri kuruluyor..."
        sudo apt-get update
        sudo apt-get install -y python3-dev build-essential
    elif command -v yum &> /dev/null; then
        echo "📦 yum paketleri kuruluyor..."
        sudo yum groupinstall -y "Development Tools"
        sudo yum install -y python3-devel
    elif command -v pacman &> /dev/null; then
        echo "📦 pacman paketleri kuruluyor..."
        sudo pacman -S --noconfirm base-devel python-pip
    fi
    
elif [[ "$OS" == "macos" ]]; then
    echo "🍎 macOS özel kurulumları..."
    
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        echo "🍺 Homebrew kuruluyor..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    echo "📦 Homebrew paketleri kuruluyor..."
    brew install python3 cmake
    
elif [[ "$OS" == "windows" ]]; then
    echo "🪟 Windows özel kurulumları..."
    
    # Check if Visual Studio Build Tools are installed
    echo "⚠️  Windows için Visual Studio Build Tools gerekli olabilir"
    echo "   https://visualstudio.microsoft.com/visual-cpp-build-tools/"
fi

# Install AI-specific packages
echo "🤖 AI kütüphaneleri kuruluyor..."

# PyTorch installation
echo "🔥 PyTorch kuruluyor..."
if [[ "$OS" == "linux" ]]; then
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
elif [[ "$OS" == "macos" ]]; then
    pip install torch torchvision torchaudio
elif [[ "$OS" == "windows" ]]; then
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
fi

# MONAI installation
echo "🔬 MONAI kuruluyor..."
pip install monai

# PyRadiomics installation
echo "🧮 PyRadiomics kuruluyor..."
pip install pyradiomics

# Additional AI packages
echo "📊 Ek AI paketleri kuruluyor..."
pip install scikit-learn scikit-image opencv-python

# Install Streamlit and other frontend dependencies
echo "🌐 Frontend bağımlılıkları kuruluyor..."
pip install streamlit plotly pandas numpy

echo ""
echo "✅ Kurulum tamamlandı!"
echo ""
echo "🚀 Sistemi başlatmak için:"
echo "   1. Backend: make run-backend"
echo "   2. Frontend: make run-frontend"
echo ""
echo "🎭 Demo mode otomatik olarak aktif"
echo "📊 http://localhost:8501 adresinden erişim"
echo ""
echo "🧠 NeuroPETrix v2.0 hazır! 🎉"

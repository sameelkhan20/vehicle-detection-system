#!/bin/bash

# Vehicle Detection System - Deployment Script
# This script helps you deploy the system quickly

echo "🚗 Vehicle Detection System - Deployment Helper"
echo "=============================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

echo "✅ Docker is installed"

# Check if we're in the right directory
if [ ! -f "app.py" ] || [ ! -f "Dockerfile" ]; then
    echo "❌ Please run this script from the project directory"
    echo "   Make sure app.py and Dockerfile are present"
    exit 1
fi

echo "✅ Project files found"

# Ask user what they want to do
echo ""
echo "What would you like to do?"
echo "1. Build Docker image locally"
echo "2. Run Docker container locally"
echo "3. Deploy to Hugging Face Spaces (instructions)"
echo "4. Run with Docker Compose"
echo "5. Test the application"

read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        echo "🔨 Building Docker image..."
        docker build -t vehicle-detection .
        echo "✅ Docker image built successfully!"
        echo "   Run: docker run -p 5000:5000 vehicle-detection"
        ;;
    2)
        echo "🚀 Running Docker container..."
        docker run -p 5000:5000 vehicle-detection
        ;;
    3)
        echo "📋 Hugging Face Spaces Deployment Instructions:"
        echo ""
        echo "1. Create a GitHub repository and upload all files"
        echo "2. Go to https://huggingface.co/spaces"
        echo "3. Click 'Create new Space'"
        echo "4. Choose:"
        echo "   - Space name: vehicle-detection-system"
        echo "   - License: MIT"
        echo "   - SDK: Docker"
        echo "   - Hardware: CPU Basic (free)"
        echo "5. Connect your GitHub repository"
        echo "6. Wait for build to complete (5-10 minutes)"
        echo ""
        echo "✅ Your app will be live at: https://huggingface.co/spaces/your-username/vehicle-detection-system"
        ;;
    4)
        echo "🐳 Running with Docker Compose..."
        docker-compose up -d
        echo "✅ Application started with Docker Compose"
        echo "   Access at: http://localhost:5000"
        echo "   View logs: docker-compose logs -f"
        echo "   Stop: docker-compose down"
        ;;
    5)
        echo "🧪 Testing application..."
        if command -v python &> /dev/null; then
            python test_app.py
        else
            echo "❌ Python not found. Please install Python to run tests."
        fi
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again and choose 1-5."
        ;;
esac

echo ""
echo "🎉 Deployment helper completed!"
echo "   For more details, see README.md or DEPLOYMENT.md"

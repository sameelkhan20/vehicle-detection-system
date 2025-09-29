# 🚀 Deployment Guide

This guide will help you deploy the Vehicle Detection System to various platforms.

## 📋 Prerequisites

- Docker installed on your system
- Git installed
- A GitHub account (for Hugging Face Spaces)
- A Hugging Face account (for free hosting)

## 🌟 Option 1: Hugging Face Spaces (Recommended)

### Step 1: Prepare Your Repository
1. Create a new repository on GitHub
2. Upload all project files to the repository
3. Make sure the repository is public (required for free Hugging Face Spaces)

### Step 2: Create Hugging Face Space
1. Go to [Hugging Face Spaces](https://huggingface.co/spaces)
2. Click "Create new Space"
3. Fill in the details:
   - **Space name**: `vehicle-detection-system` (or your preferred name)
   - **License**: MIT
   - **SDK**: Docker
   - **Hardware**: CPU Basic (free tier)
4. Click "Create Space"

### Step 3: Connect GitHub Repository
1. In your Space settings, go to "Repository"
2. Connect your GitHub repository
3. The Space will automatically start building

### Step 4: Monitor Deployment
1. Check the "Logs" tab to monitor the build process
2. Wait for the build to complete (usually 5-10 minutes)
3. Once complete, your app will be available at: `https://huggingface.co/spaces/your-username/vehicle-detection-system`

## 🐳 Option 2: Local Docker Deployment

### Step 1: Build the Docker Image
```bash
# Clone the repository
git clone <your-repo-url>
cd vehicle-detection-system

# Build the Docker image
docker build -t vehicle-detection .
```

### Step 2: Run the Container
```bash
# Run with port mapping
docker run -p 5000:5000 vehicle-detection

# Or run with volume mounting for persistent storage
docker run -p 5000:5000 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/outputs:/app/outputs \
  -v $(pwd)/logs:/tmp/logs \
  vehicle-detection
```

### Step 3: Access the Application
- Open your browser and go to `http://localhost:5000`
- The application should be running

## 🐳 Option 3: Docker Compose

### Step 1: Create docker-compose.yml
The `docker-compose.yml` file is already included in the project.

### Step 2: Run with Docker Compose
```bash
# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

## ☁️ Option 4: Cloud Deployment

### AWS EC2
1. Launch an EC2 instance (t3.medium or larger recommended)
2. Install Docker on the instance
3. Clone your repository
4. Build and run the Docker container
5. Configure security groups to allow port 5000

### Google Cloud Platform
1. Create a Compute Engine instance
2. Install Docker
3. Deploy using the same Docker commands
4. Configure firewall rules

### Azure
1. Create a Virtual Machine
2. Install Docker
3. Deploy the application
4. Configure Network Security Groups

## 🔧 Configuration

### Environment Variables
You can customize the application using these environment variables:

```bash
# Flask configuration
FLASK_ENV=production
FLASK_APP=app.py

# Directory configuration
MPLCONFIGDIR=/tmp/matplotlib
YOLO_CONFIG_DIR=/tmp/ultralytics

# Python optimization
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1
```

### Resource Requirements
- **Minimum RAM**: 2GB
- **Recommended RAM**: 4GB+
- **CPU**: 2 cores minimum
- **Storage**: 5GB+ for models and temporary files

## 🚨 Troubleshooting

### Common Issues

**Build Fails**
- Check Docker logs for specific errors
- Ensure all dependencies are in requirements.txt
- Verify Dockerfile syntax

**Permission Denied**
- The app automatically handles permission issues
- Logs are stored in `/tmp` directory
- All directories are created with proper permissions

**Out of Memory**
- Increase container memory limits
- Use a larger instance
- Consider using GPU acceleration for better performance

**Port Already in Use**
- Change the port mapping: `-p 8080:5000`
- Kill existing processes using port 5000
- Use `docker ps` to check running containers

### Health Checks
The application includes built-in health checks:
- Health endpoint: `GET /health`
- Docker health check configured
- Automatic restart on failure

## 📊 Monitoring

### Logs
- Application logs are available in the container
- Use `docker logs <container-id>` to view logs
- Logs are also available in the Hugging Face Spaces interface

### Performance
- Monitor CPU and memory usage
- Check processing times for videos
- Optimize video file sizes for better performance

## 🔒 Security

### Production Considerations
- The Docker container runs as a non-root user
- All temporary files are stored in `/tmp`
- No sensitive data is stored in the container
- Health checks ensure the application is running

### Network Security
- Only expose necessary ports
- Use HTTPS in production
- Implement proper authentication if needed

## 📈 Scaling

### Horizontal Scaling
- Deploy multiple instances behind a load balancer
- Use container orchestration (Kubernetes, Docker Swarm)
- Implement session management for stateful operations

### Vertical Scaling
- Increase container resources
- Use more powerful instances
- Implement caching for better performance

## 🎯 Best Practices

1. **Always use the latest stable versions**
2. **Monitor resource usage regularly**
3. **Keep backups of important data**
4. **Test deployments in staging first**
5. **Use environment variables for configuration**
6. **Implement proper logging and monitoring**

## 📞 Support

If you encounter issues during deployment:
1. Check the troubleshooting section above
2. Review the application logs
3. Create an issue in the repository
4. Check the Hugging Face Spaces documentation

---

**Your Vehicle Detection System is now ready for deployment!** 🎉

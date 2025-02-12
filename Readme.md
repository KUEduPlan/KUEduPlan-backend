# EduPlan Setup Guide

## Prerequisites

Before setting up the project, ensure you have the following installed:
- SWI-Prolog
- MongoDB (with network access configured)
- Python 3.x

## Installation Steps

1. First, install SWI-Prolog according to your operating system:
   - For Ubuntu/Debian: `sudo apt-get install swi-prolog`
   - For macOS: `brew install swi-prolog`
   - For Windows: Download the installer from the [official website](https://www.swi-prolog.org/download/stable)

2. Clone the repository and navigate to the project directory:
```bash
git clone [repository-url]
cd eduplan
```

3. Create and activate a virtual environment:
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# For Linux/macOS:
source .venv/bin/activate
# For Windows:
.venv\Scripts\activate
```

4. Install required dependencies:
```bash
pip install -r requirements.txt
```

5. Configure environment variables:
   - Copy the `.env.example` file to create a new `.env` file
   - Update the values in `.env` with your configuration:
```bash
cp .env.example .env
```

6. Start the application:
```bash
uvicorn main:app --reload
```

The application should now be running at `http://localhost:8000`

## Environment Variables

Make sure to configure the following variables in your `.env` file:

```plaintext
MONGO_URL=

URL_REQUEST_TOKEN=
URL_VERIFY_TOKEN=

URL_PROGRAM_LIST=
URL_CURRI_PROGRAM_LIST=
URL_PLAN_LIST=
URL_STRUCTURE=
URL_SUBJECTS=
URL_PRECO_SUBJECTS=

URL_STUDENT_STATUS=
URL_STUDENT_ENROLL=
URL_STUDENT_GRADE=
URL_ENROLL_SEM=
```

## Troubleshooting

If you encounter any issues:

1. Ensure MongoDB is running and accessible
2. Verify SWI-Prolog is properly installed and accessible from command line
3. Check that all environment variables are properly set
4. Ensure all dependencies are installed correctly

# Web App Docker Deployment Guide

This guide will walk you through deploying the web application using Docker.

## Prerequisites

- Docker and Docker Compose installed on your system
- MongoDB installed and running
- Basic understanding of Docker concepts

## Configuration

1. Add a `environment` api service in docker-compose.yml

```
      environment:
          - MONGO_URL=
          - URL_REQUEST_TOKEN=
          - URL_VERIFY_TOKEN=
          - URL_PROGRAM_LIST=
          - URL_CURRI_PROGRAM_LIST=
          - URL_PLAN_LIST=
          - URL_STRUCTURE=
          - URL_SUBJECTS=
          - URL_PRECO_SUBJECTS=
          - URL_STUDENT_STATUS=
          - URL_STUDENT_ENROLL=
          - URL_STUDENT_GRADE=
          - URL_ENROLL_SEM=
```

2. Add a `environment` mongodb service in docker-compose.yml

```
    environment:
      MONGO_INITDB_ROOT_USERNAME: 
      MONGO_INITDB_ROOT_PASSWORD: 
```

## Deployment Steps

1. Build and start the containers:
```bash
docker compose up --build -d
```
The `--build` flag ensures fresh image builds
The `-d` flag runs containers in detached mode

2. Verify the deployment:
```bash
docker ps
```
You should see your containers running

## Troubleshooting

If you encounter issues:

1. Check MongoDB connection:
   - Ensure MongoDB is running
   - Check MongoDB logs: `docker logs mongodb-container`

2. View application logs:
```bash
docker logs your-app-container
```

## Stopping the Application

To stop and remove the containers:
```bash
docker compose down
```
FROM python:3.10-slim-buster

# Install OS libraries
RUN apt-get update && apt-get install -y \
    build-essential \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Create a directory where our app will be placed
RUN mkdir -p /usr/src/application

# Change directory so that our commands run inside this new directory
WORKDIR /usr/src/application

# Copy dependency definitions
COPY requirements.txt /usr/src/application

# Install project dependecies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Get all the code needed to run the app
COPY . /usr/src/application

# Change project dir
WORKDIR /usr/src/application/app

# Open port 
EXPOSE 8501

# Serve the app
CMD ["python3", "-u", "-m", "streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]

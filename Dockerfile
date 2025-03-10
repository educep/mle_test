# Use an official Python runtime as a parent image
FROM python:3.12-slim-bullseye

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV APP_HOME=/mle_test

# Set the working directory in the container
WORKDIR $APP_HOME

# Install system dependencies, including make and curl
RUN apt-get update && apt-get install -y --no-install-recommends \
    make \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the entire application code into the container
COPY . .

# Install uv
RUN make install_uv

# Add uv to PATH
ENV PATH="/root/.local/bin:${PATH}"

# Use system Python environment for uv
ENV UV_SYSTEM_PYTHON=1

# Install dependencies using uv with system Python
RUN make install

# Set the default command to run your pipeline (can be overridden)
CMD ["python", "main.py"]

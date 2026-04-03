# Use a lightweight Python base image
FROM python:3.10

# Set up a new user named "user" with user ID 1000 for Hugging Face Spaces security
RUN useradd -m -u 1000 user
USER user

# Set home and path environment variables
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Set the working directory inside the container
WORKDIR $HOME/app

# Copy the requirements file and install dependencies
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY --chown=user . .

# Hugging Face Spaces route traffic to port 7860
EXPOSE 7860

# Command to run the FastAPI application
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
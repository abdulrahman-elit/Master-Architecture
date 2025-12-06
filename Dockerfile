# Use a lightweight Python Linux image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first (for caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the API port
EXPOSE 8000

# Command to run the server
CMD ["uvicorn", "U4_Zero_Trust.main:app", "--host", "0.0.0.0", "--port", "8000"]
FROM python:3.12-slim

WORKDIR /app

# We skip build-essential for now to speed up the build
# If a package needs it, we will add it back later

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose the port FastAPI will run on
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

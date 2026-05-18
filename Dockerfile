FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gradio

COPY . .

EXPOSE 7860

CMD ["python", "app.py"]
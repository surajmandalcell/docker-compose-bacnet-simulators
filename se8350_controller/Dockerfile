FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY se8350_controller.py .

CMD ["python","-u", "se8350_controller.py"]
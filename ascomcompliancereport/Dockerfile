FROM python:3.8-slim-buster
WORKDIR /app
COPY generateUCSReport.py /app/generateUCSReport.py
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "/app/generateUCSReport.py"]
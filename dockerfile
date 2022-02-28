FROM python:3.8-slim
COPY requirements.txt .
RUN python3 -m pip install --upgrade pip
RUN pip install -r requirements.txt
COPY app /app
COPY static /static
EXPOSE 3000
CMD ["python3", "app/main.py"]
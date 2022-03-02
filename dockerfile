FROM python:3.8-slim
COPY requirements.txt .
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN python3 -m pip install --upgrade pip
RUN pip install -r requirements.txt
RUN mkdir main
COPY main.py /main
COPY app /main/app
COPY static /main/static
COPY wait-for-it.sh .
EXPOSE 3000
CMD ["python3", "main/main.py"]
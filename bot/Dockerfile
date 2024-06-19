FROM python:3.9.5

WORKDIR /bot
RUN pip install --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY . .

CMD ["python", "main.py"]

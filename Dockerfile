FROM python:slim

WORKDIR /src

COPY . /src

RUN pip install --no-cache-dir -r /src/requirements.txt

CMD ["python", "./main.py"]
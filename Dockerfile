FROM python:3.12
EXPOSE 8000
WORKDIR /usr/local/src/renova
RUN pip install --no-cache-dir --upgrade uvicorn
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY src .
CMD ["uvicorn", "--host=0.0.0.0", "--port=8000", "renova.app:app"]

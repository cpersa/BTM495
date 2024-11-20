FROM python:3.12 AS base
EXPOSE 8000
WORKDIR /usr/local/src/renova
RUN pip install --no-cache-dir --upgrade pip pip-tools uvicorn
COPY src/renova/__about__.py src/renova/__about__.py
COPY pyproject.toml README.md ./
RUN pip-compile && pip install --no-cache-dir --upgrade -r requirements.txt

FROM base
COPY . .
RUN pip install --no-cache-dir --upgrade --no-dependencies --editable .
CMD ["uvicorn", "--host=0.0.0.0", "--port=8000", "--reload", "renova.app.index:app"]

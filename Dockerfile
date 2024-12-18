FROM python:3.13-alpine AS base
EXPOSE 8080
WORKDIR /usr/local/src/renova
RUN apk add --no-cache --update nodejs npm &&\
    npm install tailwindcss &&\
    pip install --no-cache-dir --upgrade pip pip-tools uvicorn
COPY src/renova/__about__.py src/renova/__about__.py
COPY pyproject.toml README.md ./
RUN pip-compile && pip install --no-cache-dir --upgrade -r requirements.txt
COPY src/ src/
RUN ls ./ && pip install --no-cache-dir --upgrade --no-dependencies --editable .
COPY tailwind.config.js tailwind.config.js
RUN ls ./ && npx tailwindcss -i src/renova/main/styles.css -o static/styles.css

FROM base AS main
CMD ["uvicorn", "--proxy-headers", "--forwarded-allow-ips=*", "--host=0.0.0.0", "--port=8080", "--reload", "renova.main:app"]

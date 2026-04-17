FROM python:3.11-slim

WORKDIR /app

COPY fix_requirements.py requirements.txt ./

RUN python3 fix_requirements.py && pip install --no-cache-dir -r req_clean.txt

COPY . .

CMD ["python", "main.py"]

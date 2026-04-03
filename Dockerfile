FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot.py cv_generator.py job_search.py profile.py ./

CMD ["python", "bot.py"]

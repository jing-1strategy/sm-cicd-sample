FROM python:3-alpine
RUN pip install --no-cache-dir -U pip pipenv
COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock
RUN pipenv install --system --deploy

WORKDIR /app
COPY . /app
EXPOSE 5000
CMD ["python", "flaskblog.py"]
from python:3.7-buster

RUN apt update
RUN apt install -y poppler-utils imagemagick libmagickcore-6.q16-6-extra ghostscript netpbm gsfonts

COPY . /app
WORKDIR /app

RUN pip install pipenv

RUN pipenv install --system --deploy

CMD ["flask", "run", "--host", "0.0.0.0"]

FROM python:3.8
ENV PYTHONUNBUFFERED 1

ADD /STAC /STAC/
ADD requirements.txt /STAC/

WORKDIR /STAC
RUN pip install -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]

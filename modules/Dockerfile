FROM python:3.6.9
ADD . /app
WORKDIR /app
EXPOSE 8000
RUN pip3 install -r requirements.txt
ENTRYPOINT ["python","index.py"]
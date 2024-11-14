FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt --no-cache-dir
COPY . .
RUN sh buildnorun.sh
EXPOSE 8000
CMD ["dpsiw", "consume","-e","-i","3"]
#ENTRYPOINT ["tail", "-f", "/dev/null"]

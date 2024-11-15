FROM python:3.11-slim
WORKDIR /app
COPY /docker/startup /opt/startup
COPY /docker/startup/sshd_config /etc/ssh/
COPY requirements.txt requirements.txt
RUN echo "root:Docker!" | chpasswd \
    && echo "cd /code" >> /etc/bash.bashrc \
    && cd /opt/startup \
    && chmod 755 /opt/startup/init_container.sh \
    && cd /app \
    && pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .
RUN sh buildnorun.sh
EXPOSE 8000
#CMD ["dpsiw", "consume","-e","-i","3"]
#ENTRYPOINT ["/opt/startup/init_container.sh"]
ENTRYPOINT ["tail", "-f", "/dev/null"]

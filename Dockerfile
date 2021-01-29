from python:3.9-alpine
RUN apk add git build-base libxml2-dev libxslt-dev openssh
RUN addgroup -S sarathi && adduser -h /home/sarathi -S sarathi -G sarathi
USER sarathi
WORKDIR /home/sarathi
RUN mkdir /home/sarathi/app
COPY requirements.txt /home/sarathi/app/
WORKDIR /home/sarathi/app
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
RUN mkdir -p /home/sarathi/.ssh
COPY $HOME/.ssh/* /home/sarathi/.ssh
RUN git clone git@github.com:stonecharioteer/blog.git /home/sarathi/blog

COPY sarathi.py /home/sarathi/app/
COPY til.py /home/sarathi/app/
COPY requirements.txt /home/sarathi/app/

# ENV DISCORD_TOKEN
# ENV DISCORD_GUILD
ENV TIL_JSON_PATH="/home/sarathi/blog/assets/til.json"
ENV BLOG_PATH="/home/sarathi/blog/"


CMD ["python", "-u", "sarathi.py"]

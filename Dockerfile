from python:3.9-alpine
RUN apk add git build-base libxml2-dev libxslt-dev openssh
RUN addgroup -S sarathi && adduser -h /home/sarathi -S sarathi -G sarathi
USER sarathi
WORKDIR /home/sarathi
RUN mkdir /home/sarathi/app
COPY --chown=sarathi requirements.txt /home/sarathi/app/
WORKDIR /home/sarathi/app
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
RUN mkdir -p /home/sarathi/.ssh
COPY --chown=sarathi id_rsa /home/sarathi/app/
RUN ls
RUN git clone git@github.com:stonecharioteer/blog.git --config core.sshCommand="ssh -o 'StrictHostKeyChecking=no' -i /home/sarathi/app/id_rsa" /home/sarathi/blog
RUN chown -R sarathi:sarathi /home/sarathi/blog

COPY --chown=sarathi sarathi.py /home/sarathi/app/
COPY --chown=sarathi til.py /home/sarathi/app/
COPY --chown=sarathi requirements.txt /home/sarathi/app/

# ENV DISCORD_TOKEN
# ENV DISCORD_GUILD
ENV DISCORD_GUILD="stonecharioteer's server"
ENV TIL_JSON_PATH="/home/sarathi/blog/assets/til.json"
ENV TIL_JINJA_TEMPLATE_PATH="/home/sarathi/blog/assets/til.jinja2"
ENV TIL_FILE_PATH="/home/sarathi/blog/pages/til.md"
ENV BLOG_PATH="/home/sarathi/blog/"

RUN git config --global user.name "Vinay Keerthi"
RUN git config --global user.email "11478411+stonecharioteer@users.noreply.github.com"

CMD ["python", "-u", "sarathi.py"]

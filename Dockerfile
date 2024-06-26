FROM python:3.8.2-slim


WORKDIR app

ADD dnaStreaming ./dnaStreaming/
COPY ./LICENSE ./LICENSE
COPY ./MANIFEST.in ./MANIFEST.in
COPY ./CHANGELOG.md ./CHANGELOG.md
COPY ./requirements.txt ./requirements.txt
COPY ./setup.py ./setup.py
COPY ./tox.ini ./tox.ini
COPY ./README.rst ./README.rst

RUN ["pip", "install", "--upgrade", "pip", "setuptools", "wheel"]
RUN ["python", "setup.py", "install"]

CMD ["python", "./dnaStreaming/lb_ingest/lb_dj_streams.py", "-s"]

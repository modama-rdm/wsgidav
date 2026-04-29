# Dockerfile for https://github.com/mar10/wsgidav/
# Build:
#   docker build --rm -f Dockerfile -t mar10/wsgidav .
# Run:
#   docker run --rm -it -p <PORT>:8080 -v <ROOT_FOLDER>:/var/wsgidav-root mar10/wsgidav
# for example
#   docker run --rm -it -p 8080:8080 -v c:/temp:/var/wsgidav-root mar10/wsgidav
# Then open (or enter this URL in Windows File Explorer or any other WebDAV client)
#   http://localhost:8080/

# NOTE 2018-07-28: alpine does not compile lxml
# NOTE 2019-11-27: smallest image generated at the end
FROM debian:13-slim

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=target=/var/lib/apt/lists,type=cache,sharing=locked \
    apt-get -y update && apt-get -y install build-essential python3-dev \
    python3-venv python3-pip libpam0g libpam-runtime libpam-sss libnss-sss python3-sss

RUN --mount=type=cache,target=/root/.cache python3 -m venv /venv/

RUN --mount=type=cache,target=/root/.cache /venv/bin/python -m pip install cheroot python-pam lxml gunicorn

COPY . /code/

RUN ls -la /code/

RUN --mount=type=cache,target=/root/.cache /venv/bin/python -m pip install -U pip setuptools
RUN --mount=type=cache,target=/root/.cache /venv/bin/python -m pip install wheel gunicorn

RUN --mount=type=cache,target=/root/.cache /venv/bin/python -m pip install /code/
RUN mkdir -p /var/wsgidav-root

EXPOSE 8080

CMD ["/venv/bin/wsgidav", "--host", "0.0.0.0", "--port", "8080", "--root", "/var/wsgidav-root", "--auth=useronly", "--config", "/wsgidav.json", "--server", "gunicorn"]

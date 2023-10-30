FROM python:3.9

ENV DEBIAN_FRONTEND=non-interactive

ENV APP=/services/notebooks/

RUN mkdir -p $APP && \
    apt -q update && \
    apt -qy upgrade && \
    apt -qy install postgresql-client && \
    apt clean && \
    python3 -m venv /services/venv && \
    . /services/venv/bin/activate && \
    python -m pip install --upgrade pip && \
    useradd --user-group --system --create-home --no-log-init notebook

COPY docker/00_objectiv.sql  /services/
COPY docker/1_metabase_init.sql /services
COPY docker/2_metabase_data.sql /services

COPY requirements.txt /services

RUN . /services/venv/bin/activate && \
    pip install --upgrade setuptools wheel

RUN . /services/venv/bin/activate && \
    cd /services && \
    pip install --no-use-pep517 scikit-learn && \
    pip install -r requirements.txt


COPY docker/entrypoint.sh /
RUN chmod +x /entrypoint.sh

COPY product-analytics.ipynb $APP
COPY marketing-analytics.ipynb $APP

USER notebook
ENV OBJECTIV_VERSION_CHECK_DISABLE=false
ENTRYPOINT /entrypoint.sh

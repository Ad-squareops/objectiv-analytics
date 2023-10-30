FROM node:16-alpine

ARG PORT=8082

ARG SERVICES=/services
RUN mkdir $SERVICES

WORKDIR $SERVICES/validator
# copy sourcecode into image
COPY validator $SERVICES/validator

RUN cd  $SERVICES/validator && \
    yarn install

CMD yarn serve
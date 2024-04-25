FROM di-qa-docker-public.int.repositories.cloud.sap/di-qa-e2e-validation:latest
# FROM di-qa-docker-public.int.repositories.cloud.sap/di-qa-e2e-core:latest
# FROM 990498310577.dkr.ecr.eu-central-1.amazonaws.com/di-qa/di-qa-e2e-validation:1.0.0

ENV CLUSTER=CHAOS
ENV RUN_PATH=/project/
# ENV CASE_FILE_NAME=test_chaos.py
# ENV KEYWORD=test_
ENV RESULT=INIT

RUN mkdir -p /project
ADD . /project

WORKDIR /project
RUN chmod +x /project/entrypoint.sh

CMD /project/entrypoint.sh
#FROM python:3.8.6-alpine3.11
FROM python:3.8.6-slim-buster
ADD update_pull_request.py update_pull_request.py
RUN pip install PyGithub
RUN pip install regex
CMD /update_pull_request.py
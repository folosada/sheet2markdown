FROM opencvcourses/opencv:440

ARG FUNCTION_DIR="/var/task/"
WORKDIR ${FUNCTION_DIR}

RUN pip3 install --target ${FUNCTION_DIR} awslambdaric

ADD aws-lambda-rie /usr/local/bin/aws-lambda-rie
COPY script.sh requirements.txt app.py ./

RUN python3 -m pip install -r ./requirements.txt -t .

ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]
CMD ["app.lambda_handler"]
FROM python:3

WORKDIR /usr/src/app

COPY libs.txt ./libs.txt
RUN pip install -r ./libs.txt

RUN pip install hf_xet

COPY . .

CMD ["fastapi run main.py"]

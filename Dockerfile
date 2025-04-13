FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt

RUN pip install hf_xet

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

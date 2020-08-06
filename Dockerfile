FROM python:3.7-alpine

COPY bots/ViceInd_bot.py /bots/
COPY requirements.txt /tmp
RUN pip3 install -r /tmp/requirements.txt

WORKDIR /bots
CMD ["python3", "ViceInd_bot.py"]


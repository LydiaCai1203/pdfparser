FROM python:3.7-buster

WORKDIR /app

RUN  sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list

RUN apt-get update -y && apt-get -qq install tesseract-ocr libtesseract-dev libgl1

RUN pip install --default-timeout=120 --upgrade pip -i https://mirrors.aliyun.com/pypi/simple

RUN mkdir -p /app/model/8npt && \
    curl -L https://shanghai-9.zos.ctyun.cn/flashnews-public/statics/8npt/best.pt -o /app/model/8npt/best.pt

COPY ./requirements.txt /app

RUN pip install --no-cache-dir -r requirements.txt \
    && rm -f requirements.txt

RUN python3 -m pip install paddlepaddle -i https://mirror.baidu.com/pypi/simple

ADD . /app

EXPOSE 5555

CMD ["python", "main.py"]

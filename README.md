# pdfparser

```markdown
pdf 文字内容提取服务，不使用 GPU && 基于 YOLO && PaddleOCR。
支持容器部署 docker-compose。

本服务提供基本的 pdf/picture 内容识别，识别内容以数组形式返回。

TODO：
1. 表格返回格式凌乱，需要调整排版
2. 排版恢复，转为 docx 返回文件流
3. pdf/picture 转 html
```

## 0x01. QuickStart

```sh
docker-compose build

docker-compose up -d

# 使用的是 fastapi, swagger 地址为
http://127.0.0.1:5555/docs
```

## 0x02. Debug

```sh
python main.py

cd test && python test.py
```

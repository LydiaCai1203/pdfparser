import time
import base64
from io import StringIO, BytesIO

import fitz
from PIL import Image
from ultralytics import YOLO
from fastapi import APIRouter
from paddleocr import PaddleOCR
from pdfminer.high_level import extract_text_to_fp

from config import config, logger
from app.schema import GerneralResponse
from app.schema.pdf_parser import ParserSchema

router = APIRouter()

ocr = PaddleOCR(use_angle_cls=True, lang="ch")


@router.post("/content_extraction", response_model=GerneralResponse)
async def content_parsor(item: ParserSchema):
    """ 解析 pdf 的内容
    """
    response = GerneralResponse()
    
    start_ts = time.time()

    files = map(lambda x: b64_to_bytesio(x), item.base64_code)
    if item.extract_method == "fast" and item.code_of == "pdf":
        data = list(map(lambda x: simple_extract(x), files))
    elif item.extract_method == "best" and item.code_of == "pdf":
        model = load_mode(config.layout_model_path)
        pdf_imgs = map(lambda x: pdf2img(x), files)
        data = list(map(lambda x: ocr_extract([i for _, i in x.items()], model), pdf_imgs))
    elif item.extract_method == "best" and item.code_of == "picture":
        model = load_mode(config.layout_model_path)
        imgs = map(lambda x: Image.open(x), files)
        data = list(map(lambda x: ocr_extract([x], model), imgs))
    else:
        response.code = 400
        response.message = "illegal param"
        return response
    
    end_ts = time.time()
    logger.info(f"本次请求耗时 {end_ts - start_ts}s")

    response.data = {"content": data}
    return response

def simple_extract(pdf_file: BytesIO) -> str:
    logger.info("pdfminer.six 解析中...")
    output_string = StringIO()
    extract_text_to_fp(pdf_file, output_string)
    content = output_string.getvalue().strip()
    return content

def ocr_extract(img_file: list, model: YOLO) -> list:
    logger.info("ocr 文字识别中...")
    page_boxes = [extract_boxes(img, model) for img in img_file]
    page_content = [extract_text_from_boxes(boxes) for boxes in page_boxes]
    return page_content

def load_mode(model_name: str):
    logger.info("加载布局分析模型...")
    model = YOLO(model_name)
    return model

def b64_to_bytesio(b64_code: str) -> BytesIO:
    pdf_code = base64.b64decode(b64_code)
    pdf_file = BytesIO(pdf_code)
    return pdf_file

def pdf2img(pdf_file: BytesIO) -> dict:
    logger.info("pdf 转图片中...")
    rst = {}
    pdf_file = bytearray(pdf_file.read())
    doc = fitz.open("", pdf_file)
    for page in doc:
        pix = page.get_pixmap(dpi=500)
        image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        rst.update({page.number: image})
        # pix.save("page-%i.png" % page.number)
    return rst

# 有必要的话可以不提取 table 的内容，只提取 text 和 header 的内容
def extract_boxes(image: Image, model: YOLO) -> dict:
    rst = {}
    results = model(image)
    names = results[0].names
    labels = results[0].boxes.data.tolist()
    boxes = results[0].boxes.xyxy.cpu().tolist()
    for i, box in enumerate(boxes):
        x1, y1, x2, y2 = map(int, box)
        label_key = int(labels[i][-1])
        label_name = names[label_key]
        cropped_image = image.crop((x1, y1, x2+25, y2+45))  # (25，35) 是一些边界误差
        rst.update({i: {"image": cropped_image, "label": label_name, "position": (x1, y1, x2+25, y2+40)}})
    return rst

def extract_text_from_boxes(boxes: dict) -> list:
    global ocr

    rst = []
    for _, box in boxes.items():
        sub_image = box["image"]
        label = box["label"]
        position = box["position"]
        if label in ["Header", "Figure", "Reference"]:
            continue
        
        img_byte = BytesIO()
        sub_image.save(img_byte, format="PNG")
        result = ocr.ocr(img_byte.getvalue(), cls=True)
        
        # TODO: table 细致解析
        # TODO: Table picture 是否去要提取
        splitter = "\n" if label.lower() == "table" else ""
        text = splitter.join([result[idx][-1][0] for idx in range(len(result))])
        rst.append({"content": text, "position": position, "label": label})

    # 按照 position 进行排序(一些与正文内容无关的需要去除)
    rst = sorted(rst, key=lambda x: (x["position"][1], x["position"][0]))
    return rst

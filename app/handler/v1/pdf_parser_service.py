from paddleocr import PaddleOCR



ocr = PaddleOCR(use_angle_cls=True, lang="ch", det=False)
img_path = './pic/1.jpg'
result = ocr.ocr(img_path, cls=True)
content = "".join([result[idx][-1][0] for idx in range(len(result))])

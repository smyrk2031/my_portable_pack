import cv2
import numpy as np
import fitz  # PyMuPDF
from paddleocr import PaddleOCR
import pandas as pd
from pathlib import Path
import math

class PDFTableExtractor:
    def __init__(self):
        self.ocr = PaddleOCR(use_angle_cls=True, lang='japan', show_log=False)
    
    def preprocess_image(self, image):
        """画像の前処理を行う"""
        # グレースケール変換
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # ノイズ除去
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # 適応的二値化
        binary = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # エッジ検出
        edges = cv2.Canny(binary, 50, 150, apertureSize=3)
        
        # ハフ変換で直線検出
        lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)
        
        if lines is not None:
            angles = []
            for rho, theta in lines[:, 0]:
                angle = theta * 180 / np.pi
                if angle < 45 or angle > 135:  # 垂直に近い線のみ
                    angles.append(angle)
            
            if angles:
                median_angle = np.median(angles)
                if median_angle > 90:
                    median_angle -= 180
                
                if abs(median_angle) > 0.5:
                    height, width = image.shape[:2]
                    center = (width // 2, height // 2)
                    rotation_matrix = cv2.getRotationMatrix2D(center, median_angle, 1.0)
                    image = cv2.warpAffine(image, rotation_matrix, (width, height),
                                           flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        
        return image

    def extract_text_from_pdf(self, pdf_path):
        """PDFから文字列を抽出する"""
        results = []
        
        # PDFを画像に変換
        with fitz.open(pdf_path) as pdf:
            for page_num in range(len(pdf)):
                page = pdf[page_num]
                pix = page.get_pixmap()
                img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
                
                # 前処理
                processed_image = self.preprocess_image(img)
                
                # OCR実行
                ocr_result = self.ocr.ocr(processed_image)
                
                # 結果を座標情報付きで保存
                for line in ocr_result:
                    for word in line:
                        bbox = word[0]  # 座標情報
                        text = word[1][0]  # テキスト
                        confidence = word[1][1]  # 信頼度
                        
                        # 座標の中心点を計算
                        center_x = sum(p[0] for p in bbox) / 4
                        center_y = sum(p[1] for p in bbox) / 4
                        
                        results.append({
                            'text': text,
                            'x': center_x,
                            'y': center_y,
                            'confidence': confidence
                        })
        
        return results

    def organize_to_table(self, text_results, row_threshold=20):
        """抽出したテキストを表形式に整理"""
        # y座標でグループ化してテーブルの行を特定
        sorted_results = sorted(text_results, key=lambda x: x['y'])
        
        rows = []
        current_row = []
        last_y = None
        
        for result in sorted_results:
            if last_y is None or abs(result['y'] - last_y) <= row_threshold:
                current_row.append(result)
            else:
                if current_row:
                    current_row.sort(key=lambda x: x['x'])
                    rows.append([item['text'] for item in current_row])
                current_row = [result]
            last_y = result['y']
        
        if current_row:
            current_row.sort(key=lambda x: x['x'])
            rows.append([item['text'] for item in current_row])
        
        return rows

    def save_to_csv(self, table_data, output_path):
        """表データをCSVとして保存"""
        df = pd.DataFrame(table_data)
        df.to_csv(output_path, index=False, encoding='utf-8-sig')

def main():
    extractor = PDFTableExtractor()
    
    # 入力PDFパスと出力CSVパスの設定
    input_pdf = "input.pdf"  # 実際のパスに変更してください
    output_csv = "output.csv"  # 実際のパスに変更してください
    
    try:
        # テキスト抽出
        text_results = extractor.extract_text_from_pdf(input_pdf)
        
        # テーブルとして整理
        table_data = extractor.organize_to_table(text_results)
        
        # CSV保存
        extractor.save_to_csv(table_data, output_csv)
        print(f"Successfully converted {input_pdf} to {output_csv}")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    main()

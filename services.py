import google.generativeai as genai
import pandas as pd
import io
import json
import os
from dotenv import load_dotenv

# .env 파일에서 API 키 로드
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# API 키 확인
if not api_key:
    raise ValueError("API Key가 없습니다. .env 파일을 확인해주세요.")

genai.configure(api_key=api_key)

class AIService:
    def __init__(self):
        # flash 모델이 속도가 빠르고 엑셀 데이터 처리에 충분합니다.
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def text_to_excel(self, raw_text):
        """텍스트를 받아서 엑셀 파일(Binary)로 반환하는 함수"""
        
        # 1. 프롬프트 작성: JSON으로 데이터를 확실하게 뽑아내도록 지시
        prompt = f"""
        Extract data from the following text and format it as a JSON array of objects.
        Do not include any markdown formatting (like ```json). Just the raw JSON.
        Ensure all keys are consistent.
        
        [Text Data]
        {raw_text}
        """
        
        try:
            # 2. AI에게 요청
            response = self.model.generate_content(prompt)
            json_str = response.text.strip()
            
            # 혹시 모를 마크다운 기호 제거
            if json_str.startswith("```json"):
                json_str = json_str[7:]
            if json_str.endswith("```"):
                json_str = json_str[:-3]
                
            # 3. JSON -> DataFrame 변환
            data = json.loads(json_str)
            df = pd.DataFrame(data)
            
            # 4. DataFrame -> Excel (메모리 버퍼 사용)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Sheet1')
                
                # (선택) 열 너비 자동 조정
                worksheet = writer.sheets['Sheet1']
                for i, col in enumerate(df.columns):
                    worksheet.set_column(i, i, 20)
                    
            output.seek(0)
            return output

        except Exception as e:
            print(f"Error: {e}")
            return None
        
    def generate_notion_md(self, topic):
        """기능 3: 주제를 받아서 노션 호환 마크다운 텍스트 반환"""
        prompt = f"""
        주제: '{topic}'
        
        위 주제로 노션(Notion)에 붙여넣기 좋은 마크다운 문서를 작성해.
        
        [작성 규칙]
        1. 제목(#), 소제목(##, ###)을 명확히 구분해.
        2. 중요한 내용은 인용구(> ) 또는 콜아웃 스타일로 강조해.
        3. 할 일 목록(- [ ])이나 글머리 기호(-)를 적극적으로 사용해.
        4. 정보가 많으면 표(| 헤더 |)를 사용해서 정리해.
        5. 이모지를 많이 사용해서 문서를 예쁘게 꾸며줘.
        6. 서론, 본론, 결론 같은 말은 빼고 바로 내용만 출력해.
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error: {e}")
            return None
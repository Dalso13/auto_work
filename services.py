import pandas as pd
import io
import json
import re  # JSON 추출을 위한 정규표현식 라이브러리
from llm_wrapper import LLMWrapper  # <--- 핵심: 이제 직접 모델을 부르지 않고 래퍼를 씁니다.

class AIService:
    def __init__(self):
        # Gemini에 고정되지 않고, Wrapper를 통해 유연하게 호출합니다.
        self.llm = LLMWrapper()

    def text_to_excel(self, raw_text):
        """텍스트 -> 엑셀 변환 (유연한 구조 + JSON 에러 방지 적용)"""
        
        # 1. 프롬프트: JSON 포맷만 내놓으라고 강력하게 지시
        prompt = f"""
        Extract data from the text below and return ONLY a JSON array of objects.
        Do not include any markdown formatting (like ```json). Just the raw JSON.
        
        [Input Text]
        {raw_text}
        """
        
        try:
            # 2. Wrapper를 통해 AI에게 요청 (Gemini든 GPT든 상관없음)
            response_text = self.llm.generate(prompt)
            
            # --- [디버깅] 터미널에서 AI가 뭐라 했는지 확인하고 싶을 때 주석 해제 ---
            # print(f"\n[AI 응답]: {response_text}\n")
            
            # 3. JSON 정제 (강력한 에러 방지)
            # AI가 말주변이 많아서 "Here is the JSON..." 같은 사족을 붙일 때를 대비해
            # 대괄호 [ ... ] 안에 있는 내용만 강제로 끄집어냅니다.
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(0)
            else:
                # 대괄호를 못 찾았으면 전체 텍스트 시도 (혹시 모르니)
                json_str = response_text.replace("```json", "").replace("```", "").strip()

            # 4. JSON -> DataFrame 변환
            data = json.loads(json_str)
            df = pd.DataFrame(data)
            
            # 5. DataFrame -> Excel (메모리 버퍼)
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
            # 에러가 나면 터미널에 빨간 글씨로 원인을 알려줌
            print(f"❌ [Excel 변환 에러]: {e}")
            # 디버깅을 위해 원본 텍스트도 출력해봄
            if 'response_text' in locals():
                print(f"🔍 [AI 원본 응답]: {response_text}")
            return None
        
    def generate_notion_md(self, topic):
        """기능 3: 노션 마크다운 생성 (유연한 구조 적용)"""
        prompt = f"""
        주제: '{topic}'
        
        위 주제로 노션(Notion)에 붙여넣기 좋은 마크다운 문서를 작성해.
        
        [작성 규칙]
        1. 제목(#), 소제목(##, ###)을 명확히 구분해.
        2. 중요한 내용은 인용구(> ) 또는 콜아웃 스타일로 강조해.
        3. 할 일 목록(- [ ])이나 글머리 기호(-)를 적극적으로 사용해.
        4. 정보가 많으면 표(| 헤더 |)를 사용해서 정리해.
        5. 이모지를 사용은 금지해줘.
        6. 서론, 본론, 결론 같은 말은 빼고 바로 내용만 출력해.
        7. 개발자 문서 스타일로 작성해줘.
        """
        try:
            # 여기도 Wrapper 사용
            return self.llm.generate(prompt)
        except Exception as e:
            print(f"❌ [Notion 생성 에러]: {e}")
            return None
        
    # 기존 코드 아래에 추가
    def translate_text(self, text, direction, tone):
        """기능 4: 뉘앙스와 톤을 살린 AI 번역"""
        
        # 방향 설정
        if direction == "ko_to_en":
            target_lang = "English"
            source_lang = "Korean"
        else:
            target_lang = "Korean"
            source_lang = "English"

        # 프롬프트 구성 (여기가 핵심!)
        prompt = f"""
        Act as a professional translator.
        Translate the following {source_lang} text into {target_lang}.

        [Requirements]
        1. Tone & Style: {tone} (Apply this strictly).
        2. Preserve the original meaning but make it sound natural in the target language.
        3. Do not add any explanations, just the translated text.

        [Source Text]
        {text}
        """

        try:
            return self.llm.generate(prompt)
        except Exception as e:
            print(f"❌ [Translation Error]: {e}")
            return None
    # 기존 코드 아래에 추가
    def summarize_meeting(self, transcript):
        """기능: 회의 녹취록(txt)을 받아서 구조화된 회의록으로 정리"""
        
        prompt = f"""
        당신은 꼼꼼한 '전문 회의 서기'입니다.
        아래 대화 기록(Transcript)을 바탕으로 보고하기 좋은 완벽한 회의록을 작성하세요.

        [대화 기록]
        {transcript}

        [작성 양식]
        # 📅 회의 요약 보고서
        
        ## 1. 회의 개요
        - **주제:** (대화 내용으로 추론)
        - **참석자:** (대화에 등장하는 이름들 추론)

        ## 2. 주요 안건 (Agenda)
        - (논의된 핵심 주제들을 글머리 기호로 정리)

        ## 3. 핵심 결정 사항 (Key Decisions) ⭐중요
        - (결론이 난 사항이나 합의된 내용을 명확하게 기술)

        ## 4. 향후 행동 계획 (Action Items) 🏃
        - [담당자] 할 일 내용 (기한이 있다면 기한 포함)
        - [담당자] 할 일 내용

        ## 5. 기타 메모
        - (그 외 중요한 언급 사항이나 아이디어)

        [작성 규칙]
        - 말투는 '~함', '~했음' 처럼 간결한 개조식(Bullet points)으로 작성할 것.
        - 불필요한 추임새나 잡담은 모두 제거할 것.
        """
        
        try:
            return self.llm.generate(prompt)
        except Exception as e:
            print(f"❌ [Meeting Summary Error]: {e}")
            return None
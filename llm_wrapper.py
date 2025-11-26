import os
import google.generativeai as genai
# import openai  # 나중에 OpenAI 쓸 때 주석 해제

class LLMWrapper:
    def __init__(self):
        # .env에서 어떤 모델을 쓸지 가져옴 (기본값: gemini)
        self.provider = os.getenv("AI_PROVIDER", "gemini")
        self.api_key = os.getenv("API_KEY")

        if self.provider == "gemini":
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        elif self.provider == "openai":
            # self.client = openai.OpenAI(api_key=self.api_key)
            pass # 나중에 구현

    def generate(self, prompt):
        """
        어떤 모델이든 텍스트를 받아서 텍스트를 뱉는 함수로 통일
        """
        if self.provider == "gemini":
            response = self.model.generate_content(prompt)
            return response.text
            
        elif self.provider == "openai":
            # OpenAI 방식의 코드 (예시)
            # response = self.client.chat.completions.create(...)
            # return response.choices[0].message.content
            return "OpenAI 응답 (아직 구현 안됨)"
            
        else:
            raise ValueError(f"지원하지 않는 AI 모델입니다: {self.provider}")
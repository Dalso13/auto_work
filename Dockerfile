FROM python:3.11-slim

WORKDIR /app

# 1. 시스템 패키지 설치 (git 추가 필수!)
# - git: 소스코드 다운로드용
# - libgl1, libglib: 이미지/PDF 처리용
RUN apt-get update && apt-get install -y \
    git \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 2. 소스코드 가져오기
ARG REPO_URL
RUN git clone https://github.com/Dalso13/auto_work.git .

# 3. 라이브러리 설치
RUN pip install --no-cache-dir -r requirements.txt

# 4. 포트 열기
EXPOSE 5000

# 5. 실행
CMD ["python", "app.py"]
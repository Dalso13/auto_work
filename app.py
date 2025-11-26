from flask import Flask, render_template, request, send_file
from services import AIService

app = Flask(__name__)
ai_service = AIService()

# 1. 메인 대시보드
@app.route('/')
def index():
    return render_template('index.html')

# 2. 엑셀 생성 기능
@app.route('/excel', methods=['GET', 'POST'])
def excel_page():
    if request.method == 'POST':
        raw_text = request.form.get('raw_text')
        excel_file = ai_service.text_to_excel(raw_text)
        if excel_file:
            return send_file(excel_file, as_attachment=True, download_name='result.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        return "변환 실패"
    return render_template('excel.html') # 이 파일도 {% extends "base.html" %} 적용 필요

# 3. 노션 (준비 중)
@app.route('/notion', methods=['GET', 'POST'])
def notion_page():
    result = None
    if request.method == 'POST':
        topic = request.form.get('topic')
        # AI에게 마크다운 텍스트 생성 요청
        result = ai_service.generate_notion_md(topic)
    
    # 결과를 notion.html로 넘겨줌 (result가 있으면 결과 화면, 없으면 입력 화면)
    return render_template('notion.html', result=result)

# 4. 번역 (준비 중)
@app.route('/translator', methods=['GET', 'POST'])
def translator_page():
    result = None
    input_text = ""
    selected_direction = "ko_to_en" # 기본값
    selected_tone = "Business (Formal)" # 기본값

    if request.method == 'POST':
        input_text = request.form.get('input_text')
        selected_direction = request.form.get('direction')
        selected_tone = request.form.get('tone')
        
        # AI 번역 요청
        result = ai_service.translate_text(input_text, selected_direction, selected_tone)

    return render_template(
        'translator.html', 
        result=result, 
        input_text=input_text,
        selected_direction=selected_direction,
        selected_tone=selected_tone
    )
@app.route('/meeting', methods=['GET', 'POST'])
def meeting_page():
    result = None
    if request.method == 'POST':
        if 'file' not in request.files:
            return "파일이 없습니다."
        
        file = request.files['file']
        if file.filename == '':
            return "파일을 선택해주세요."

        # 1. 텍스트 파일 읽기 (인코딩 처리 중요!)
        try:
            # 먼저 utf-8로 시도
            transcript = file.read().decode('utf-8')
        except UnicodeDecodeError:
            # 실패하면 cp949 (윈도우 메모장 기본 저장 방식)로 재시도
            file.seek(0)
            transcript = file.read().decode('cp949')

        # 2. AI 요약 요청
        result = ai_service.summarize_meeting(transcript)

    return render_template('meeting.html', result=result)
if __name__ == '__main__':
    app.run(debug=True)
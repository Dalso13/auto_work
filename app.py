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

# 4. 변환 (준비 중)
@app.route('/converter')
def converter_page():
    return render_template('converter.html')

# 5. 번역 (준비 중)
@app.route('/translator')
def translator_page():
    return render_template('translator.html')

if __name__ == '__main__':
    app.run(debug=True)
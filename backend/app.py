import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from groq import Groq

# 환경 변수 로드
load_dotenv()

# Flask 앱 설정: 프로젝트 루트 기준으로 frontend 폴더를 static으로 설정
# backend/app.py 위치 기준 한 단계 위(root)의 frontend 폴더를 지정
current_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.path.join(os.path.dirname(current_dir), 'frontend')

app = Flask(__name__, static_folder=frontend_dir, static_url_path='')
CORS(app)

# Groq 클라이언트 초기화
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/api/convert', methods=['POST'])
def convert_tone():
    try:
        data = request.json
        text = data.get('text')
        target = data.get('target', 'upward') # PRD 기준 기본값: upward (상사)

        if not text:
            return jsonify({"error": "변환할 텍스트를 입력해주세요."}), 400

        # PRD 명칭에 맞춘 대상별 프롬프트 설정
        prompts = {
            "upward": (
                "당신은 대한민국 비즈니스 커뮤니케이션 전문가입니다. "
                "입력된 문장의 의도를 파악하여, 상사(Upward)에게 보고하기 적합한 격식 있고 정중한 현대 한국어 말투로 '재작성'해주세요. "
                "반드시 다음 지침을 엄격히 준수하세요:\n"
                "1. 입력 문장의 언어나 말투에 상관없이, 결과물은 무조건 완벽한 한국어(표준어)여야 합니다.\n"
                "2. 베트남어, 한자(Hanja)만 사용, 또는 다른 외국어를 섞는 행위를 절대 금지합니다.\n"
                "3. 결론부터 명확하게 제시하는 보고 형식을 유지할 것.\n"
                "4. 변환된 결과 이외의 설명이나 인사말은 생략할 것."
            ),
            "lateral": (
                "당신은 대한민국 비즈니스 커뮤니케이션 전문가입니다. "
                "입력된 문장의 의도를 파악하여, 타팀 동료(Lateral)에게 요청하거나 협업하기 적합한 친절하고 상호 존중하는 현대 한국어 말투로 '재작성'해주세요. "
                "반드시 다음 지침을 엄격히 준수하세요:\n"
                "1. 입력 문장의 언어나 말투에 상관없이, 결과물은 무조건 완벽한 한국어(표준어)여야 합니다.\n"
                "2. 베트남어, 한자(Hanja)만 사용, 또는 다른 외국어를 섞는 행위를 절대 금지합니다.\n"
                "3. 요청 사항과 기한을 명확하게 표현할 것.\n"
                "4. 변환된 결과 이외의 설명이나 인사말은 생략할 것."
            ),
            "external": (
                "당신은 대한민국 비즈니스 커뮤니케이션 전문가입니다. "
                "입력된 문장의 의도를 파악하여, 고객(External)에게 전달하기 적합한 극존칭을 사용한 매우 정중하고 공식적인 현대 한국어 말투로 '재작성'해주세요. "
                "반드시 다음 지침을 엄격히 준수하세요:\n"
                "1. 입력 문장의 언어나 말투에 상관없이, 결과물은 무조건 완벽한 한국어(표준어)여야 합니다.\n"
                "2. 베트남어, 한자(Hanja)만 사용, 또는 다른 외국어를 섞는 행위를 절대 금지합니다.\n"
                "3. 전문성과 서비스 마인드가 느껴지는 격식체를 사용할 것.\n"
                "4. 변환된 결과 이외의 설명이나 인사말은 생략할 것."
            )
        }

        system_prompt = prompts.get(target, prompts["upward"])

        # Groq API 호출
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0,
            max_tokens=1024,
        )

        converted_text = chat_completion.choices[0].message.content

        return jsonify({
            "original_text": text,
            "converted_text": converted_text,
            "target": target
        }), 200

    except Exception as e:
        app.logger.error(f"Error during conversion: {str(e)}")
        return jsonify({"error": "서버 내부 오류가 발생했습니다. 잠시 후 다시 시도해주세요."}), 500

if __name__ == '__main__':
    # 0.0.0.0으로 호스팅하여 외부 접근 허용
    app.run(debug=False, host='0.0.0.0', port=5000)

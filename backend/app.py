import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from groq import Groq

# 환경 변수 로드
load_dotenv()

app = Flask(__name__)
CORS(app)  # 프론트엔드와의 통신을 위해 CORS 허용

# Groq 클라이언트 초기화
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/api/convert', methods=['POST'])
def convert_tone():
    try:
        data = request.json
        text = data.get('text')
        target = data.get('target', '상사') # 기본값: 상사

        if not text:
            return jsonify({"error": "변환할 텍스트를 입력해주세요."}), 400

        # 대상별 프롬프트 설정
        prompts = {
            "상사": "당신은 비즈니스 커뮤니케이션 전문가입니다. 다음 문장을 상사에게 보고하기 적합한 격식 있고 정중한 말투로 변환해주세요. 불필요한 미사여구는 빼고 결론 위주로 작성하세요.",
            "동료": "당신은 비즈니스 커뮤니케이션 전문가입니다. 다음 문장을 타팀 동료에게 요청하거나 협업하기 적합한 정중하면서도 부드러운 말투로 변환해주세요.",
            "고객": "당신은 비즈니스 커뮤니케이션 전문가입니다. 다음 문장을 고객에게 전달하기 적합한 매우 정중하고 공식적인 말투로 변환해주세요."
        }

        system_prompt = prompts.get(target, prompts["상사"])

        # Groq API 호출 (Sprint 1: 기본 연동 테스트)
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": text,
                }
            ],
            model="llama3-8b-8192",
        )

        converted_text = chat_completion.choices[0].message.content

        return jsonify({
            "original": text,
            "converted": converted_text,
            "target": target
        }), 200

    except Exception as e:
        app.logger.error(f"Error during conversion: {str(e)}")
        return jsonify({"error": "서버 내부 오류가 발생했습니다. 잠시 후 다시 시도해주세요."}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

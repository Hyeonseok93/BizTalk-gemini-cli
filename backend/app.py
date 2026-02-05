import os
import logging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from groq import Groq

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Flask 앱 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.path.join(os.path.dirname(current_dir), 'frontend')
app = Flask(__name__, static_folder=frontend_dir, static_url_path='')
CORS(app)

# Groq 클라이언트 초기화
try:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        logger.warning("GROQ_API_KEY is not set in environment variables.")
    client = Groq(api_key=api_key)
except Exception as e:
    logger.error(f"Failed to initialize Groq client: {e}")
    client = None

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/api/convert', methods=['POST'])
def convert_tone():
    if not client:
        return jsonify({"error": "Server configuration error: AI client not available"}), 503

    try:
        data = request.json
        text = data.get('text')
        target = data.get('target', 'upward') # Default: 상사

        if not text:
            return jsonify({"error": "변환할 텍스트를 입력해주세요."}), 400

        # PRD 3.1 수신자 페르소나 기반 프롬프트 엔지니어링
        prompts = {
            "upward": (
                "역할: 당신은 대한민국 최고의 비즈니스 커뮤니케이션 전문가입니다.\n"
                "임무: 사용자의 입력 텍스트를 '상사(Upward)'에게 보고하기 적합한 형태로 변환하세요.\n"
                "핵심 가치: 보고의 명확성, 격식, 신뢰성.\n"
                "작성 지침:\n"
                "1. 톤앤매너: 정중한 격식체(하십시오체 위주)를 사용하세요.\n"
                "2. 구조: '결론'부터 명확하게 제시하는 두괄식 보고 형식을 취하세요.\n"
                "3. 내용: 불필요한 사족을 제거하고 핵심 내용을 간결하게 전달하세요.\n"
                "4. 주의: 오직 변환된 텍스트만 출력하세요. 설명이나 인사말을 덧붙이지 마세요."
            ),
            "lateral": (
                "역할: 당신은 대한민국 최고의 비즈니스 커뮤니케이션 전문가입니다.\n"
                "임무: 사용자의 입력 텍스트를 '타팀 동료(Lateral)'에게 전달하기 적합한 형태로 변환하세요.\n"
                "핵심 가치: 협업의 원활함, 요청의 명확성.\n"
                "작성 지침:\n"
                "1. 톤앤매너: 친절하고 상호 존중하는 해요체(합니다/해요)를 사용하세요.\n"
                "2. 구조: 협조 요청 형식을 갖추되, 요청 사항과 마감 기한(있다면)을 명확히 전달하세요.\n"
                "3. 내용: 부드럽지만 모호하지 않게 의사를 전달하세요.\n"
                "4. 주의: 오직 변환된 텍스트만 출력하세요. 설명이나 인사말을 덧붙이지 마세요."
            ),
            "external": (
                "역할: 당신은 대한민국 최고의 비즈니스 커뮤니케이션 전문가입니다.\n"
                "임무: 사용자의 입력 텍스트를 '고객(External)'에게 전달하기 적합한 형태로 변환하세요.\n"
                "핵심 가치: 서비스의 신뢰도, 친절함, 문제 해결.\n"
                "작성 지침:\n"
                "1. 톤앤매너: 극존칭을 사용하며, 전문성과 서비스 마인드가 느껴지도록 하세요.\n"
                "2. 구조: 안내, 공지, 사과 등 목적에 부합하는 격식 있는 형식을 취하세요.\n"
                "3. 내용: 고객의 입장을 배려하는 쿠션어(죄송하지만, 양해 부탁드립니다 등)를 적절히 활용하세요.\n"
                "4. 주의: 오직 변환된 텍스트만 출력하세요. 설명이나 인사말을 덧붙이지 마세요."
            )
        }

        system_prompt = prompts.get(target, prompts["upward"])
        
        # Sprint 3 목표 모델 사용: moonshotai/kimi-k2-instruct-0905
        # 만약 해당 모델이 Groq에서 지원되지 않는 경우를 대비해 예외처리 로직을 고려할 수 있으나, 
        # 현재는 요구사항에 따라 지정된 모델 ID를 사용합니다.
        model_id = "moonshotai/kimi-k2-instruct-0905"

        logger.info(f"Processing conversion request for target: {target}")

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            model=model_id,
            temperature=0.3, # 비즈니스 작문의 창의성과 일관성 균형
            max_tokens=1024,
        )

        converted_text = chat_completion.choices[0].message.content.strip()
        
        # 간혹 모델이 따옴표를 포함하거나 설명조로 시작할 경우를 대비한 간단한 정제
        if converted_text.startswith('"') and converted_text.endswith('"'):
            converted_text = converted_text[1:-1]

        return jsonify({
            "original_text": text,
            "converted_text": converted_text,
            "target": target
        }), 200

    except Exception as e:
        logger.error(f"Error during conversion: {str(e)}", exc_info=True)
        # 사용자에게 보여줄 친절한 에러 메시지
        return jsonify({"error": "AI 변환 서비스에 일시적인 문제가 발생했습니다. 잠시 후 다시 시도해주세요."}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
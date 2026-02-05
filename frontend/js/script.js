document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const sourceText = document.getElementById('sourceText');
    const recipient = document.getElementById('recipient');
    const convertBtn = document.getElementById('convertBtn');
    const resultBox = document.getElementById('resultText');
    const copyBtn = document.getElementById('copyBtn');
    const currentCharCount = document.getElementById('currentCharCount');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const feedbackSection = document.getElementById('feedbackSection');

    // API Endpoint - Flask 서버가 같은 오리진에서 서빙하므로 상대 경로 사용 가능
    const API_URL = '/api/convert';

    // 1. 실시간 글자 수 업데이트 (FR-04)
    sourceText.addEventListener('input', () => {
        const length = sourceText.value.length;
        currentCharCount.textContent = length;
        
        if (length >= 500) {
            currentCharCount.parentElement.style.color = '#D0021B';
        } else {
            currentCharCount.parentElement.style.color = '#999';
        }
    });

    // 2. 말투 변환 로직 (FR-01)
    convertBtn.addEventListener('click', async () => {
        const text = sourceText.value.trim();
        const target = recipient.value;

        if (!text) {
            alert('변환할 내용을 입력해주세요.');
            sourceText.focus();
            return;
        }

        // 상태 초기화
        setLoading(true);
        resultBox.textContent = '';
        copyBtn.disabled = true;
        feedbackSection.classList.add('hidden');

        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text, target })
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `서버 오류 (${response.status})`);
            }

            const data = await response.json();
            
            if (data.converted_text) {
                // 결과 표시
                resultBox.textContent = data.converted_text;
                copyBtn.disabled = false;
                // 피드백 영역 표시 (Want 요건)
                feedbackSection.classList.remove('hidden');
            } else {
                throw new Error('변환된 내용이 없습니다.');
            }

        } catch (error) {
            console.error('Error:', error);
            resultBox.innerHTML = `<span style="color: #D0021B;">오류: ${error.message}<br>잠시 후 다시 시도해주세요.</span>`;
        } finally {
            setLoading(false);
        }
    });

    // 3. 클립보드 복사 기능 (FR-03)
    copyBtn.addEventListener('click', async () => {
        const textToCopy = resultBox.textContent;
        if (!textToCopy) return;

        try {
            await navigator.clipboard.writeText(textToCopy);
            
            // 시각적 피드백
            const originalText = copyBtn.textContent;
            copyBtn.textContent = '✅ 복사되었습니다!';
            copyBtn.style.color = '#50E3C2';
            
            setTimeout(() => {
                copyBtn.textContent = originalText;
                copyBtn.style.color = '';
            }, 2000);
            
        } catch (err) {
            alert('복사에 실패했습니다.');
        }
    });

    // 4. 피드백 버튼 (FR-06)
    document.querySelectorAll('.feedback-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const type = btn.dataset.type;
            alert(type === 'positive' ? '좋은 피드백 감사합니다!' : '더 나은 서비스를 위해 노력하겠습니다.');
            feedbackSection.innerHTML = '<p style="color: #4A90E2; font-weight: 600;">피드백이 전달되었습니다. 감사합니다!</p>';
        });
    });

    // 로딩 상태 제어 함수
    function setLoading(isLoading) {
        if (isLoading) {
            loadingOverlay.classList.remove('hidden');
            convertBtn.disabled = true;
        } else {
            loadingOverlay.classList.add('hidden');
            convertBtn.disabled = false;
        }
    }
});

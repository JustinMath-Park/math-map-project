import json
import re  # ⭐ 이 줄 추가!
from config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)

class AIService:
    """AI 해설 및 분석 서비스"""
    
    def __init__(self, ai_client):
        self.ai_client = ai_client
    
    def generate_solution(self, problem_id, problem_text, correct_answer, db_solution=None):
        """문제 해설 생성 (일반 해설, user_answer 불필요)"""
        try:
            if db_solution:
                solution_guide = (
                    f"아래 '모범 풀이'를 기반으로 하되, 단순히 복사하지 말고, "
                    f"각 단계가 **'왜(Why)'** 그렇게 되는지 논리적인 이유를 덧붙여 단계별로 설명해주세요.\n\n"
                    f"**[참고용 모범 풀이]:** {db_solution}\n\n"
                )
            else:
                solution_guide = (
                    "모범 풀이가 제공되지 않았습니다. 문제를 직접 풀고, "
                    "학생이 이해할 수 있도록 **해당 공식이나 정리**가 왜 적용되었는지 설명하며 "
                    "단계별로 풀이 과정을 생성해주세요.\n\n"
                )

            user_prompt = (
                f"다음 문제의 정답은 {correct_answer}입니다. 이 답이 나오는 과정을 단계별로 설명해주세요.\n\n"
                f"**문제:** {problem_text}\n\n"
                f"**정답:** {correct_answer}\n\n"
                f"{solution_guide}"
                "**LaTeX 사용 규칙 (매우 중요!):**\n"
                "1. LaTeX는 숫자와 영문자만: $2x + 5 = 10$, $\\frac{{a}}{{b}}$\n"
                "2. 한글은 절대 LaTeX 안에 넣지 마세요!\n"
                "   - 잘못된 예: $시간당대여료$\n"
                "   - 올바른 예: 시간당 대여료는 $10t$입니다\n"
                "3. 수식만 LaTeX로, 설명은 일반 텍스트로\n"
                "4. HTML 태그 사용 금지: <br>, <strong> 등\n"
                "5. 마크다운 볼드는 가능: **굵게**\n\n"
                "**출력 형식:**\n"
                "- 불필요한 서론 없이 바로 풀이 시작\n\n"
                "지금 바로 풀이하세요:"
            )
            
            logger.info(f"AI 해설 생성 요청 - 문제 ID: {problem_id}")
            
            response = self.ai_client.models.generate_content(
                model=Config.MODEL_FLASH,
                contents=[
                    Config.SOLUTION_SYSTEM_PROMPT,
                    user_prompt
                ]
            )
            
            if response and hasattr(response, 'text') and response.text:
                # ⭐ 줄바꿈을 <br>로 변환하지 않고 그대로 반환
                solution = response.text
                # ⭐⭐⭐ AI 원본 응답 로깅 (중요!) ⭐⭐⭐
                logger.info("=" * 80)
                logger.info(f"[AI RAW RESPONSE START] 문제 ID: {problem_id}")
                logger.info("=" * 80)
                logger.info(solution)
                logger.info("=" * 80)
                logger.info(f"[AI RAW RESPONSE END] 문제 ID: {problem_id}")
                logger.info("=" * 80)
                
                # ⭐ 앞뒤 공백 제거
                solution = solution.strip()

                # HTML 태그 제거
                solution = re.sub(r'<br\s*/?>', '\n', solution)
                solution = re.sub(r'<[^>]+>', '', solution)

                # ⭐ 연속된 줄바꿈을 2개로 제한
                solution = re.sub(r'\n{3,}', '\n\n', solution)
                
                # 정제된 응답 로깅
                logger.info("-" * 80)
                logger.info(f"[AI CLEANED RESPONSE START] 문제 ID: {problem_id}")
                logger.info("-" * 80)
                logger.info(solution)
                logger.info("-" * 80)
                logger.info(f"[AI CLEANED RESPONSE END] 문제 ID: {problem_id}")
                logger.info("-" * 80)
                
                # <br> 태그 개수 확인
                br_count = len(re.findall(r'<br\s*/?>', solution))
                if br_count > 0:
                    logger.warning(f"⚠️  <br> 태그 {br_count}개 발견됨!")
                
                logger.info(f"AI 해설 생성 완료 - 문제 ID: {problem_id}")
                return solution

            else:
                logger.warning(f"AI 응답 형식 오류 - 문제 ID: {problem_id}")
                return "AI 해설 생성 중 문제가 발생했습니다."
                
        except Exception as e:
            logger.error(f"AI 해설 생성 실패 - 문제 ID: {problem_id}, 오류: {e}", exc_info=True)
            return f"AI 해설 생성 중 오류가 발생했습니다: {str(e)}"
    
    def analyze_weakness(self, wrong_categories, time_info=None):
        """약점 분석 (시간 정보 포함)"""
        try:
            if not wrong_categories:
                return "모든 문제를 맞추셨습니다! 훌륭해요!"

            logger.info(f"AI 약점 분석 요청 - {len(wrong_categories)}개 카테고리")

            # 시간 정보 문자열 생성
            time_context = ""
            if time_info:
                total_time = time_info.get('total_time_spent', 0)
                time_limit = time_info.get('time_limit', 1800)
                is_overtime = time_info.get('is_overtime', False)

                minutes = total_time // 60
                seconds = total_time % 60
                limit_minutes = time_limit // 60

                if is_overtime:
                    overtime_seconds = total_time - time_limit
                    overtime_minutes = overtime_seconds // 60
                    overtime_secs = overtime_seconds % 60
                    time_context = (
                        f"\n\n**시간 분석:**\n"
                        f"- 제한 시간: {limit_minutes}분\n"
                        f"- 실제 소요 시간: {minutes}분 {seconds}초\n"
                        f"- 초과 시간: {overtime_minutes}분 {overtime_secs}초\n"
                        f"- 학생이 제한 시간을 초과하여 문제를 풀었습니다. 시간 관리에 대한 조언도 포함해주세요.\n"
                    )
                else:
                    saved_seconds = time_limit - total_time
                    saved_minutes = saved_seconds // 60
                    saved_secs = saved_seconds % 60
                    time_context = (
                        f"\n\n**시간 분석:**\n"
                        f"- 제한 시간: {limit_minutes}분\n"
                        f"- 실제 소요 시간: {minutes}분 {seconds}초\n"
                        f"- 남은 시간: {saved_minutes}분 {saved_secs}초\n"
                        f"- 학생이 제한 시간보다 빠르게 문제를 풀었습니다. 이 점을 긍정적으로 언급해주세요.\n"
                    )

            user_prompt = (
                f"학생이 틀린 문제의 카테고리 리스트입니다: {json.dumps(wrong_categories, ensure_ascii=False)}\n"
                f"{time_context}\n"
                "학생의 약점을 진단하고 다음 학습을 추천해주세요."
            )

            response = self.ai_client.models.generate_content(
                model=Config.MODEL_FLASH,
                contents=[
                    Config.ANALYSIS_SYSTEM_PROMPT,
                    user_prompt
                ]
            )

            if response and hasattr(response, 'text') and response.text:
                # ⭐ 줄바꿈을 <br>로 변환하지 않고 그대로 반환
                analysis = response.text
                logger.info("AI 약점 분석 완료")
                return analysis
            else:
                logger.warning("AI 약점 분석 응답 형식 오류")
                return "AI 약점 분석 중 문제가 발생했습니다."

        except Exception as e:
            logger.error(f"AI 약점 분석 실패: {e}", exc_info=True)
            return f"AI 약점 분석 중 오류가 발생했습니다: {str(e)}"
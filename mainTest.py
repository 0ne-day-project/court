from typing import TypedDict
from langgraph.graph import StateGraph, START, END


class DebateState(TypedDict):
    topic: str               # 사용자 입력 주제
    supporter_args: str      # 소희(Supporter) 담당
    skeptic_args: str        # 지인(Skeptic) 담당
    fact_check_result: str   # 구거니(Fact Checker) 담당
    final_verdict: str       # 우진(Judge) 담당

# ==========================================
# 2. 배관 테스트용 가짜(Mock) 노드들
# (나중에 팀원들이 진짜 LLM 연동 코드를 짜오면 여기를 교체함)
# ==========================================
def mock_supporter(state: DebateState):
    print("[실행 중] Supporter가 찬성 논리를 생성합니다...")
    return {"supporter_args": "찬성 근거: 업무 효율성 증가, 직원 만족도 향상 (임시 데이터)"}

def mock_skeptic(state: DebateState):
    print("[실행 중] Skeptic이 반대 논리를 생성합니다...")
    return {"skeptic_args": "반대 근거: 인건비 부담, 업무 연속성 단절 (임시 데이터)"}

def mock_fact_checker(state: DebateState):
    print("[실행 중] Fact Checker가 양측 주장을 검증합니다...")
    # 실제로는 state["supporter_args"]와 state["skeptic_args"]를 읽어서 검증함
    return {"fact_check_result": "팩트 체크 완료: 양측 근거 모두 논리적 오류 없음 (임시 데이터)"}

def mock_judge(state: DebateState):
    print("[실행 중] Judge이 최종 판결을 내립니다...")
    return {"final_verdict": "최종 판결: 조건부 도입을 권장함 (임시 데이터)"}

# ==========================================
# 3. 팔거니 전용: LangGraph 흐름 조립
# ==========================================
def build_graph():
    # 그래프 초기화 (정의한 State 바구니 적용)
    workflow = StateGraph(DebateState)

    # 노드 등록
    workflow.add_node("supporter", mock_supporter)
    workflow.add_node("skeptic", mock_skeptic)
    workflow.add_node("fact_checker", mock_fact_checker)
    workflow.add_node("judge", mock_judge)

    # 엣지(흐름) 연결
    # 1단계: 시작하자마자 소희와 지인이 병렬로 실행됨
    workflow.add_edge(START, "supporter")
    workflow.add_edge(START, "skeptic")

    # 2단계: 소희와 지인의 작업이 모두 끝나면 구거니에게 넘어감
    workflow.add_edge("supporter", "fact_checker")
    workflow.add_edge("skeptic", "fact_checker")

    # 3단계: 구거니의 팩트 체크가 끝나면 우진이에게 넘어감
    workflow.add_edge("fact_checker", "judge")

    # 4단계: 우진이의 판결이 끝나면 전체 프로세스 종료
    workflow.add_edge("judge", END)

    # 그래프 컴파일
    return workflow.compile()

# ==========================================
# 4. 메인 실행부
# ==========================================
if __name__ == "__main__":
    print("🚀 [시스템 시작] AI 토론 파이프라인 가동\n" + "="*40)

    # 팔거니가 그래프 생성
    app = build_graph()

    # 사용자의 초기 입력값
    initial_input = {"topic": "주 4일제 도입은 기업 생산성을 떨어뜨리는가?"}

    # 그래프 실행 (invoke)
    final_state = app.invoke(initial_input)

    print("\n" + "="*40)
    print("🌟 [최종 결과] 바구니(State)에 담긴 모든 데이터 출력")
    print("="*40)

    # 결과물을 예쁘게 출력
    for key, value in final_state.items():
        print(f"[{key}]:\n{value}\n")
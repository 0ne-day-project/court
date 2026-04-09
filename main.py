from typing import TypedDict
from langgraph.graph import StateGraph, START, END

# [팀원들의 진짜 노드 함수 불러오기]
# 팀원들이 nodes 폴더 안의 각 파일에 '본인역할_node'라는 이름으로 함수를 짰다고 가정함
from nodes.supporter import supporter_node
from nodes.skeptic import skeptic_node
from nodes.fact_checker import fact_checker_node
from nodes.judge import judge_node


# ==========================================
# 1. 팔거니 전용: State (데이터 규격) 정의
# ==========================================
class DebateState(TypedDict):
    topic: str  # 사용자 입력 주제
    supporter_args: str  # 소희(Supporter) 담당 결과물
    skeptic_args: str  # 지인(Skeptic) 담당 결과물
    fact_check_result: str  # 구거니(Fact Checker) 담당 결과물
    final_verdict: str  # 우진(Judge) 담당 결과물


# ==========================================
# 2. 팔거니 전용: LangGraph 흐름 조립
# ==========================================
def build_graph():
    # 그래프 초기화 (정의한 State 바구니 적용)
    workflow = StateGraph(DebateState)

    # 노드 등록 (가짜 함수 대신 팀원들의 진짜 함수를 넣음!)
    workflow.add_node("supporter", supporter_node)
    workflow.add_node("skeptic", skeptic_node)
    workflow.add_node("fact_checker", fact_checker_node)
    workflow.add_node("judge", judge_node)

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
# 3. 메인 실행부
# ==========================================
if __name__ == "__main__":
    print("🚀 [시스템 시작] 진짜 AI 토론 파이프라인 가동\n" + "=" * 40)

    # 팔거니가 그래프 생성
    app = build_graph()

    # 사용자의 초기 입력값
    initial_input = {"topic": "최근 한화이글스는 경기를 우승했다."}

    # 그래프 실행 (invoke) - 여기서 팀원들의 LLM이 실제로 작동함!
    final_state = app.invoke(initial_input)

    print("\n" + "=" * 40)
    print("🌟 [최종 결과] 바구니(State)에 담긴 모든 데이터 출력")
    print("=" * 40)

    # 결과물을 예쁘게 출력
    for key, value in final_state.items():
        print(f"[{key}]:\n{value}\n")
        print("-" * 30)
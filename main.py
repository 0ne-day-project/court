from langgraph.graph import StateGraph, START, END
from court.schema import DebateState

# 노드들 불러오기
from court.nodes.supporter import supporter_node
from court.nodes.skeptic import skeptic_node
from court.nodes.fact_checker import fact_checker_node
from court.nodes.judge import judge_node


def build_debate_graph():
    # 1. 그래프 뼈대 생성
    workflow = StateGraph(DebateState)

    # 2. 노드 등록
    workflow.add_node("supporter", supporter_node)
    workflow.add_node("skeptic", skeptic_node)
    workflow.add_node("fact_checker", fact_checker_node)
    workflow.add_node("judge", judge_node)

    # 3. 흐름(Edge) 연결
    workflow.add_edge(START, "supporter")
    workflow.add_edge(START, "skeptic")

    # 🚨 안전하게 두 줄로 풀어서 작성 (병렬 처리 후 모임)
    workflow.add_edge("supporter", "fact_checker")
    workflow.add_edge("skeptic", "fact_checker")

    # 팩트체크가 끝나면 판사에게 전달
    workflow.add_edge("fact_checker", "judge")

    # 4. 조건부 흐름 (판결에 따라 토론을 끝낼지, 다시 할지 결정)
    def should_continue(state: DebateState):
        if state.get("is_conclusive", False):  # 판사가 '종결'을 선언했다면
            return END
        else:
            return ["supporter", "skeptic"]

    # 🚨 경로 맵핑 딕셔너리(path_map)를 아예 삭제해서 리스트 에러 원천 차단!
    workflow.add_conditional_edges("judge", should_continue)

    # 그래프 완성
    return workflow.compile()


if __name__ == "__main__":
    print("[시스템 시작] AI 재판이 시작됩니다. ")
    print("=" * 40)

    app = build_debate_graph()

    # 판사가 찾던 'iteration'을 0으로 명시적 초기화
    initial_input = {
        "topic": "이번 대통령 선거가 부정선거인가?",
        "iteration": 0
    }

    # 대망의 실행!
    final_state = app.invoke(initial_input)

    print("\n" + "=" * 40)
    print("🎉 [시스템 종료] 최종 판결문이 도착했습니다!")
    print("=" * 40)
    print(final_state.get("final_verdict", "판결문을 가져오지 못했습니다."))
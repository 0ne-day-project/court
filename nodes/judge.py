import os
from langchain_openai import ChatOpenAI
from court.schema import DebateState


def judge_node(state: DebateState):
    current_iteration = state.get("iteration", 0)

    print(f"⚖️ [실행 중] 판사(Judge)가 {current_iteration + 1}번째 판결을 내립니다...")

    llm = ChatOpenAI(
        temperature=0.2,
        model_name="gpt-5-mini",
        openai_api_key=os.getenv("OPENAI_API_KEY"),
    )

    context = f"""
    [토론 주제]: {state.get('topic', '')}
    - 찬성측(소희): {state.get('supporter_args', '')}
    - 반대측(지인): {state.get('skeptic_args', '')}
    - 팩트체크(구거니): {state.get('fact_check_result', '')}
    """

    prompt = f"""
    당신은 공정하고 엄격한 판사입니다. 아래 토론을 보고 최종 판결을 내리세요.
    {context}
    조건: 승패를 명확히 가릴 수 있다면 판결문 어딘가에 '종결' 이라는 단어를 꼭 포함하세요.
    """
    response = llm.invoke(prompt)

    is_done = "종결" in response.content or current_iteration >= 2

    # 🚨 종결 시 티 내기!
    if is_done:
        print("⚖️ [판사] 탕탕탕! 토론 종결을 선언합니다.")

    return {
        "final_verdict": response.content,
        "is_conclusive": is_done,
        "iteration": current_iteration + 1
    }
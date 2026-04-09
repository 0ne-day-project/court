from langchain_openai import ChatOpenAI
import os

def judge_node(state: DebateState):
    
    llm = ChatOpenAI(
        temperature=0.2,
        model_name="gpt-5-mini", 
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )  
    context = f"""
    [토론 주제]: {state['topic']}
    - 찬성측(소희): {state['supporter_args']}
    - 반대측(지인): {state['skeptic_args']}
    - 팩트체크(구거니): {state['fact_check_result']}
    """

    prompt = f"""
    당신은 공정하고 엄격한 판사입니다. 아래 토론을 보고 최종 판결을 내리세요.
    {context}
    조건: 
    """
    response = llm.invoke(prompt)

    # 4. 결과 업데이트 (바구니에 담기만 함, 출력 X)
    # 3라운드 이상이거나 판결문에 '종결'이 포함되면 끝내기로 설정
    is_done = "종결" in response.content or state['iteration'] >= 2

    return {
        "final_verdict": response.content,
        "is_conclusive": is_done,
        "iteration": state["iteration"] + 1
    }
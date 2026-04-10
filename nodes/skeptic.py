import os
import sys
from langchain_openai import ChatOpenAI
from tavily import TavilyClient
from dotenv import load_dotenv

# 단독 테스트를 위한 경로 마법
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from court.schema import DebateState

# 환경 변수 로드
load_dotenv()

# 🚨 API 설정 (소희랑 똑같이 base_url 추가해서 에러 방지!)
llm = ChatOpenAI(
    model="gpt-5-mini",
    api_key=os.getenv("OPENAI_API_KEY"),
)

# Tavily 클라이언트 명시적 초기화
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


# 노드 함수 (dict 대신 DebateState 규격 적용!)
def skeptic_node(state: DebateState) -> dict:
    print("🔴 [실행 중] 지인(Skeptic)이 반대 논리를 생성합니다...")

    topic = state.get("topic")

    # 검색어 설정
    search_prompt = f"""
    당신은 주제에 대한 검색 키워드를 설정하는 역할입니다.

    {topic}에 대한 반대 입장의 이유 및 근거를 인터넷에서 하나의 검색어로 찾아봐야 할 때 가장 적합한 검색어를 제시해야 합니다.

    답변시에는 추천한 이유, 다른 사족을 추가하지 않고 **검색어만** 제시해주세요
    """

    print("🔍 [Skeptic 검색어 생성 중...]")
    search_keyword = llm.invoke(search_prompt).content

    # tavily 실행
    print(f"🔍 [검색 중] Tavily로 반대 근거를 검색합니다 (키워드: {search_keyword})")
    search_result = tavily.search(query=search_keyword, search_depth="advanced", max_results=3)

    summary_search = "\n\n---\n\n".join([_['content'] for _ in search_result['results']])

    # 근거 제시 프롬프트 생성
    argument_prompt = f"""
    당신은 토론에서 반대의 의견을 제시하는 skeptic입니다.
    토론의 주제에 대해 비판적인 입장에서 논리적으로 근거를 제시해야 합니다.


    아래는 토론의 주제입니다.
    {topic}

    아래는 해당 주제에 대해 반대하는 이유에 대한 인터넷 검색 결과입니다.
    {summary_search}


    위 주제와 검색결과를 바탕으로 아래의 원칙을 준수하며 답변하세요.
    - 이유를 최소한 2가지 이상 제시하세요.
    - 각 이유에 대한 근거를 구체적으로 제시하세요.
    - 감정적인 호소가 아닌, 철저히 데이터와 검색자료를 기반으로 이성적으로 주장하세요.
    - 상대방의 반론을 예상하고 미리 반박 포인트를 준비하세요
    - 같은 내용을 2번 이상 반복하지 않고 각 주장의 논지와 이유, 또는 반박 등만 간결하게 제시하세요

    출력 형식:
    ## 핵심 주장
    [주제에 대한 반대 입장 한 문장 요약]

    ## 주요 논거
    1. [논거 1]
        - 근거: [구체적 근거/예시]

    2. [논거 2]
       - 근거: [구체적 근거/예시]

    3. [논거 3]
        - 근거: [구체적 근거/예시]

    ## 예상 반론에 대한 선제적 반박
    [반론 예상 및 대응 논리]
    """

    response = llm.invoke(argument_prompt).content

    # 규격에 맞게 리턴
    return {"skeptic_args": response}


# 테스트용 코드
if __name__ == "__main__":
    test_state = {"topic": "주 4일제 도입은 기업 생산성을 떨어뜨리는가?"}
    result = skeptic_node(test_state)
    print("\n" + "=" * 50)
    print("🔴 Skeptic 결과:")
    print("=" * 50)
    print(result["skeptic_args"])
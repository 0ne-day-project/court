import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from tavily import TavilyClient
from court.schema import DebateState

# 환경 변수 로드
load_dotenv()

# LLM 초기화 (OpenRouter)
llm = ChatOpenAI(
    model="gpt-5-mini",
    api_key=os.getenv("OPENAI_API_KEY"),
)

# Tavily 검색 클라이언트
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# Supporter 프롬프트 템플릿
SUPPORTER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """당신은 토론에서 주장을 옹호하는 'Supporter' 역할입니다.
주어진 주제에 대해 **찬성/긍정적 입장**에서 설득력 있는 논리를 제시해야 합니다.

아래는 주제에 대해 인터넷에서 검색한 실제 근거 자료입니다:
{search_results}

위 검색 결과를 활용하여 다음 원칙을 따르세요:
1. 명확한 논거를 3가지 이상 제시하세요
2. 각 논거에 대한 구체적인 근거나 예시를 포함하세요 (검색 결과 인용)
3. 논리적이고 체계적으로 구성하세요
4. 상대방의 반론을 예상하고 미리 반박 포인트를 준비하세요

출력 형식:
## 핵심 주장
[주제에 대한 찬성 입장 한 문장 요약]

## 주요 논거
1. [논거 1]
   - 근거: [구체적 근거/예시]

2. [논거 2]
   - 근거: [구체적 근거/예시]

3. [논거 3]
   - 근거: [구체적 근거/예시]

## 예상 반론에 대한 선제적 반박
[반론 예상 및 대응 논리]
"""),
    ("human", "토론 주제: {topic}\n\n위 주제에 대해 찬성/긍정적 입장에서 논리를 전개해주세요.")
])

# 체인 구성
supporter_chain = SUPPORTER_PROMPT | llm


def supporter_node(state: DebateState) -> dict:
    """
    Supporter 노드 함수
    """
    print("🟢 [실행 중] 소희(Supporter)가 찬성 논리를 생성합니다...")

    topic = state.get("topic", "")

    # Tavily 검색으로 근거 수집
    print("🔍 [검색 중] Tavily로 찬성 근거를 검색합니다...")
    search_response = tavily.search(
        query=f"{topic} 찬성 긍정적 근거 장점",
        max_results=5
    )
    search_results = "\n".join(
        f"- {r['content']}" for r in search_response["results"]
    )

    # LLM 호출 (검색 결과 포함)
    response = supporter_chain.invoke({
        "topic": topic,
        "search_results": search_results
    })

    # 결과 반환 (State 업데이트)
    return {"supporter_args": response.content}


# 테스트용 코드
if __name__ == "__main__":
    test_state = {"topic": "주 4일제 도입은 기업 생산성을 떨어뜨리는가?"}
    result = supporter_node(test_state)
    print("\n" + "=" * 50)
    print("🟢 Supporter 결과:")
    print("=" * 50)
    print(result["supporter_args"])

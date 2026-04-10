import os
from typing import List

from langchain_groq import ChatGroq
from langchain_community.retrievers import TavilySearchAPIRetriever
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv
from court.schema import DebateState


load_dotenv()

llm = ChatOpenAI(
        temperature=0.2,
        model_name="gpt-5-mini",
        openai_api_key=os.getenv("OPENAI_API_KEY")
)

# Tavily Retriever
retriever = TavilySearchAPIRetriever(
    k=5,
    api_key=os.getenv("TAVILY_API_KEY")
)


def _safe_get_text(value) -> str:
    return value.strip() if isinstance(value, str) else ""


def _parse_queries(text: str, max_queries: int = 5) -> List[str]:
    queries = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        line = line.lstrip("-•1234567890. ").strip()
        if line:
            queries.append(line)
    return queries[:max_queries]


def fact_checker_node(state):
    print("[실행 중] Fact Checker가 양측 주장을 검증합니다...")

    topic = _safe_get_text(state.get("topic", ""))
    supporter_args = _safe_get_text(state.get("supporter_args", ""))
    skeptic_args = _safe_get_text(state.get("skeptic_args", ""))

    # 1단계: 주장 분석 + 사실/의견 분리
    analysis_prompt = f"""
당신은 토론 시스템의 Fact Checker입니다.

주제:
{topic}

Supporter 주장:
{supporter_args}

Skeptic 주장:
{skeptic_args}

당신의 핵심 기능은 다음 3가지입니다.
1. supporter / skeptic 결과 분석
2. 객관적 검증
3. 사실 vs 의견 분리

먼저 양측 주장을 분석하여 핵심 claim을 정리하세요.

규칙:
- supporter와 skeptic의 핵심 주장만 간단히 정리
- 각 claim을 반드시 fact 또는 opinion으로 분류
- fact는 객관적으로 검색/검증 가능한 주장
- opinion은 해석, 평가, 입장, 추측
- 너무 긴 문장은 짧은 claim 단위로 분리
- 중복 표현은 줄이기

반드시 아래 형식으로 출력하세요.

[Supporter Claims]
- claim: ...
  type: fact/opinion
- claim: ...
  type: fact/opinion

[Skeptic Claims]
- claim: ...
  type: fact/opinion
- claim: ...
  type: fact/opinion
"""

    analyzed_claims = llm.invoke(analysis_prompt).content

    # 2단계: 검색용 쿼리 생성
    query_prompt = f"""
당신은 검색 쿼리 생성기입니다.

아래 claim 분석 결과에서 type이 fact인 주장만 골라,
웹 검색에 적합한 짧고 명확한 검색어로 바꾸세요.

주제:
{topic}

claim 분석 결과:
{analyzed_claims}

규칙:
- 한 줄에 검색어 하나만 출력
- 설명 금지
- 최대 5개
- 검색어는 짧고 핵심 명사 위주로 만들 것
- supporter와 skeptic 양쪽의 중요한 fact claim을 골고루 반영할 것
"""

    query_text = llm.invoke(query_prompt).content
    queries = _parse_queries(query_text, max_queries=5)

    # 검색 쿼리가 비면 fallback
    if not queries:
        queries = [topic]

    # 3단계: Tavily 검색
    search_result_blocks = []

    for idx, query in enumerate(queries, start=1):
        try:
            docs = retriever.invoke(query)

            block_lines = [f"[검색 쿼리 {idx}] {query}"]
            if not docs:
                block_lines.append("- 검색 결과 없음")
            else:
                for j, doc in enumerate(docs[:3], start=1):
                    content = getattr(doc, "page_content", "")
                    metadata = getattr(doc, "metadata", {})

                    block_lines.append(f"- 문서 {j} 내용: {content}")
                    block_lines.append(f"  문서 {j} 메타데이터: {metadata}")

            search_result_blocks.append("\n".join(block_lines))

        except Exception as e:
            search_result_blocks.append(
                f"[검색 쿼리 {idx}] {query}\n- 검색 실패: {str(e)}"
            )

    search_results_text = "\n\n".join(search_result_blocks)

    # 4단계: 최종 팩트체크 결과 생성
    final_prompt = f"""
당신은 토론 시스템의 최종 Fact Checker입니다.

주제:
{topic}

Supporter 주장:
{supporter_args}

Skeptic 주장:
{skeptic_args}

1차 claim 분석 결과:
{analyzed_claims}

웹 검색 결과:
{search_results_text}

당신의 핵심 기능:
1. supporter / skeptic 결과 분석
2. 객관적 검증
3. 사실 vs 의견 분리

아래 형식으로 최종 결과를 작성하세요.

[1. 주장 분석]
- Supporter 핵심 주장:
- Skeptic 핵심 주장:

[2. 사실 vs 의견 분리]
- 사실 주장:
- 의견 주장:

[3. 객관적 검증 결과]
- 근거가 비교적 확인된 주장:
- 근거가 부족한 주장:
- 과장되었거나 해석의 여지가 있는 주장:

[4. 종합 판단]
- 어느 쪽 주장이 상대적으로 더 근거가 탄탄한지
- 아직 추가 검증이 필요한 부분이 무엇인지

중요 규칙:
- 검색 결과에 없는 내용을 단정하지 말 것
- 의견을 사실처럼 검증하지 말 것
- 애매하면 '근거 부족'으로 둘 것
- 정치적/감정적 표현 없이 중립적으로 작성할 것
"""

    fact_check_result = llm.invoke(final_prompt).content

    return {
        "fact_check_result": fact_check_result
    }
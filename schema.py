# schema.py
from typing import TypedDict

class DebateState(TypedDict):
    topic: str               # 사용자 입력 주제
    supporter_args: str      # 소희 담당
    skeptic_args: str        # 지인 담당
    fact_check_result: str   # 건희 담당
    final_verdict: str       # 우진 담당


    final_verdict: str
    is_conclusive: bool
    iteration: int

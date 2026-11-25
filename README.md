# Claude Code 반복 업무 스킬

마케팅 실무에서 Claude Code에 같은 지시를 계속 하게 되는 일을 스킬로 묶었습니다. 대화 기록 약 3,900건을 집계해서 자주 나온 지시를 골랐습니다.

| 스킬 | 호출 예시 | 기록상 빈도 |
|---|---|---|
| `slop-check` | "AI 슬롭 제거해", "가독성 점검해" | 지적 약 40건 |
| `research-first` | "인터넷에서 써치해서 참고해" | 56건 |
| `threads-cardnews` | "오늘 올릴 카드뉴스 말해줘" | 29건 |
| `collab-mail` | "협업 메일 작성해줘" | 35건 |
| `capture-check` | "모바일 버전도 캡처 떠줘" | 85건 |

## 스킬별 내용

- **slop-check**
  - `scan.py`가 엠대시, 번역투, 과장 어휘, 순우리말 교체 후보를 줄번호로 출력
  - 판정 목록은 `references/slop-list.md`
- **research-first**
  - 공식 문서와 실제 사례 3~5건 수집, 2회 대조, 출처 링크 첨부 후 작업에 반영
- **threads-cardnews**
  - 게시 기록과 게시 예정 폴더를 대조해 오늘 올릴 세트 확인, 없으면 다음 회차 제작
  - 체크리스트는 `references/checklist.md`
  - 작업 폴더 구조는 SKILL.md 0번 표를 자기 경로로 수정해서 사용
- **collab-mail**
  - 1:1 협업 메일을 쿠션어 말투로 작성, 대상 목록 전원분 초안
- **capture-check**
  - `shoot.py`가 1440·390·360px 전체 캡처와 비교 이미지 1장 생성, 가로 넘침 수치 출력

## 설치

```bash
git clone https://github.com/kidujm/claude-skills.git
cp -r claude-skills/skills/* ~/.claude/skills/
pip install playwright pillow && playwright install chromium   # capture-check용
```

## 산출물 폴더 자동 열기 (선택)

`hooks/open_output_folder.py`는 Claude Code가 답변을 마칠 때 그 턴에 바탕화면 아래에서 바뀐 산출물 폴더를 탐색기로 엽니다(Windows). `_`로 시작하는 작업 폴더보다 최종 폴더를 먼저 고릅니다.

`~/.claude/settings.json`에 추가합니다.

```json
{
  "hooks": {
    "Stop": [
      { "hooks": [ { "type": "command", "command": "python ~/.claude/scripts/open_output_folder.py 2>/dev/null || true", "timeout": 20 } ] }
    ]
  }
}
```

스크립트는 `~/.claude/scripts/`에 복사합니다. 감시 폴더는 스크립트 상단 `ROOT`에서 바꿀 수 있습니다.

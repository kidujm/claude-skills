"""AI 슬롭 기계 검사: 걸린 줄을 '줄번호: [항목] 내용'으로 출력한다. 0건이면 OK."""
import re
import sys

RULES = [
    ("엠대시", r"—|―"),
    ("장식 기호", r"[→←⇒✓✔✅❌≈★☆•]"),
    ("영어 단골어", r"(?i)\b(delve|tapestry|pivotal|landscape|testament|seamless|robust|leverage|serves as)\b"),
    ("과장 어휘", r"핵심적인|획기적인|새 장을 열|빠르게 변화하는|자리매김|의 중심에 자리한|를 자랑하는"),
    ("상투 문장", r"하는 것이 중요합니다|라고 할 수 있습니다|살펴보겠습니다|핵심은 이겁니다|결론부터 말하면"),
    ("번역투", r"되어지|에 의해|를 통해|을 통해|함에 있어"),
    ("반전 구문", r"아니라.{0,20}(입니다|이다|예요)|단순한 .{1,15}(을|를) 넘어"),
    ("꼬리절", r"에 기여하며|를 보여주며|을 보여주며"),
    ("챗봇 잔재", r"물론이죠|좋은 질문|도움이 되셨길|궁금한 점 ?있으시면"),
    ("에요 말투(쓰레드 카드·본문만 금지)", r"에요[.!?\s]|이에요"),
    ("물결표", r"~(?![\s\d/])|～"),
    ("접속사 남발", r"^(또한|더불어|나아가),"),
    ("순우리말(한자어·외래어로 교체 검토)",
     r"바로잡|알맞|갈래|솜씨|쓰임새|낱말|뒷받침|살펴보|살피|알아보|견주|꼼꼼|손쉽|쓸모|짜임|얼개|갈무리|톺아|길잡이|누리집|들여다보|틀을|틀에 |틀로 "),
]


def main(path):
    with open(path, encoding="utf-8", errors="ignore") as f:
        lines = f.read().splitlines()
    hits = 0
    for i, line in enumerate(lines, 1):
        for name, pat in RULES:
            if re.search(pat, line):
                hits += 1
                print(f"{i}: [{name}] {line.strip()[:120]}")
    print(f"총 {hits}건" if hits else "OK 0건")


if __name__ == "__main__":
    main(sys.argv[1])

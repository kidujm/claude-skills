"""Stop hook: 이번 턴에 바탕화면 아래에서 만들어지거나 바뀐 산출물 폴더를 탐색기로 연다."""
import json
import os
import subprocess
import sys
import tempfile
import time
from collections import Counter
from datetime import datetime

ROOT = os.path.join(os.path.expanduser("~"), "Desktop")
EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".mp4", ".mov", ".webm",
        ".pdf", ".md", ".docx", ".pptx", ".xlsx", ".hwpx", ".txt", ".csv", ".html", ".zip"}
SKIP_DIRS = {"_생성스크립트", "_소스", "__pycache__", "node_modules", ".git", ".venv"}
MAX_DEPTH = 6
STATE = os.path.join(tempfile.gettempdir(), "claude_open_folder_state.json")


def is_prompt(entry):
    if entry.get("type") != "user" or entry.get("isMeta") or entry.get("isSidechain"):
        return False
    content = entry.get("message", {}).get("content")
    if isinstance(content, str):
        return not content.startswith("<")
    if isinstance(content, list):
        return any(isinstance(c, dict) and c.get("type") == "text" for c in content)
    return False


def turn_start(transcript_path):
    stamp = None
    try:
        with open(transcript_path, encoding="utf-8", errors="ignore") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                except ValueError:
                    continue
                if is_prompt(entry) and entry.get("timestamp"):
                    stamp = entry["timestamp"]
    except OSError:
        pass
    if not stamp:
        return time.time() - 1800
    return datetime.fromisoformat(stamp.replace("Z", "+00:00")).timestamp(), stamp


def changed_dirs(since):
    counts, latest = Counter(), {}
    base_depth = ROOT.rstrip(os.sep).count(os.sep)
    for dirpath, dirnames, filenames in os.walk(ROOT):
        if dirpath.count(os.sep) - base_depth >= MAX_DEPTH:
            dirnames[:] = []
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for name in filenames:
            if os.path.splitext(name)[1].lower() not in EXTS or name.startswith("~$"):
                continue
            try:
                mtime = os.path.getmtime(os.path.join(dirpath, name))
            except OSError:
                continue
            if mtime >= since:
                counts[dirpath] += 1
                latest[dirpath] = max(latest.get(dirpath, 0), mtime)
    return counts, latest


def main():
    data = json.load(sys.stdin)
    if data.get("stop_hook_active"):
        return
    result = turn_start(data.get("transcript_path", ""))
    since, stamp = result if isinstance(result, tuple) else (result, "")
    counts, latest = changed_dirs(since)
    if not counts:
        return
    def is_final(d):
        return not any(part.startswith("_") for part in os.path.relpath(d, ROOT).split(os.sep))

    target = max(counts, key=lambda d: (is_final(d), counts[d], latest[d]))

    key = f"{data.get('session_id', '')}|{stamp}|{target}"
    try:
        with open(STATE, encoding="utf-8") as f:
            if f.read() == key:
                return
    except OSError:
        pass
    with open(STATE, "w", encoding="utf-8") as f:
        f.write(key)

    subprocess.Popen(["explorer", os.path.normpath(target)])
    print(json.dumps({"systemMessage": f"폴더 열림: {target}"}, ensure_ascii=False))


if __name__ == "__main__":
    main()

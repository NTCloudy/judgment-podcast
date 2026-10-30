"""審判天下 trilogy: novel/{ch,p2_ch,p3_ch}NN_popo.txt -> docs/audio/sSeNN.mp3 (season = part).

Skips existing audio; regenerates when the chapter text is newer than its MP3. Updates episodes.json.
"""
import glob, json, os, re, subprocess, sys
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
SRC = os.path.expanduser("~/.gemini/jetski/brain/9ddac055-6c3d-4b59-b184-5e8f8f7c2fd8/novel")
PARTS = {1: ("ch", "第一部・還帳"), 2: ("p2_ch", "第二部・審判"), 3: ("p3_ch", "第三部・秤")}
CN = "零一二三四五六七八九"
def cn(n): return CN[n] if n < 10 else ("十" + (CN[n % 10] if n % 10 else "") if n < 20 else CN[n // 10] + "十" + (CN[n % 10] if n % 10 else ""))
eps = json.load(open("episodes.json", encoding="utf-8")) if os.path.exists("episodes.json") else []
have = {e["file"] for e in eps}
base = datetime(2026, 10, 30, 12, tzinfo=timezone(timedelta(hours=8)))
for season, (prefix, part) in PARTS.items():
    for txt in sorted(glob.glob(f"{SRC}/{prefix}[0-9][0-9]_popo.txt")):
        n = int(re.search(r"ch(\d+)_popo", txt).group(1))
        md = open(txt.replace("_popo.txt", ".md"), encoding="utf-8").read()
        m = re.search(r"^## (.+)$", md, re.M); title = m.group(1).strip() if m else f"第{cn(n)}章"
        f = f"s{season}e{n:02d}.mp3"
        mp3 = f"docs/audio/{f}"
        if os.path.exists(mp3) and os.path.getmtime(txt) > os.path.getmtime(mp3) + 60:
            os.remove(mp3)  # chapter text was edited after the audio was made: regenerate
        if f in have and os.path.exists(mp3):
            continue
        if not os.path.exists(mp3):
            subprocess.run([sys.executable, "-u", "tools/tts.py", txt, mp3,
                            f"審判天下，{part.replace('・', '，')}。{title.replace('　', '，')}。",
                            f"{title.split('　')[0]}，完。感謝收聽審判天下。"], check=True)
        if f not in have:
            eps.append({"n": n, "season": season, "file": f, "title": f"審判天下 {part}｜{title}",
                        "summary": f"《審判天下》{part}　{title}。含寫實暴力與死亡描寫，純屬虛構。",
                        "pub": format_datetime(base + timedelta(minutes=season * 100 + n))})
            have.add(f)
        json.dump(sorted(eps, key=lambda e: (e["season"], e["n"])), open("episodes.json", "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        print("done", f, flush=True)

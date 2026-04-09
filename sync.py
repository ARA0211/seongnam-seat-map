import os
import csv
import requests

NOTION_TOKEN = os.environ["NOTION_TOKEN"]
NOTION_PAGE_ID = os.environ["NOTION_PAGE_ID"]

COLOR_MAP = {
    "gray":   {"bg": "#e8eaf0", "border": "#c9cdd6", "text": "#555555"},
    "blue":   {"bg": "#ddeaf8", "border": "#a8c8e8", "text": "#2a5f8a"},
    "pink":   {"bg": "#fde8ec", "border": "#f4b8c4", "text": "#a03050"},
    "teal":   {"bg": "#e0f4f0", "border": "#8ed4c8", "text": "#1a6b5e"},
    "green":  {"bg": "#e8f4e0", "border": "#a8d890", "text": "#2a6a1a"},
    "purple": {"bg": "#ede8f8", "border": "#c4b0e8", "text": "#5a3a9a"},
    "orange": {"bg": "#fde8d0", "border": "#f4c898", "text": "#a06020"},
}

def read_csv():
    data = {"CEO": [], "COO": [], "left": [], "right": [], "rnd": []}
    with open("seatmap.csv", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sec = row["section"].strip()
            if sec in data:
                data[sec].append({"name": row["name"].strip(), "color": row["color"].strip()})
    return data

def cell(name, color, extra_style=""):
    c = COLOR_MAP.get(color, COLOR_MAP["gray"])
    return f'<div class="cell" style="background:{c["bg"]};border:1.5px solid {c["border"]};color:{c["text"]};{extra_style}">{name}</div>'

def build_html(data):
    # CEO / COO 카드
    ceo_html = ""
    for p in data["CEO"]:
        ceo_html += f'<div class="cell pink-card"><div style="font-weight:600;">CEO</div><div class="name-sm">{p["name"]}</div></div>'
    for p in data["COO"]:
        ceo_html += f'<div class="cell pink-card"><div style="font-weight:600;">COO</div><div class="name-sm">{p["name"]}</div></div>'

    # left 그룹 (정언식, 고정인, 김미란, 공석, 정의찬, 이아라)
    def make_rows_left(people):
        rows = ""
        # 1행: 첫번째 사람 (넓게)
        if len(people) > 0:
            p = people[0]
            rows += f'<div class="row"><div class="cell w2" style="background:{COLOR_MAP[p["color"]]["bg"]};border:1.5px solid {COLOR_MAP[p["color"]]["border"]};color:{COLOR_MAP[p["color"]]["text"]};">{p["name"]}</div></div>'
        # 2행: 2,3번째
        if len(people) > 2:
            rows += '<div class="row">'
            for p in people[1:3]:
                c = COLOR_MAP[p["color"]]
                rows += f'<div class="cell w1" style="background:{c["bg"]};border:1.5px solid {c["border"]};color:{c["text"]};">{p["name"]}</div>'
            rows += '</div>'
        # 3행: 4,5번째
        if len(people) > 4:
            rows += '<div class="row">'
            for p in people[3:5]:
                c = COLOR_MAP[p["color"]]
                rows += f'<div class="cell w1" style="background:{c["bg"]};border:1.5px solid {c["border"]};color:{c["text"]};">{p["name"]}</div>'
            rows += '</div>'
        # 4행: 마지막 (넓게)
        if len(people) > 5:
            p = people[5]
            rows += f'<div class="row"><div class="cell w2" style="background:{COLOR_MAP[p["color"]]["bg"]};border:1.5px solid {COLOR_MAP[p["color"]]["border"]};color:{COLOR_MAP[p["color"]]["text"]};">{p["name"]}</div></div>'
        return rows

    def make_rows_right(people):
        rows = ""
        if len(people) > 0:
            p = people[0]
            rows += f'<div class="row"><div class="cell w2" style="background:{COLOR_MAP[p["color"]]["bg"]};border:1.5px solid {COLOR_MAP[p["color"]]["border"]};color:{COLOR_MAP[p["color"]]["text"]};">{p["name"]}</div></div>'
        if len(people) > 2:
            rows += '<div class="row">'
            for p in people[1:3]:
                c = COLOR_MAP[p["color"]]
                rows += f'<div class="cell w1" style="background:{c["bg"]};border:1.5px solid {c["border"]};color:{c["text"]};">{p["name"]}</div>'
            rows += '</div>'
        if len(people) > 4:
            rows += '<div class="row">'
            for p in people[3:5]:
                c = COLOR_MAP[p["color"]]
                rows += f'<div class="cell w1" style="background:{c["bg"]};border:1.5px solid {c["border"]};color:{c["text"]};">{p["name"]}</div>'
            rows += '</div>'
        if len(people) > 5:
            p = people[5]
            rows += f'<div class="row"><div class="cell w2" style="background:{COLOR_MAP[p["color"]]["bg"]};border:1.5px solid {COLOR_MAP[p["color"]]["border"]};color:{COLOR_MAP[p["color"]]["text"]};">{p["name"]}</div></div>'
        return rows

    # R&D Center
    rnd_names = "".join([f'<div class="name-sm">{p["name"]}</div>' for p in data["rnd"]])

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>성남 캠퍼스 자리배치도</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Apple SD Gothic Neo', 'Noto Sans KR', sans-serif; background: #faf9f6; padding: 32px 24px; }}
  h1 {{ font-size: 20px; font-weight: 600; color: #1a1a2e; margin-bottom: 4px; }}
  .sub {{ font-size: 12px; color: #888; margin-bottom: 24px; }}
  .layout {{ display: flex; gap: 16px; align-items: flex-start; }}
  .left-col {{ display: flex; flex-direction: column; gap: 12px; flex-shrink: 0; }}
  .right-col {{ display: flex; flex-direction: column; gap: 8px; flex: 1; }}
  .cell {{ border-radius: 10px; padding: 10px 14px; text-align: center; font-size: 13px; font-weight: 500; border: 1.5px solid; transition: transform 0.15s; }}
  .cell:hover {{ transform: translateY(-1px); }}
  .pink-card {{ background:#fde8ec; border:1.5px solid #f4b8c4; color:#a03050; min-width:90px; }}
  .name-sm {{ font-size: 11px; margin-top: 3px; opacity: 0.85; }}
  .row {{ display: flex; gap: 8px; }}
  .w1 {{ min-width: 80px; }}
  .w2 {{ min-width: 168px; }}
  .groups {{ display: flex; gap: 24px; }}
  .group {{ display: flex; flex-direction: column; gap: 8px; }}
</style>
</head>
<body>
  <h1>🏢 성남 캠퍼스 자리배치도</h1>
  <p class="sub">seatmap.csv 수정 후 GitHub 업로드 시 자동 반영됩니다</p>
  <div class="layout">
    <div class="left-col">
      <div class="cell" style="background:#e8eaf0;border:1.5px solid #c9cdd6;color:#555;width:110px;height:200px;display:flex;align-items:center;justify-content:center;">대회의실</div>
      <div class="cell" style="background:#ddeaf8;border:1.5px solid #a8c8e8;color:#2a5f8a;width:110px;min-height:110px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;">
        <div style="font-weight:600;">R&D Center</div>
        {rnd_names}
      </div>
    </div>
    <div class="right-col">
      <div class="row">
        {ceo_html}
        <div class="cell" style="background:#e8eaf0;border:1.5px solid #c9cdd6;color:#555;min-width:90px;display:flex;align-items:center;justify-content:center;">회의실</div>
      </div>
      <div class="groups">
        <div class="group">{make_rows_left(data["left"])}</div>
        <div class="group">{make_rows_right(data["right"])}</div>
      </div>
    </div>
  </div>
</body>
</html>"""
    return html

def clear_notion_page():
    headers = {"Authorization": f"Bearer {NOTION_TOKEN}", "Notion-Version": "2022-06-28"}
    res = requests.get(f"https://api.notion.com/v1/blocks/{NOTION_PAGE_ID}/children", headers=headers)
    for block in res.json().get("results", []):
        requests.delete(f"https://api.notion.com/v1/blocks/{block['id']}", headers=headers)

def update_notion_with_embed(pages_url):
    headers = {"Authorization": f"Bearer {NOTION_TOKEN}", "Notion-Version": "2022-06-28", "Content-Type": "application/json"}
    body = {"children": [{"type": "embed", "embed": {"url": pages_url}}]}
    res = requests.patch(f"https://api.notion.com/v1/blocks/{NOTION_PAGE_ID}/children", headers=headers, json=body)
    print("노션 업데이트 결과:", res.status_code)

if __name__ == "__main__":
    print("CSV 읽는 중...")
    data = read_csv()
    print("HTML 생성 중...")
    html = build_html(data)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("저장 완료!")
    clear_notion_page()
    github_user = os.environ.get("GITHUB_REPOSITORY", "").split("/")[0]
    github_repo = os.environ.get("GITHUB_REPOSITORY", "").split("/")[-1]
    pages_url = f"https://{github_user}.github.io/{github_repo}/"
    update_notion_with_embed(pages_url)
    print(f"완료! {pages_url}")

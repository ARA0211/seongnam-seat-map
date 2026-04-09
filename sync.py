import os
import requests
import csv
import io

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
    with open("seatmap.csv", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return list(reader)

def build_html(cells):
    # 그리드 최대 크기 계산
    max_row = max(int(c["row"]) + int(c.get("rowspan", 1)) - 1 for c in cells)
    max_col = max(int(c["col"]) + int(c.get("colspan", 1)) - 1 for c in cells)

    # 그리드 초기화
    grid = [[None] * (max_col + 1) for _ in range(max_row + 1)]
    occupied = set()

    cell_html_map = {}
    for c in cells:
        r, col = int(c["row"]), int(c["col"])
        rs = int(c.get("rowspan", 1))
        cs = int(c.get("colspan", 1))
        color = COLOR_MAP.get(c.get("color", "gray"), COLOR_MAP["gray"])
        t = c.get("type", "person")
        name = c.get("name", "")

        style = f'background:{color["bg"]};border:1.5px solid {color["border"]};color:{color["text"]};'
        rs_attr = f' rowspan="{rs}"' if rs > 1 else ""
        cs_attr = f' colspan="{cs}"' if cs > 1 else ""

        if t == "room":
            inner = f'<div style="font-weight:600;font-size:13px;">{name}</div>'
        elif t == "ceo":
            parts = name.split("|")
            inner = f'<div style="font-weight:600;font-size:13px;">{parts[0]}</div>'
            if len(parts) > 1:
                inner += f'<div style="font-size:11px;margin-top:2px;">{parts[1]}</div>'
        elif t == "empty":
            inner = f'<div style="font-size:12px;">{name}</div>'
        else:
            inner = f'<div style="font-size:12px;font-weight:500;">{name}</div>'

        cell_html_map[(r, col)] = f'<td{rs_attr}{cs_attr} style="padding:10px 14px;text-align:center;border-radius:8px;{style}min-width:80px;">{inner}</td>'

        for dr in range(rs):
            for dc in range(cs):
                if dr == 0 and dc == 0:
                    continue
                occupied.add((r + dr, col + dc))

    # 테이블 HTML 생성
    rows_html = ""
    for r in range(1, max_row + 1):
        rows_html += "<tr style='height:10px;'></tr><tr>"
        for col in range(1, max_col + 1):
            if (r, col) in occupied:
                continue
            if (r, col) in cell_html_map:
                rows_html += cell_html_map[(r, col)]
            else:
                rows_html += '<td style="background:transparent;border:none;min-width:16px;"></td>'
        rows_html += "</tr>"

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>성남 캠퍼스 자리배치도</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Apple SD Gothic Neo', 'Noto Sans KR', sans-serif;
    background: #faf9f6;
    padding: 32px 24px;
  }}
  h1 {{ font-size: 20px; font-weight: 600; color: #1a1a2e; margin-bottom: 4px; }}
  .sub {{ font-size: 12px; color: #888; margin-bottom: 24px; }}
  table {{ border-collapse: separate; border-spacing: 6px; }}
  td {{ transition: transform 0.15s; }}
  td:hover {{ transform: translateY(-1px); }}
</style>
</head>
<body>
  <h1>🏢 성남 캠퍼스 자리배치도</h1>
  <p class="sub">엑셀 수정 후 GitHub 업로드 시 자동 반영됩니다</p>
  <table>
    {rows_html}
  </table>
</body>
</html>"""
    return html

def clear_notion_page():
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28"
    }
    url = f"https://api.notion.com/v1/blocks/{NOTION_PAGE_ID}/children"
    res = requests.get(url, headers=headers)
    blocks = res.json().get("results", [])
    for block in blocks:
        requests.delete(f"https://api.notion.com/v1/blocks/{block['id']}", headers=headers)

def update_notion_with_embed(pages_url):
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    url = f"https://api.notion.com/v1/blocks/{NOTION_PAGE_ID}/children"
    body = {"children": [{"type": "embed", "embed": {"url": pages_url}}]}
    res = requests.patch(url, headers=headers, json=body)
    print("노션 업데이트 결과:", res.status_code)

if __name__ == "__main__":
    print("CSV 읽는 중...")
    cells = read_csv()
    print(f"{len(cells)}개 셀 읽음")

    print("HTML 생성 중...")
    html = build_html(cells)

    print("index.html 저장 중...")
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("저장 완료!")

    print("노션 업데이트 중...")
    clear_notion_page()
    github_user = os.environ.get("GITHUB_REPOSITORY", "").split("/")[0]
    github_repo = os.environ.get("GITHUB_REPOSITORY", "").split("/")[-1]
    pages_url = f"https://{github_user}.github.io/{github_repo}/"
    update_notion_with_embed(pages_url)
    print(f"완료! {pages_url}")

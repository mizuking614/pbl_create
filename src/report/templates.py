HTML_TEMPLATE = """<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>授業資料ポータル</title>
  <style>
    :root {{
      --bg: #fafafa;
      --ink: #1f2937;
      --soft: #f3f4f6;
      --line: #e5e7eb;
      --accent: #2563eb;
      --accent-soft: #dbeafe;
      --muted: #6b7280;
    }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      margin: 0;
      padding: 0;
      background: var(--bg);
      color: var(--ink);
      line-height: 1.5;
    }}
    header {{
      background: #ffffff;
      border-bottom: 1px solid var(--line);
      padding: 20px;
      position: sticky;
      top: 0;
      z-index: 100;
    }}
    .header-content {{
      max-width: 1000px;
      margin: 0 auto;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 15px;
    }}
    h1 {{
      margin: 0;
      font-size: 1.5rem;
      font-weight: 700;
    }}
    .search-box {{
      position: relative;
    }}
    .search-box input {{
      width: 250px;
      padding: 8px 12px;
      border: 1px solid var(--line);
      border-radius: 6px;
      font-size: 0.9rem;
      background: var(--soft);
      color: var(--ink);
      outline: none;
      transition: border-color 0.2s, background-color 0.2s;
    }}
    .search-box input:focus {{
      border-color: var(--accent);
      background: #ffffff;
    }}
    main {{
      max-width: 1000px;
      margin: 30px auto;
      padding: 0 20px;
    }}
    .nav-links {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-bottom: 30px;
    }}
    .nav-links a {{
      padding: 8px 16px;
      background: #ffffff;
      border: 1px solid var(--line);
      border-radius: 20px;
      color: var(--ink);
      text-decoration: none;
      font-size: 0.9rem;
      transition: border-color 0.2s, background-color 0.2s;
    }}
    .nav-links a:hover {{
      border-color: var(--accent);
      background: var(--accent-soft);
    }}
    section {{
      background: #ffffff;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 24px;
      margin-bottom: 30px;
      scroll-margin-top: 100px;
    }}
    .course-head {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      border-bottom: 1px solid var(--line);
      padding-bottom: 16px;
      margin-bottom: 20px;
    }}
    .course-head h2 {{
      margin: 0 0 8px 0;
      font-size: 1.4rem;
    }}
    .course-head .teacher {{
      color: var(--muted);
      font-size: 0.9rem;
    }}
    .course-head .meta {{
      font-size: 0.9rem;
      background: var(--soft);
      padding: 4px 8px;
      border-radius: 4px;
    }}
    .chips {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 10px;
    }}
    .chip {{
      font-size: 0.75rem;
      padding: 2px 8px;
      background: var(--soft);
      border-radius: 12px;
      color: var(--muted);
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 20px;
    }}
    .material {{
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      background: #ffffff;
    }}
    .material .preview {{
      width: 50px;
      height: 50px;
      background: var(--soft);
      border-radius: 4px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      color: var(--muted);
      flex-shrink: 0;
      overflow: hidden;
    }}
    .material .preview img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
    }}
    .material .name {{
      font-weight: 600;
      font-size: 0.95rem;
      word-break: break-all;
    }}
    .material .terms {{
      font-size: 0.8rem;
      color: var(--muted);
    }}
    .btn {{
      display: inline-block;
      padding: 6px 12px;
      background: var(--soft);
      border: 1px solid var(--line);
      border-radius: 4px;
      color: var(--ink);
      text-decoration: none;
      font-size: 0.85rem;
      font-weight: 500;
      cursor: pointer;
      text-align: center;
      transition: border-color 0.2s, background-color 0.2s;
    }}
    .btn:hover {{
      border-color: var(--accent);
      background: var(--accent-soft);
      color: var(--accent);
    }}
    .summary-details {{
      width: 100%;
      margin-top: 8px;
    }}
    .summary-details summary {{
      list-style: none;
      outline: none;
    }}
    .summary-details summary::-webkit-details-marker {{
      display: none;
    }}
    .summary-content {{
      margin-top: 12px;
      padding: 12px;
      background: var(--soft);
      border-radius: 6px;
      font-size: 0.85rem;
    }}
    .summary-content h4 {{
      margin: 0 0 8px 0;
      font-size: 0.9rem;
    }}
    .summary-content p {{
      margin: 0 0 12px 0;
      color: #374151;
    }}
    .summary-content ul {{
      margin: 0 0 12px 0;
      padding-left: 20px;
    }}
    .summary-content li {{
      margin-bottom: 4px;
    }}
    .insight-section {{
      background: var(--accent-soft);
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 15px;
      margin-bottom: 20px;
    }}
    .insight-section h3 {{
      margin: 0 0 10px 0;
      font-size: 1.1rem;
      color: var(--accent);
    }}
    .insight-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 15px;
      font-size: 0.9rem;
    }}
    .insight-card {{
      background: #ffffff;
      padding: 10px;
      border-radius: 4px;
      border: 1px solid var(--line);
    }}
    .insight-card strong {{
      color: var(--accent);
    }}
    .attendance-table {{
      margin-top: 10px;
    }}
    .status-badge {{
      display: inline-block;
      padding: 2px 8px;
      border-radius: 12px;
      font-size: 0.8rem;
      font-weight: bold;
    }}
    .status-badge.present {{ background: #ccfbf1; color: #0f766e; }}
    .status-badge.late {{ background: #fef3c7; color: #d97706; }}
    .status-badge.absent {{ background: #fee2e2; color: #b91c1c; }}
    .status-badge.excused {{ background: #dbeafe; color: #1d4ed8; }}
    .empty {{
      grid-column: 1 / -1;
      text-align: center;
      padding: 40px;
      color: var(--muted);
      background: #ffffff;
      border: 1px dashed var(--line);
      border-radius: 6px;
    }}
    .global-links-section {{
      background: #ffffff;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 24px;
      margin-bottom: 30px;
    }}
    .global-links-section h2 {{
      margin: 0 0 15px 0;
      font-size: 1.3rem;
      color: var(--accent);
    }}
    .global-links-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 15px;
    }}
    .global-link-card {{
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 12px;
      background: var(--soft);
    }}
    .global-link-card a {{
      font-weight: 600;
      color: var(--accent);
      text-decoration: none;
    }}
    .global-link-card a:hover {{
      text-decoration: underline;
    }}
    .global-link-card div {{
      font-size: 0.85rem;
      color: var(--muted);
      margin-top: 4px;
    }}
  </style>
</head>
<body>
  <header>
    <div class="header-content">
      <h1>授業資料ポータル</h1>
      <div class="search-box">
        <input type="search" id="search" placeholder="授業名・資料名で検索...">
      </div>
    </div>
  </header>
  <main>
    <div class="nav-links">
      {nav_links}
      <a href="#links-list">🔗 共通参考リンク集</a>
    </div>
    {content}
    <section id="links-list" class="global-links-section">
      <h2>🔗 共通参考リンク集</h2>
      {global_links_html}
    </section>
  </main>
  <script>
    const searchInput = document.getElementById("search");
    let searchIndex = {{ index: [] }};
    
    fetch("search_index.json")
      .then(response => response.json())
      .then(data => {{
        searchIndex = data;
        console.log("Search index loaded:", searchIndex.index.length, "items.");
      }})
      .catch(err => {{
        console.warn("Could not load search_index.json natively via AJAX. This is expected if opening index.html directly from file:/// in Chrome. Error:", err);
      }});

    function getMatchInfo(item, queryTerms) {{
      const fields = [
        {{ name: "授業名", val: item.course }},
        {{ name: "教員名", val: item.teacher }},
        {{ name: "資料名", val: item.material_name }},
        {{ name: "キーワード", val: item.keywords.join(", ") }},
        {{ name: "AI要約", val: item.summary }},
        {{ name: "要点", val: item.key_points.join(" ") }},
        {{ name: "重要語句", val: item.important_terms.join(" ") }},
        {{ name: "復習リスト", val: item.review_checklist.join(" ") }},
        {{ name: "OCR本文", val: item.ocr_text }}
      ];
      
      for (const field of fields) {{
        if (!field.val) continue;
        const valLower = field.val.toLowerCase();
        const matchesAll = queryTerms.every(term => valLower.includes(term));
        if (matchesAll) {{
          const firstTerm = queryTerms[0];
          const idx = valLower.indexOf(firstTerm);
          const start = Math.max(0, idx - 40);
          const end = Math.min(field.val.length, idx + firstTerm.length + 40);
          let snippet = field.val.substring(start, end);
          if (start > 0) snippet = "..." + snippet;
          if (end < field.val.length) snippet = snippet + "...";
          
          queryTerms.forEach(term => {{
            const regex = new RegExp("(" + escapeRegExp(term) + ")", "gi");
            snippet = snippet.replace(regex, "<mark style='background-color: #fef08a;'>$1</mark>");
          }});
          
          return {{ reason: field.name, snippet: snippet }};
        }}
      }}
      return null;
    }}
    
    function escapeRegExp(string) {{
      return string.replace(/[.*+?^${{}}()|[\\\\\\\\]/g, '\\\\$&');
    }}

    searchInput.addEventListener("input", () => {{
      const query = searchInput.value.trim().toLowerCase();
      
      document.querySelectorAll(".search-match-info").forEach(el => el.remove());
      
      if (query.length === 0) {{
        document.querySelectorAll("[data-search]").forEach(el => el.hidden = false);
        return;
      }}
      
      const queryTerms = query.split(/\\s+/).filter(t => t.length > 0);
      if (queryTerms.length === 0) return;
      
      const cardMap = new Map();
      document.querySelectorAll(".material[data-path]").forEach(el => {{
        cardMap.set(el.dataset.path, el);
        el.hidden = true;
      }});
      
      searchIndex.index.forEach(item => {{
        const match = getMatchInfo(item, queryTerms);
        const card = cardMap.get(item.path);
        if (card) {{
          if (match) {{
            card.hidden = false;
            const infoDiv = document.createElement("div");
            infoDiv.className = "search-match-info";
            infoDiv.style.margin = "8px 0";
            infoDiv.style.padding = "6px 8px";
            infoDiv.style.background = "#f3f4f6";
            infoDiv.style.borderLeft = "3px solid #3b82f6";
            infoDiv.style.borderRadius = "4px";
            infoDiv.style.fontSize = "0.85rem";
            infoDiv.innerHTML = `<strong>一致項目 (${{match.reason}}):</strong> <span style="color: #4b5563;">${{match.snippet}}</span>`;
            card.appendChild(infoDiv);
          }} else {{
            card.hidden = true;
          }}
        }}
      }});
      
      for (const section of document.querySelectorAll("section")) {{
        const hasVisible = Array.from(section.querySelectorAll(".material")).some(item => !item.hidden);
        section.hidden = !hasVisible;
      }}
    }});
  </script>
</body>
</html>
"""

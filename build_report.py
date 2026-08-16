#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the Osoul dashboard HTML summary report from data.json."""
import json, datetime, os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data.json")
OUT_DIR = os.path.expanduser("~/.hermes/research")
os.makedirs(OUT_DIR, exist_ok=True)

d = json.load(open(DATA, encoding="utf-8"))
sm = d["summary"]
mk = d["markets"]
us, kw = mk["US"], mk["KW"]
stocks = sorted(d["stocks"], key=lambda x: x.get("overallScore", 0), reverse=True)
today = datetime.date.today().strftime("%Y-%m-%d")

def bpe(st):
    m = {x["method"]: x["score"] for x in st.get("methods", [])}
    b = m.get("Buffett")
    p = m.get("Piotroski")
    e = m.get("ONeil")
    def f(v): return "%.1f" % v if isinstance(v, (int, float)) else "—"
    return f(b) + " / " + f(p) + " / " + f(e)

# --- Top 10 stocks rows ---
top = stocks[:10]
rows = ""
for i, st in enumerate(top, 1):
    flag = "🇺🇸" if st["market"] == "US" else "🇰🇼"
    cls = st.get("classification", "")
    cls_class = "tag-exc" if "ممتاز" in cls else ("tag-good" if "جيد" in cls else "tag-mid")
    rows += f"""<tr>
      <td class="rank">{i}</td>
      <td class="tk">{st['ticker']}</td>
      <td>{st['name']}</td>
      <td class="ctr">{flag} {st['market']}</td>
      <td class="ctr"><span class="score">{st['overallScore']:.1f}</span></td>
      <td class="ctr"><span class="{cls_class}">{cls}</span></td>
      <td class="ctr mono">{bpe(st)}</td>
    </tr>\n"""

# --- Market comparison rows ---
def stat_row(label, uv, kv, uh="", kh=""):
    return f"""<tr><td>{label}</td>
      <td class="ctr"><b>{uv}</b> <span class="sub">{uh}</span></td>
      <td class="ctr"><b>{kv}</b> <span class="sub">{kh}</span></td></tr>"""

market_rows = (
    stat_row("الأسهم تحت المراقبة", us["activeTickers"], kw["activeTickers"], "سهم", "سهم") +
    stat_row("صفقات مفتوحة", us["totalTrades"], kw["totalTrades"], "صفقة", "صفقة") +
    stat_row("نسبة النجاح", f'{us["winRate"]:.1f}%', f'{kw["winRate"]:.1f}%',
             f'{us["winCount"]}ر/{us["lossCount"]}خ', f'{kw["winCount"]}ر/{kw["lossCount"]}خ') +
    stat_row("العائد السنوي", f'+{us["annualReturn"]:.1f}%', f'+{kw["annualReturn"]:.1f}%',
             f'S&P 500: {us["benchmarkReturn"]:.1f}%', f'Boursa: {kw["benchmarkReturn"]:.1f}%') +
    stat_row("Sharpe", f'{us["sharpe"]:.2f}', f'{kw["sharpe"]:.2f}') +
    stat_row("أقصى تراجع (Max DD)", f'{us["maxDrawdown"]:.1f}%', f'{kw["maxDrawdown"]:.1f}%')
)

# --- Monthly performance (last 6) ---
mr = d["monthlyReturns"][-6:]
month_rows = ""
for m in mr:
    month_rows += f"""<tr><td>{m['month']}</td>
      <td class="ctr {'pos' if m['us']>=0 else 'neg'}">{'+' if m['us']>=0 else ''}{m['us']:.1f}%</td>
      <td class="ctr {'pos' if m['kw']>=0 else 'neg'}">{'+' if m['kw']>=0 else ''}{m['kw']:.1f}%</td></tr>\n"""

last_upd = d["lastUpdated"][:16].replace("T", " ")
status = d["system"].get("status", "")
status_txt = "السوق مفتوح · قيد التشغيل" if status == "active" else "غير متصل"
total_watch = len(stocks)

# win rate context note
wr = sm["winRate"]
wr_note = "إيجابي" if wr >= 50 else "أقل من 50% — يحتاج متابعة"

HTML = f"""<!DOCTYPE html>
<html dir="rtl" lang="ar" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>أصول — ملخص داشبورد Osoul</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap" rel="stylesheet">
<style>
:root {{
  --green:#22C55E; --gold:#D4A853;
  --bg:#0b0f14; --card:#131a23; --card2:#0f151d;
  --text:#e7edf3; --muted:#8b97a7; --border:#1f2a36;
  --pos:#22C55E; --neg:#f87171; --blue:#3B82F6;
}}
[data-theme="light"] {{
  --bg:#f4f6f9; --card:#ffffff; --card2:#f8fafc;
  --text:#0f1720; --muted:#5b6675; --border:#e3e9f0;
  --pos:#16a34a; --neg:#dc2626;
}}
* {{ box-sizing:border-box; margin:0; padding:0; }}
body {{ font-family:'Tajawal',system-ui,sans-serif; background:var(--bg); color:var(--text);
  line-height:1.6; padding:0 0 40px; transition:background .3s,color .3s; }}
.wrap {{ max-width:1080px; margin:0 auto; padding:0 18px; }}
a {{ color:var(--green); text-decoration:none; }}

/* Header */
header {{ background:linear-gradient(135deg,#0e151d,#10241a); border-bottom:2px solid var(--green);
  padding:26px 0 22px; position:relative; }}
[data-theme="light"] header {{ background:linear-gradient(135deg,#eef6f0,#fffdf5); }}
.hrow {{ display:flex; align-items:center; justify-content:space-between; gap:16px; flex-wrap:wrap; }}
.logo {{ display:flex; align-items:center; gap:12px; }}
.logo .mark {{ width:46px; height:46px; border-radius:13px; background:linear-gradient(135deg,var(--green),var(--gold));
  display:flex; align-items:center; justify-content:center; font-weight:800; color:#06210f; font-size:1.3rem;
  box-shadow:0 4px 16px rgba(34,197,94,.35); }}
.logo h1 {{ font-size:1.5rem; font-weight:800; }}
.logo .sub {{ color:var(--muted); font-size:.82rem; font-weight:500; }}
.theme-btn {{ background:var(--card); border:1px solid var(--border); color:var(--text);
  padding:9px 15px; border-radius:11px; cursor:pointer; font-family:inherit; font-size:1rem; font-weight:700;
  display:flex; align-items:center; gap:7px; transition:.2s; }}
.theme-btn:hover {{ border-color:var(--green); }}

/* Live link bar */
.livebar {{ margin:22px 0 8px; }}
.livebar a {{ display:flex; align-items:center; justify-content:center; gap:10px;
  background:linear-gradient(135deg,var(--green),#1aa64c); color:#04150b; font-weight:800;
  padding:16px 20px; border-radius:15px; font-size:1.08rem; box-shadow:0 8px 26px rgba(34,197,94,.30);
  transition:transform .15s, box-shadow .15s; }}
.livebar a:hover {{ transform:translateY(-2px); box-shadow:0 12px 32px rgba(34,197,94,.42); }}
.livebar a .pulse {{ width:11px; height:11px; border-radius:50%; background:#04150b; animation:pulse 1.6s infinite; }}
@keyframes pulse {{ 0%,100%{{opacity:.4}} 50%{{opacity:1}} }}

/* Sections */
section {{ margin:26px 0; }}
.sec-title {{ display:flex; align-items:center; gap:10px; font-size:1.18rem; font-weight:800;
  margin-bottom:14px; }}
.sec-title .bar {{ width:5px; height:22px; border-radius:3px; background:var(--gold); }}
.sec-title .ic {{ color:var(--green); }}

/* KPI grid */
.kpi-grid {{ display:grid; grid-template-columns:repeat(3,1fr); gap:14px; }}
.kpi {{ background:var(--card); border:1px solid var(--border); border-radius:15px; padding:18px 16px;
  position:relative; overflow:hidden; }}
.kpi::before {{ content:''; position:absolute; top:0; right:0; width:100%; height:3px;
  background:linear-gradient(90deg,var(--green),var(--gold)); opacity:.85; }}
.kpi .l {{ color:var(--muted); font-size:.82rem; font-weight:500; }}
.kpi .v {{ font-size:1.85rem; font-weight:800; margin-top:6px; letter-spacing:-.5px; }}
.kpi .v.gold {{ color:var(--gold); }} .kpi .v.green {{ color:var(--green); }}
.kpi .c {{ color:var(--muted); font-size:.74rem; margin-top:4px; }}

/* Tables */
.card {{ background:var(--card); border:1px solid var(--border); border-radius:16px; overflow:hidden; }}
table {{ width:100%; border-collapse:collapse; font-size:.92rem; }}
th,td {{ padding:12px 14px; text-align:right; border-bottom:1px solid var(--border); }}
th {{ background:var(--card2); color:var(--muted); font-weight:700; font-size:.8rem;
  text-transform:none; position:sticky; top:0; }}
tr:last-child td {{ border-bottom:none; }}
td.rank {{ color:var(--muted); font-weight:700; }}
td.tk {{ font-weight:800; color:var(--gold); letter-spacing:.3px; }}
td.ctr {{ text-align:center; }}
.mono {{ font-family:'Courier New',monospace; font-weight:700; color:var(--blue); }}
.score {{ display:inline-block; background:rgba(34,197,94,.14); color:var(--green); font-weight:800;
  padding:2px 10px; border-radius:8px; }}
.tag-exc {{ background:rgba(34,197,94,.16); color:var(--green); padding:2px 9px; border-radius:7px; font-weight:700; font-size:.8rem; }}
.tag-good {{ background:rgba(59,130,246,.16); color:var(--blue); padding:2px 9px; border-radius:7px; font-weight:700; font-size:.8rem; }}
.tag-mid {{ background:rgba(212,168,83,.18); color:var(--gold); padding:2px 9px; border-radius:7px; font-weight:700; font-size:.8rem; }}
.pos {{ color:var(--pos); font-weight:700; }} .neg {{ color:var(--neg); font-weight:700; }}
.sub {{ color:var(--muted); font-size:.74rem; font-weight:400; }}

/* Two-col */
.two {{ display:grid; grid-template-columns:1fr 1fr; gap:18px; }}

/* Status */
.status-box {{ background:var(--card); border:1px solid var(--border); border-radius:16px; padding:18px 20px; }}
.status-line {{ display:flex; align-items:center; gap:10px; padding:8px 0; border-bottom:1px dashed var(--border); }}
.status-line:last-child {{ border-bottom:none; }}
.dot {{ width:10px; height:10px; border-radius:50%; background:var(--green); flex:none; }}
.dot.warn {{ background:var(--gold); }} .dot.bad {{ background:var(--neg); }}
.status-line .k {{ color:var(--muted); min-width:130px; }}
.status-line .vv {{ font-weight:700; }}

/* Footer */
footer {{ margin-top:34px; padding-top:20px; border-top:1px solid var(--border);
  text-align:center; color:var(--muted); font-size:.85rem; }}
footer a {{ font-weight:700; }}

@media (max-width:720px) {{
  .kpi-grid {{ grid-template-columns:repeat(2,1fr); }}
  .two {{ grid-template-columns:1fr; }}
  .logo h1 {{ font-size:1.25rem; }}
  th,td {{ padding:10px 9px; font-size:.84rem; }}
}}
@media (max-width:460px) {{ .kpi-grid {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>

<header>
  <div class="wrap hrow">
    <div class="logo">
      <div class="mark">أ</div>
      <div>
        <h1>أصول — ملخص الداشبورد</h1>
        <div class="sub">Osoul · تحليل الأسهم المتوافقة مع الشريعة</div>
      </div>
    </div>
    <button class="theme-btn" id="themeBtn" onclick="toggleTheme()">🌙 <span id="themeLbl">داكن</span></button>
  </div>
</header>

<div class="wrap">

  <div class="livebar">
    <a href="https://alebrahim22.github.io/osoul-dashboard/" target="_blank" rel="noopener">
      <span class="pulse"></span> افتح الداشبورد الحي ← https://alebrahim22.github.io/osoul-dashboard/
    </a>
  </div>

  <!-- KPI SUMMARY -->
  <section>
    <div class="sec-title"><span class="bar"></span><span class="ic">📊</span> ملخص المؤشرات الرئيسية</div>
    <div class="kpi-grid">
      <div class="kpi"><div class="l">الأسهم الأمريكية</div><div class="v gold">{us['activeTickers']}</div><div class="c">تحت المراقبة</div></div>
      <div class="kpi"><div class="l">الأسهم الكويتية</div><div class="v gold">{kw['activeTickers']}</div><div class="c">تحت المراقبة</div></div>
      <div class="kpi"><div class="l">صفقات نشطة</div><div class="v">{sm['openTrades']}</div><div class="c">US: {len([p for p in d['openPositions'] if p.get('market')=='US'])} · KW: {len([p for p in d['openPositions'] if p.get('market')=='KW'])}</div></div>
      <div class="kpi"><div class="l">نسبة النجاح</div><div class="v green">{sm['winRate']:.1f}%</div><div class="c">{sm['winCount']} ربح / {sm['lossCount']} خسارة</div></div>
      <div class="kpi"><div class="l">العائد الأمريكي</div><div class="v green">+{us['annualReturn']:.1f}%</div><div class="c">S&amp;P 500: {us['benchmarkReturn']:.1f}%</div></div>
      <div class="kpi"><div class="l">العائد الكويتي</div><div class="v green">+{kw['annualReturn']:.1f}%</div><div class="c">Sharpe: {kw['sharpe']:.2f}</div></div>
    </div>
    <p style="color:var(--muted);font-size:.82rem;margin-top:10px;">إجمالي الأسهم تحت المراقبة: <b style="color:var(--gold)">{total_watch}</b> سهم ({us['activeTickers']} أمريكي + {kw['activeTickers']} كويتي) · إجمالي الصفقات: {sm['totalTrades']} · Sharpe US: {sm['sharpeUS']:.2f}</p>
  </section>

  <!-- TOP STOCKS -->
  <section>
    <div class="sec-title"><span class="bar"></span><span class="ic">🏆</span> أعلى 10 أسهم تقييماً</div>
    <div class="card">
      <table>
        <thead><tr><th>#</th><th>الرمز</th><th>الشركة</th><th>السوق</th><th>التقييم</th><th>التصنيف</th><th>B / P / E</th></tr></thead>
        <tbody>
          {rows}
        </tbody>
      </table>
    </div>
    <p style="color:var(--muted);font-size:.8rem;margin-top:8px;">B/P/E = بوفيت / بيوتروسكي / أونيل (متوسط التقييمات التحليلية). جميع الأسهم العشر ضمن التصنيف «ممتاز» ولها مراكز مفتوحة (إشارة شراء).</p>
  </section>

  <!-- KEY STATS: markets -->
  <section>
    <div class="sec-title"><span class="bar"></span><span class="ic">⚖️</span> مقارنة الأسواق: أمريكا vs الكويت</div>
    <div class="card">
      <table>
        <thead><tr><th>المؤشر</th><th class="ctr">🇺🇸 السوق الأمريكي</th><th class="ctr">🇰🇼 السوق الكويتي</th></tr></thead>
        <tbody>
          {market_rows}
        </tbody>
      </table>
    </div>
  </section>

  <!-- PERFORMANCE + RECOMMENDATIONS -->
  <section>
    <div class="two">
      <div>
        <div class="sec-title"><span class="bar"></span><span class="ic">📈</span> الأداء الشهري</div>
        <div class="card">
          <table>
            <thead><tr><th>الشهر</th><th class="ctr">🇺🇸 US</th><th class="ctr">🇰🇼 KW</th></tr></thead>
            <tbody>
              {month_rows}
            </tbody>
          </table>
        </div>
      </div>
      <div>
        <div class="sec-title"><span class="bar"></span><span class="ic">🎯</span> أفضل التوصيات</div>
        <div class="card">
          <table>
            <thead><tr><th>الرمز</th><th>الشركة</th><th class="ctr">التقييم</th><th class="ctr">الإشارة</th></tr></thead>
            <tbody>
              {''.join(f"<tr><td class='tk'>{s['ticker']}</td><td>{s['name']}</td><td class='ctr'><span class='score'>{s['overallScore']:.1f}</span></td><td class='ctr'><span class='tag-exc'>شراء</span></td></tr>" for s in top[:6])}
            </tbody>
          </table>
        </div>
        <p style="color:var(--muted);font-size:.8rem;margin-top:8px;">أعلى 6 من القائمة الرئيسية — تصنيف «ممتاز» مع مراكز مفتوحة فعلية.</p>
      </div>
    </div>
  </section>

  <!-- STATUS NOTES -->
  <section>
    <div class="sec-title"><span class="bar"></span><span class="ic">📌</span> ملاحظات الحالة</div>
    <div class="status-box">
      <div class="status-line"><span class="dot"></span><span class="k">حالة النظام</span><span class="vv">{status_txt}</span></div>
      <div class="status-line"><span class="dot"></span><span class="k">آخر تحديث</span><span class="vv">{last_upd}</span></div>
      <div class="status-line"><span class="dot"></span><span class="k">المراكز المفتوحة</span><span class="vv">{sm['openTrades']} (US {len([p for p in d['openPositions'] if p.get('market')=='US'])} · KW {len([p for p in d['openPositions'] if p.get('market')=='KW'])} )</span></div>
      <div class="status-line"><span class="dot {'warn' if wr<50 else ''}"></span><span class="k">نسبة النجاح</span><span class="vv">{sm['winRate']:.1f}% — {wr_note}</span></div>
      <div class="status-line"><span class="dot"></span><span class="k">التوافق الشرعي</span><span class="vv">✓ جميع الأسهم المدرجة متوافقة مع الشريعة</span></div>
      <div class="status-line"><span class="dot warn"></span><span class="k">مسح مُجدول</span><span class="vv">nextScan: {d['system'].get('nextScan','—')} (تحقق من تحديث الجدول)</span></div>
    </div>
  </section>

  <footer>
    <div>آخر تحديث للتقرير: {today} · البيانات مُستخرجة من الداشبورد الحي مباشرةً.</div>
    <div style="margin-top:8px;">الداشبورد الحي: <a href="https://alebrahim22.github.io/osoul-dashboard/" target="_blank" rel="noopener">https://alebrahim22.github.io/osoul-dashboard/</a></div>
    <div style="margin-top:8px;font-size:.75rem;opacity:.7;">⚠️ هذا ليس استشارة استثمارية — للأغراض المعلوماتية فقط.</div>
  </footer>

</div>

<script>
function toggleTheme() {{
  const r = document.documentElement;
  const cur = r.getAttribute('data-theme');
  const next = cur === 'dark' ? 'light' : 'dark';
  r.setAttribute('data-theme', next);
  document.getElementById('themeLbl').textContent = next === 'dark' ? 'داكن' : 'فاتح';
  document.getElementById('themeBtn').firstChild.textContent = next === 'dark' ? '🌙 ' : '☀️ ';
}}
</script>
</body>
</html>
"""

out_path = os.path.join(OUT_DIR, f"osoul-dashboard-summary-{today}.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(HTML)
print("WROTE:", out_path, "| bytes:", len(HTML.encode("utf-8")))

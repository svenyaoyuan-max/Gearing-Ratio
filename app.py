"""
Gearing Ratio Analyser — Streamlit App
Imports data functions from gearing_ratio.py in the same folder.
"""

import pandas as pd
import streamlit as st

# ── Load data functions from gearing_ratio.py (same directory) ───────────────
from gearing_ratio import stock_profile_cninfo, stock_financial_report_sina


# ── Helpers ───────────────────────────────────────────────────────────────────
def fmt_num(value) -> str:
    try:
        return f"{int(float(value)):,}"
    except (TypeError, ValueError):
        return str(value)


def gr_color(gr: float) -> str:
    if gr <= 100:  return "#16a34a"
    if gr <= 200:  return "#d97706"
    if gr <= 300:  return "#ea580c"
    return "#dc2626"


def gr_bg(gr: float) -> str:
    if gr <= 100:  return "#f0fdf4"
    if gr <= 200:  return "#fffbeb"
    if gr <= 300:  return "#fff7ed"
    return "#fef2f2"


# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GR Analyser",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
/* ── Reset & base ── */
.stApp { background-color: #f1f5f9 !important; }
[data-testid="stHeader"] { display: none; }
[data-testid="stMainBlockContainer"] { padding: 0 1.2rem 0.5rem !important; }
.block-container { padding-top: 0 !important; max-width: 100% !important; }
div[data-testid="stVerticalBlock"] > div { gap: 0 !important; }

/* ── Header ── */
.gr-header {
  background: #ffffff; border-bottom: 2px solid #e2e8f0;
  padding: 0.55rem 1rem; margin: 0 -1.2rem 0.7rem;
  display: flex; align-items: center; gap: 0.75rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.gr-logo {
  background: linear-gradient(135deg, #1d4ed8, #3b82f6);
  border-radius: 9px; width: 36px; height: 36px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.9rem; font-weight: 900; color: #fff; letter-spacing: -0.5px;
}
.gr-header h1 { color: #0f172a; font-size: 1.1rem; margin: 0; font-weight: 700; }
.gr-header p  { color: #94a3b8; font-size: 0.72rem; margin: 0; }

/* ── Key panel ── */
.key-panel {
  background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px;
  margin-bottom: 0.7rem; overflow: hidden;
  box-shadow: 0 2px 6px rgba(0,0,0,0.07);
}
.key-panel-hdr {
  background: #f8fafc; border-bottom: 1px solid #e2e8f0;
  padding: 0.3rem 1rem;
  font-size: 0.68rem; font-weight: 700; color: #64748b; letter-spacing: 0.09em; text-transform: uppercase;
}
.gr-center {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 0.9rem 1rem;
}
.gr-main-label { font-size: 0.68rem; font-weight: 700; color: #94a3b8;
                 text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.2rem; }
.gr-main-num   { font-size: 3.2rem; font-weight: 900; line-height: 1; }

/* ── Risk boxes ── */
.risk-box {
  border-radius: 10px; padding: 0.75rem 0.9rem;
  height: 100%; display: flex; flex-direction: column; justify-content: center;
}
.risk-pass { background: #f0fdf4; border: 1.5px solid #86efac; }
.risk-fail { background: #fef2f2; border: 1.5px solid #fca5a5; }
.risk-icon  { font-size: 1.1rem; }
.risk-head  { font-size: 0.82rem; font-weight: 700; margin: 0.2rem 0 0.15rem; }
.pass-head  { color: #15803d; }
.fail-head  { color: #b91c1c; }
.risk-sub   { font-size: 0.75rem; color: #475569; line-height: 1.35; }

/* ── Cards ── */
.card {
  background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px;
  padding: 0.65rem 0.9rem; margin-bottom: 0.7rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.card-title {
  font-size: 0.68rem; font-weight: 700; color: #64748b;
  text-transform: uppercase; letter-spacing: 0.09em;
  margin: 0 0 0.45rem; padding-bottom: 0.35rem;
  border-bottom: 1px solid #f1f5f9;
}

/* ── Info rows — strictly uniform font ── */
.row {
  display: flex; justify-content: space-between; align-items: baseline;
  border-bottom: 1px solid #f1f5f9; padding: 0.22rem 0;
  font-size: 0.78rem; font-weight: 400; color: #0f172a;
}
.row:last-child { border-bottom: none; }
.rl    { color: #64748b; flex: 1; font-size: 0.78rem; font-weight: 400; }
.rv    { color: #0f172a; text-align: right; font-size: 0.78rem; font-weight: 400;
         font-family: 'SF Mono','Menlo',monospace; }
/* highlight = blue + bold, used ONLY for GR before/after rows */
.rv-hi { color: #1d4ed8; text-align: right; font-size: 0.78rem; font-weight: 700;
         font-family: 'SF Mono','Menlo',monospace; }

/* ── Inputs ── */
.stTextInput input, .stNumberInput input {
  background: #fff !important; color: #0f172a !important;
  border: 1px solid #cbd5e1 !important; border-radius: 7px !important;
  font-size: 0.85rem !important; padding: 0.35rem 0.6rem !important;
}
label { font-size: 0.78rem !important; color: #475569 !important; }
.stButton > button {
  background: linear-gradient(135deg, #1d4ed8, #3b82f6) !important;
  color: #fff !important; border: none !important; border-radius: 7px !important;
  font-weight: 700 !important; width: 100% !important; font-size: 0.85rem !important;
  padding: 0.42rem 1rem !important;
}
hr { border-color: #e2e8f0 !important; margin: 0.5rem 0 !important; }
.stAlert { font-size: 0.82rem !important; }
</style>
""", unsafe_allow_html=True)


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="gr-header">
  <div class="gr-logo">GR</div>
  <div>
    <h1>Gearing Ratio Analyser</h1>
    <p>Live data · CNInfo &amp; Sina Finance · A-share / B-share</p>
  </div>
</div>
""", unsafe_allow_html=True)


# ── Inputs ────────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns([2, 2, 1, 0.5])
with c1:
    ticker = st.text_input("Stock Ticker (6 digits)", placeholder="e.g. 600030", max_chars=6)
with c2:
    proposed_m_raw = st.text_input("Proposed Borrowing (million ¥)", value="0", placeholder="0")
with c3:
    st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)
    run = st.button("Analyse", use_container_width=True)
with c4:
    st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)
    with st.popover("ℹ️", use_container_width=True):
        st.markdown("""
### Gearing Ratio Methodology

**Formula**: Total Financial Debt ÷ Total Equity × 100%

Company type is auto-detected from CNInfo industry data and balance sheet structure.

---

#### 📦 Standard (Non-Financial) Companies
| Item | Source column |
|------|--------------|
| **Debt** | 短期借款 + 应付票据 + 一年内到期的非流动负债 + 应付债券 + 长期借款 + 租赁负债 |
| **Equity** | 所有者权益(或股东权益)合计 |

---

#### 🏦 Commercial Banks
| Item | Source column |
|------|--------------|
| **Debt** | 卖出回购金融资产款 + 向中央银行借款 + 应付债券 + 租赁负债 |
| **Equity** | 所有者权益合计 (incl. 其他权益工具 / AT1 perpetual bonds) |

*Excludes: customer deposits (core business), 拆入资金 (interbank money market)*

---

#### 📈 Securities / Brokerage Firms
| Item | Source column |
|------|--------------|
| **Debt** | 卖出回购金融资产款 + 应付短期融资款 + 短期借款 + 拆入资金 + 应付债券(all sub-items) + 长期借款 + 租赁负债 |
| **Equity** | 所有者权益合计 |

---

#### 🛡️ Pure-play Insurers *(e.g. China Life, China Pacific)*
| Item | Source column |
|------|--------------|
| **Debt** | 短期借款 + 应付短期融资款 + 应付债券(all sub-items) + 长期借款 + 租赁负债 |
| **Equity** | 所有者权益合计 |

*Excludes: 卖出回购金融资产款 (portfolio liquidity management, not financing)*

---

#### 🏛️ Insurance Conglomerates with Banking Subsidiary *(e.g. Ping An)*
Detected when 吸收存款 > 0 in consolidated balance sheet.

| Item | Source column |
|------|--------------|
| **Debt** | 吸收存款 + 卖出回购金融资产款 + 拆入资金 + 应付短期融资款 + 短期借款 + 应付债券(all sub-items) + 长期借款 + 租赁负债 |
| **Equity** | 所有者权益合计 |

---

#### Equity Fallback (Financial Institutions)
When the standard equity column is absent, the app tries in order:
1. 所有者权益合计 / 归属于母公司股东权益合计
2. Dynamic scan for columns containing 权益+合计 (excluding asset-side items)
3. Sum of components: 股本 + 资本公积 + 盈余公积 + 一般风险准备 + 未分配利润 + 其他综合收益 + 少数股东权益 + 其他权益工具 (AT1)

---

#### Data Sources
- **Company profile**: CNInfo (webapi.cninfo.com.cn)
- **Balance sheet**: Sina Finance (quotes.sina.cn)
- **Period**: Most recent quarterly filing

#### Risk Checks
1. **Gearing > 300%** — exceeds typical bank covenant threshold
2. **Proposed > 2× existing debt** — size check on new issuance
""")


st.markdown("<hr>", unsafe_allow_html=True)

if "result" not in st.session_state:
    st.session_state.result = None


# ── Calculate ─────────────────────────────────────────────────────────────────
if run:
    if len(ticker) != 6 or not ticker.isdigit():
        st.error("Please enter a valid 6-digit stock ticker.")
        st.stop()

    try:
        proposed_borrowing = int(float(proposed_m_raw.replace(",", "").strip())) * 1_000_000
    except (ValueError, AttributeError):
        proposed_borrowing = 0

    with st.spinner("Fetching data…"):
        try:
            profile_df = stock_profile_cninfo(symbol=ticker)
            if profile_df.empty:
                st.error(f"No company found for ticker {ticker}.")
                st.stop()

            prof_cols = ['公司名称', '英文名称', '所属市场', 'A股代码', 'B股代码', '主营业务']
            prof_vals = profile_df.loc[0, prof_cols].values.tolist()
            prof_lbls = profile_df.loc[0, prof_cols].index.tolist()

            market    = str(profile_df.loc[0, "所属市场"])
            sina_code = ("sh" if "上海" in market or ticker.startswith(("6","9")) else "sz") + ticker

            df2 = stock_financial_report_sina(stock=sina_code, symbol="资产负债表").head(1)
            cols = df2.columns.tolist()

            # ── Detect institution type ───────────────────────────────────────
            industry = str(profile_df.loc[0, '所属行业']) if '所属行业' in profile_df.columns else ''
            eng_name = str(profile_df.loc[0, '英文名称']) if '英文名称' in profile_df.columns else ''
            is_bank = '所有者权益(或股东权益)合计' not in cols
            is_securities = is_bank and ('证券' in industry or 'Securities' in eng_name
                                         or 'Brokerage' in eng_name)
            is_insurance  = is_bank and ('保险' in industry or 'Insurance' in eng_name)

            def safe(col):
                """Return value or 0 if column missing."""
                if col in cols:
                    v = df2.loc[0, col]
                    return 0 if pd.isna(v) else float(v)
                return 0

            def fmt_date(raw):
                """Convert 2026-03-31 or 20260331 → 2026/03/31."""
                s = str(raw).strip()
                if len(s) == 8 and s.isdigit():
                    return f"{s[:4]}/{s[4:6]}/{s[6:]}"
                return s.replace("-", "/")

            report_date = fmt_date(df2.loc[0, '报告日'] if '报告日' in cols else "")

            found_eq_col = '所有者权益(或股东权益)合计'
            _debug_eq    = {}

            if not is_bank:
                # ── Standard company ─────────────────────────────────────────
                debt_items = [
                    ('短期借款',              safe('短期借款')),
                    ('应付票据',              safe('应付票据')),
                    ('一年内到期的非流动负债', safe('一年内到期的非流动负债')),
                    ('应付债券',              safe('应付债券')),
                    ('长期借款',              safe('长期借款')),
                    ('租赁负债',              safe('租赁负债')),
                ]
                equity = safe('所有者权益(或股东权益)合计')
            elif is_securities:
                # ── Securities / brokerage firm ───────────────────────────────
                # Refinitiv: repo + ST financing + interbank + bonds + LT loans + leases
                # Note: '应付债券' may be 0 in Sina for securities firms — bonds can
                # appear in sub-category columns containing '债券'; we scan for them.
                _bond_cols = [c for c in cols if '债券' in c and '应收' not in c]
                _bond_total = sum(safe(c) for c in _bond_cols)
                debt_items = [
                    ('卖出回购金融资产款', safe('卖出回购金融资产款')),
                    ('应付短期融资款',     safe('应付短期融资款')),
                    ('短期借款',           safe('短期借款')),
                    ('拆入资金',           safe('拆入资金')),
                    ('应付债券(合计)',      _bond_total),
                    ('长期借款',           safe('长期借款')),
                    ('租赁负债',           safe('租赁负债')),
                ]
            elif is_insurance:
                # ── Insurance: split by conglomerate vs pure-play ─────────────
                # Key Refinitiv rule:
                #   Conglomerate (has banking subsidiary, 吸收存款 > 0):
                #     → include bank deposits + repo + all borrowings
                #   Pure-play insurer (吸收存款 = 0):
                #     → EXCLUDE repo (it's portfolio liquidity, not financing)
                #     → only bonds + bank loans + leases
                _ins_bond_cols = [c for c in cols if '债券' in c and '应收' not in c]
                _ins_bond_total = sum(safe(c) for c in _ins_bond_cols)
                _has_bank_sub = safe('吸收存款') > 0

                if _has_bank_sub:
                    # Insurance conglomerate (e.g. 601318 Ping An)
                    debt_items = [
                        ('吸收存款',           safe('吸收存款')),
                        ('卖出回购金融资产款', safe('卖出回购金融资产款')),
                        ('拆入资金',           safe('拆入资金')),
                        ('应付短期融资款',     safe('应付短期融资款')),
                        ('短期借款',           safe('短期借款')),
                        ('应付债券(合计)',      _ins_bond_total),
                        ('长期借款',           safe('长期借款')),
                        ('租赁负债',           safe('租赁负债')),
                    ]
                else:
                    # Pure-play insurer (e.g. 601628 China Life, 601601 China Pacific)
                    # Repo excluded — portfolio management tool, not financing
                    debt_items = [
                        ('短期借款',       safe('短期借款')),
                        ('应付短期融资款', safe('应付短期融资款')),
                        ('应付债券(合计)',  _ins_bond_total),
                        ('长期借款',       safe('长期借款')),
                        ('租赁负债',       safe('租赁负债')),
                    ]
            else:
                # ── Commercial bank ───────────────────────────────────────────
                # Matches Refinitiv: repo + PBoC + bonds + leases
                debt_items = [
                    ('卖出回购金融资产款', safe('卖出回购金融资产款')),
                    ('向中央银行借款',     safe('向中央银行借款')),
                    ('应付债券',           safe('应付债券')),
                    ('租赁负债',           safe('租赁负债')),
                ]

            # ── Equity: shared progressive search for all financial types ─────
            if is_bank:
                equity = 0
                found_eq_col = '股东权益合计'
                total_assets_prelim = safe('资产总计')
                _min_eq = total_assets_prelim * 0.03 if total_assets_prelim else 1e9

                # 1) Exact known names
                for _eq_col in ['所有者权益合计',
                                 '归属于母公司股东权益合计',
                                 '归属于母公司所有者的权益合计',
                                 '归属于母公司股东的权益合计',
                                 '股东权益合计']:
                    _v = safe(_eq_col)
                    if _v >= _min_eq:
                        equity = _v; found_eq_col = _eq_col; break

                # 2) Dynamic scan: 权益+合计, exclude asset-side cols, plausibly large
                if equity == 0:
                    _asset_kw = ('投资', '工具', '持有', '收益', '减值', '摊销')
                    for _eq_col in cols:
                        if ('权益' in _eq_col and '合计' in _eq_col
                                and not any(k in _eq_col for k in _asset_kw)):
                            _v = safe(_eq_col)
                            if _v >= _min_eq:
                                equity = _v; found_eq_col = _eq_col; break

                # 3) Sum components as last resort
                if equity == 0:
                    _parts = ['股本', '实收资本', '资本公积', '盈余公积',
                              '一般风险准备', '未分配利润', '其他综合收益',
                              '少数股东权益', '其他权益工具', '永续债']
                    _sum = sum(safe(c) for c in _parts)
                    if _sum >= _min_eq:
                        equity = _sum; found_eq_col = '(sum of components)'

                _debug_eq = {c: safe(c) for c in cols if '权益' in c} if equity == 0 else {}

            total_debt0 = sum(v for _, v in debt_items)
            total_debt1 = total_debt0 + float(proposed_borrowing)
            gr_before   = total_debt0 / equity * 100 if equity else 0
            gr_after    = total_debt1 / equity * 100 if equity else 0
            total_assets = safe('资产总计')

            equity_col  = found_eq_col if is_bank else '所有者权益(或股东权益)合计'
            _debug_eq   = (_debug_eq if is_bank and equity == 0 else {})
            inst_type   = ('Securities' if is_securities
                           else 'Insurance' if is_insurance
                           else 'Bank' if is_bank else '')
            st.session_state.result = {
                "prof_lbls":    prof_lbls,   "prof_vals":   prof_vals,
                "debt_items":   debt_items,
                "report_date":  report_date,
                "equity":       equity,      "equity_col":  equity_col,
                "total_assets": total_assets,
                "total_debt0":  total_debt0, "proposed":    proposed_borrowing,
                "total_debt1":  total_debt1,
                "gr_before":    gr_before,   "gr_after":    gr_after,
                "is_bank":      is_bank,     "debug_eq":    _debug_eq,
                "inst_type":    inst_type,
            }

        except Exception as e:
            st.error(f"Error: {e}")
            st.stop()


# ── Display ───────────────────────────────────────────────────────────────────
if st.session_state.result:
    r   = st.session_state.result
    gr  = r["gr_after"]
    col = gr_color(gr)
    bg  = gr_bg(gr)
    ratio = r["proposed"] / r["total_debt0"] if r["total_debt0"] > 0 else 0

    # ── KEY PANEL ─────────────────────────────────────────────────────────────
    st.markdown('<div class="key-panel">', unsafe_allow_html=True)
    st.markdown('<div class="key-panel-hdr">📐 GEARING RATIO RESULT &amp; RISK CHECKS</div>', unsafe_allow_html=True)

    kc1, kc2, kc3 = st.columns([1, 1.1, 1.1])

    with kc1:
        st.markdown(f"""
        <div class="gr-center" style="background:{bg};height:120px;border-right:1px solid #e2e8f0">
          <div class="gr-main-label">Gearing Ratio (After)</div>
          <div class="gr-main-num" style="color:{col}">{gr:.2f}%</div>
        </div>""", unsafe_allow_html=True)

    with kc2:
        if gr > 300:
            st.markdown(f"""
            <div style="padding:0.75rem 0.9rem;height:120px;display:flex;align-items:center;border-right:1px solid #e2e8f0">
              <div class="risk-box risk-fail" style="width:100%">
                <div class="risk-icon">🔴</div>
                <div class="risk-head fail-head">Exceeds 300% Limit</div>
                <div class="risk-sub">Gearing ratio <b>{gr:.2f}%</b> exceeds the 300% threshold.</div>
              </div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="padding:0.75rem 0.9rem;height:120px;display:flex;align-items:center;border-right:1px solid #e2e8f0">
              <div class="risk-box risk-pass" style="width:100%">
                <div class="risk-icon">🟢</div>
                <div class="risk-head pass-head">Within 300% Limit</div>
                <div class="risk-sub">Gearing ratio <b>{gr:.2f}%</b> is within the acceptable threshold.</div>
              </div>
            </div>""", unsafe_allow_html=True)

    with kc3:
        if ratio > 2:
            st.markdown(f"""
            <div style="padding:0.75rem 0.9rem;height:120px;display:flex;align-items:center">
              <div class="risk-box risk-fail" style="width:100%">
                <div class="risk-icon">🔴</div>
                <div class="risk-head fail-head">Exceeds 2× Current Debt</div>
                <div class="risk-sub">Proposed is <b>{ratio:.2f}×</b> the current total debt.</div>
              </div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="padding:0.75rem 0.9rem;height:120px;display:flex;align-items:center">
              <div class="risk-box risk-pass" style="width:100%">
                <div class="risk-icon">🟢</div>
                <div class="risk-head pass-head">Within 2× Guideline</div>
                <div class="risk-sub">Proposed is <b>{ratio:.2f}×</b> the current total debt.</div>
              </div>
            </div>""", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ── DETAIL ROW ────────────────────────────────────────────────────────────
    d1, d2, d3 = st.columns([1, 1, 1.2])

    # ── Company Profile ───────────────────────────────────────────────────────
    with d1:
        st.markdown('<div class="card"><div class="card-title">🏢 Company Profile</div>', unsafe_allow_html=True)
        for lbl, val in zip(r["prof_lbls"], r["prof_vals"]):
            st.markdown(
                f'<div class="row">'
                f'<span class="rl">{lbl}</span>'
                f'<span class="rv" style="font-family:inherit">{val or "—"}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Debt Summary ──────────────────────────────────────────────────────────
    with d2:
        inst_tag = f' · {r["inst_type"]} Method' if r.get("inst_type") else ''
        st.markdown(f'<div class="card"><div class="card-title">💰 Debt Summary{inst_tag}</div>', unsafe_allow_html=True)
        for lbl, val, hi in [
            ("Gearing — Before",     f"{r['gr_before']:.2f}%",  True),
            ("Gearing — After",      f"{gr:.2f}%",              True),
            ("Total Debt — Before",  fmt_num(r["total_debt0"]), False),
            ("Proposed Borrowing",   fmt_num(r["proposed"]),    False),
            ("Total Debt — After",   fmt_num(r["total_debt1"]), False),
            ("Shareholders' Equity", fmt_num(r["equity"]),      False),
        ]:
            st.markdown(
                f'<div class="row">'
                f'<span class="rl">{lbl}</span>'
                f'<span class="rv{"-hi" if hi else ""}">{val}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Balance Sheet ─────────────────────────────────────────────────────────
    with d3:
        st.markdown('<div class="card"><div class="card-title">📋 Balance Sheet Detail</div>', unsafe_allow_html=True)

        # Report date
        st.markdown(
            f'<div class="row">'
            f'<span class="rl">Report Date</span>'
            f'<span class="rv" style="font-family:inherit">{r["report_date"]}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Debt line items
        for lbl, val in r["debt_items"]:
            st.markdown(
                f'<div class="row">'
                f'<span class="rl">{lbl}</span>'
                f'<span class="rv">{fmt_num(val)}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # Total debt separator
        st.markdown(
            f'<div class="row" style="border-top:1.5px solid #e2e8f0;margin-top:0.2rem;padding-top:0.3rem">'
            f'<span class="rl">Total Debt</span>'
            f'<span class="rv">{fmt_num(r["total_debt0"])}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Equity and total assets
        equity_lbl = r.get("equity_col", '股东权益合计') if r["is_bank"] else '所有者权益(或股东权益)合计'
        for lbl, val in [(equity_lbl, r["equity"]), ('资产总计', r["total_assets"])]:
            st.markdown(
                f'<div class="row">'
                f'<span class="rl">{lbl}</span>'
                f'<span class="rv">{fmt_num(val)}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)

    # ── Debug: show 权益 columns if equity not found ──────────────────────────
    if r.get("debug_eq"):
        with st.expander("⚠️ Equity not detected — available 权益 columns (for diagnosis)"):
            for col_name, col_val in r["debug_eq"].items():
                st.text(f"{col_name}: {col_val:,.0f}" if col_val else f"{col_name}: 0")

else:
    st.markdown("""
    <div style='text-align:center;padding:4rem 2rem'>
      <div style='font-size:2.5rem;margin-bottom:0.8rem'>📐</div>
      <div style='font-size:0.95rem;color:#94a3b8;font-weight:500'>
        Enter a stock ticker and proposed borrowing, then click Analyse
      </div>
      <div style='font-size:0.75rem;color:#cbd5e1;margin-top:0.3rem'>
        Supports A-share and B-share · Live data from CNInfo &amp; Sina Finance
      </div>
    </div>
    """, unsafe_allow_html=True)

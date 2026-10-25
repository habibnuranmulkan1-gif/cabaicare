"""CabaiCare — UI baru untuk sistem pakar rekomendasi pemupukan tanaman cabai."""
from __future__ import annotations

import html
import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

from engine import ExpertSystem
from storage import (
    HISTORY_PATH,
    append_history,
    load_knowledge_base,
    save_knowledge_base,
)

st.set_page_config(
    page_title="CabaiCare | Cek Tanaman Cabai",
    page_icon="🌶️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Data ──────────────────────────────────────────────────────────────────
try:
    kb = load_knowledge_base()
except (OSError, json.JSONDecodeError, ValueError) as exc:
    st.error(f"Basis pengetahuan gagal dibaca: {exc}")
    st.stop()

# ─── Single visual system: warm botanical light theme ───────────────────────
# Tidak ada pengalih tema. Seluruh aplikasi memakai satu palet terang yang
# konsisten dengan identitas natural CabaiCare.
header_left, header_mid = st.columns([1.65, 4.35], vertical_alignment="center")
with header_left:
    st.markdown(
        """
        <div class="cc-brand">
          <div class="cc-brand-icon">🌶️</div>
          <div><div class="cc-brand-name">CabaiCare<span>•</span></div>
          <div class="cc-brand-sub">Teman merawat cabai</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with header_mid:
    st.markdown(
        '<div class="cc-header-caption">ASISTEN PEMUPUKAN TANAMAN CABAI <span class="cc-live-dot"></span><span class="cc-caption-extra">Praktis, ramah, dan transparan</span></div>',
        unsafe_allow_html=True,
    )

theme = {
    "scheme": "light", "page": "#D2E6C9", "sidebar": "#C9DFC4",
    "surface": "#EEF6EA", "surface_alt": "#DEEDD9", "widget": "#EAF3E5",
    "text": "#183B29", "muted": "#56745C", "border": "#C5DCC1",
    "primary": "#317B49", "primary_hover": "#28663C", "green": "#4B9755",
    "green_deep": "#205437", "green_soft": "#DCEFD8", "info_bg": "#EAF5DF",
    "info_text": "#2E5B40", "table_head": "#E1EFDC", "shadow": "rgba(31, 74, 52, .14)",
    "input": "#EAF3E5", "input_text": "#203D2D", "input_border": "#B5D1AF",
    "nav_active": "#C6E3C1", "nav_active_text": "#234E3D", "hero_a": "#B8DDB7",
    "hero_b": "#E0EBBC", "select_hover": "#D5EACF",
}

CSS_TEMPLATE = r"""
<style>
:root {
  color-scheme: __SCHEME__;
    --primary-color: __PRIMARY__;
    --st-primary-color: __PRIMARY__;
  --cc-page: __PAGE__; --cc-sidebar: __SIDEBAR__; --cc-surface: __SURFACE__;
  --cc-surface-alt: __SURFACE_ALT__; --cc-widget: __WIDGET__; --cc-text: __TEXT__;
  --cc-muted: __MUTED__; --cc-border: __BORDER__; --cc-primary: __PRIMARY__;
  --cc-primary-hover: __PRIMARY_HOVER__; --cc-green: __GREEN__;
  --cc-green-deep: __GREEN_DEEP__; --cc-green-soft: __GREEN_SOFT__;
  --cc-info-bg: __INFO_BG__; --cc-info-text: __INFO_TEXT__; --cc-table-head: __TABLE_HEAD__;
  --cc-shadow: __SHADOW__; --cc-input: __INPUT__; --cc-input-text: __INPUT_TEXT__;
  --cc-input-border: __INPUT_BORDER__; --cc-nav-active: __NAV_ACTIVE__;
  --cc-nav-active-text: __NAV_ACTIVE_TEXT__; --cc-hero-a: __HERO_A__;
  --cc-hero-b: __HERO_B__; --cc-select-hover: __SELECT_HOVER__;
}
html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"],
[data-testid="stMainBlockContainer"] {
  background: var(--cc-page) !important; color: var(--cc-text) !important;
  color-scheme: __SCHEME__ !important;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
/* Paksa semua lapisan Streamlit mengikuti satu tema terang, termasuk sidebar dan popover. */
[data-testid="stSidebar"], [data-testid="stSidebar"] > div,
[data-testid="stSidebarContent"], [data-testid="stPopover"], [data-baseweb="popover"] {
  background: var(--cc-sidebar) !important; color: var(--cc-text) !important; color-scheme: light !important;
}
[data-testid="stMain"], [data-testid="stMainBlockContainer"], [data-testid="stBottom"],
[data-testid="stHeader"], [data-testid="stToolbar"] { color-scheme: light !important; }
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"] { right: .65rem; }
[data-testid="stMainBlockContainer"] { max-width: 1500px; padding: 1rem 2.4rem 2.8rem; }
[data-testid="stBottom"] { background: var(--cc-page) !important; }
[data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li, [data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] p, [data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] p, [data-testid="stRadio"] label,
[data-testid="stCheckbox"] label, [data-testid="stToggle"] label,
[data-testid="stSlider"] label, label, h1, h2, h3, h4, h5, h6, p, li, small {
  color: var(--cc-text) !important;
}
p, li { line-height: 1.66; }
h1, h2, h3, h4 { letter-spacing: -.035em; font-weight: 780 !important; }
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p { color: var(--cc-muted) !important; }
a { color: var(--cc-green) !important; text-underline-offset: 3px; }
hr { border-color: var(--cc-border) !important; }
[data-testid="stAlert"] { border-radius: 16px !important; }

/* Header brand: completely new, horizontal and airy. */
.cc-brand { display:flex; align-items:center; gap:.78rem; min-height:3.5rem; }
.cc-brand-icon { width:54px; height:54px; display:grid; place-items:center; border-radius:18px 18px 18px 7px;
  font-size:1.6rem; background:linear-gradient(135deg,#DFF9E9 0%,#FFF7E8 100%);
  border:1px solid var(--cc-border); box-shadow:0 10px 24px var(--cc-shadow); transform:rotate(-2deg); }
.cc-brand-name { color:var(--cc-green-deep)!important; font-size:1.45rem; font-weight:900; letter-spacing:-.055em; line-height:1.2; }
.cc-brand-name span { color:var(--cc-primary)!important; padding-left:.1rem; }
.cc-brand-sub { color:var(--cc-muted)!important; font-size:.76rem; margin-top:.2rem; }
.cc-header-caption { min-height:3rem; display:flex; align-items:center; gap:.6rem; color:var(--cc-muted)!important;
  font-size:.72rem; font-weight:850; letter-spacing:.12em; }
.cc-live-dot { width:9px; height:9px; border-radius:50%; display:inline-block; background:var(--cc-green); box-shadow:0 0 0 6px rgba(46,184,114,.12); }
.cc-caption-extra { letter-spacing:0; font-weight:500; text-transform:none; font-size:.82rem; }
.cc-rule { height:1px; width:100%; background:var(--cc-border); margin:.65rem 0 1.1rem; }

/* Shared surfaces, fresh palette and soft corners. */
[data-testid="stVerticalBlockBorderWrapper"] { border:1px solid var(--cc-border)!important;
  background:var(--cc-surface)!important; border-radius:22px!important; box-shadow:0 7px 24px var(--cc-shadow); }
[data-testid="stVerticalBlockBorderWrapper"] > div { border-radius:inherit; }
.cc-hero { display:grid; grid-template-columns:minmax(0,1.5fr) minmax(240px,.8fr); gap:1rem; align-items:center;
  overflow:hidden; position:relative; padding:2.3rem 2.5rem; border-radius:28px; border:1px solid var(--cc-border);
  background:linear-gradient(115deg,var(--cc-hero-a),var(--cc-hero-b)); box-shadow:0 12px 35px var(--cc-shadow); }
.cc-hero:after { content:""; position:absolute; width:260px; height:260px; border-radius:50%; right:7%; top:-55%;
  background:var(--cc-green-soft); opacity:.7; pointer-events:none; }
.cc-eyebrow { color:var(--cc-green)!important; font-size:.69rem; font-weight:900; letter-spacing:.16em; text-transform:uppercase; }
.cc-hero h1 { color:var(--cc-text)!important; font-size:clamp(2rem,3.3vw,3.4rem); line-height:1.08; letter-spacing:-.06em; margin:.65rem 0 .85rem; max-width:760px; }
.cc-hero h1 em { color:var(--cc-green-deep)!important; font-style:normal; }
.cc-hero p { color:var(--cc-muted)!important; max-width:680px; font-size:1rem; margin:0; }
.cc-hero-pills { display:flex; flex-wrap:wrap; gap:.45rem; margin-top:1.25rem; }
.cc-pill { display:inline-flex; align-items:center; padding:.45rem .72rem; border:1px solid var(--cc-border); border-radius:999px;
  background:var(--cc-surface); color:var(--cc-text)!important; font-size:.72rem; font-weight:750; }
.cc-hero-art { min-height:240px; position:relative; display:grid; place-items:center; z-index:1; }
.cc-art-plate { width:min(100%,300px); min-height:225px; display:grid; place-items:center; border-radius:35% 35% 27px 27px;
  background:radial-gradient(circle at 48% 35%,var(--cc-surface) 0,var(--cc-green-soft) 65%,transparent 66%); }
.cc-art-plate svg { width:min(100%,285px); height:auto; filter:drop-shadow(0 15px 14px var(--cc-shadow)); }
.cc-art-label { position:absolute; right:-.15rem; bottom:.1rem; padding:.7rem .9rem; border-radius:16px;
  border:1px solid var(--cc-border); background:var(--cc-surface); color:var(--cc-text)!important; box-shadow:0 8px 20px var(--cc-shadow); }
.cc-art-label strong { display:block; font-size:.8rem; }
.cc-art-label small { display:block; color:var(--cc-muted)!important; font-size:.68rem; margin-top:.13rem; }
.cc-alert { margin:1rem 0 1.6rem; display:flex; align-items:flex-start; gap:.8rem; padding:1rem 1.15rem;
  border:1px solid var(--cc-border); border-radius:18px; background:var(--cc-surface); }
.cc-alert-icon { display:grid; place-items:center; min-width:36px; height:36px; border-radius:12px; background:var(--cc-green-soft); }
.cc-alert strong { display:block; font-size:.86rem; color:var(--cc-text)!important; }
.cc-alert p { color:var(--cc-muted)!important; font-size:.82rem; margin:.12rem 0 0; }
.cc-section { margin:1.7rem 0 .85rem; }
.cc-section .cc-eyebrow { margin-bottom:.3rem; }
.cc-section h2 { font-size:1.55rem; margin:.18rem 0 .25rem; color:var(--cc-text)!important; }
.cc-section p { color:var(--cc-muted)!important; margin:0; font-size:.9rem; }
.cc-mini-card { height:100%; padding:1.1rem 1.15rem; border:1px solid var(--cc-border); background:var(--cc-surface); border-radius:19px; }
.cc-mini-card .mini-icon { width:38px;height:38px;display:grid;place-items:center;border-radius:13px;background:var(--cc-green-soft);font-size:1.05rem;margin-bottom:.7rem; }
.cc-mini-card h3 { color:var(--cc-text)!important; font-size:.95rem; margin:.1rem 0 .35rem; }
.cc-mini-card p { color:var(--cc-muted)!important; font-size:.8rem; margin:0; }
.cc-feature-label { color:var(--cc-green)!important; font-size:.68rem; font-weight:850; letter-spacing:.12em; text-transform:uppercase; }
.cc-result-banner { display:flex; gap:.85rem; align-items:flex-start; padding:1.1rem 1.2rem; border-radius:20px;
  border:1px solid var(--cc-border); background:var(--cc-info-bg); margin:.65rem 0 1rem; }
.cc-result-icon { width:42px;height:42px;display:grid;place-items:center;flex:0 0 42px;border-radius:14px;background:var(--cc-green-soft);font-size:1.2rem; }
.cc-result-banner strong { display:block; font-size:1rem; color:var(--cc-text)!important; }
.cc-result-banner p { color:var(--cc-muted)!important; margin:.2rem 0 0; font-size:.85rem; }
.cc-recommendation { padding:1.2rem 1.25rem; margin:.8rem 0; border:1px solid var(--cc-border); border-left:5px solid var(--cc-primary);
  border-radius:18px; background:var(--cc-surface); }
.cc-recommendation .cc-rec-title { font-weight:850; color:var(--cc-green-deep)!important; margin-bottom:.4rem; }
.cc-recommendation p { color:var(--cc-text)!important; margin:0; }
.cc-stat { padding:1rem 1.1rem; border:1px solid var(--cc-border); border-radius:18px; background:var(--cc-surface); height:100%; }
.cc-stat span { display:block; color:var(--cc-muted)!important; font-size:.75rem; }
.cc-stat strong { display:block; color:var(--cc-text)!important; font-size:1.45rem; letter-spacing:-.04em; margin-top:.22rem; }
.cc-page-hero { display:flex; gap:1rem; align-items:center; margin:1.5rem 0 1.1rem; padding:1.35rem 1.5rem; border-radius:22px;
  background:linear-gradient(110deg,var(--cc-hero-a),var(--cc-surface)); border:1px solid var(--cc-border); }
.cc-page-icon { width:54px;height:54px;display:grid;place-items:center;flex:0 0 54px;background:var(--cc-surface);border:1px solid var(--cc-border);border-radius:17px;font-size:1.45rem; }
.cc-page-hero h1 { font-size:1.7rem; line-height:1.15; margin:.2rem 0; }
.cc-page-hero p { color:var(--cc-muted)!important; font-size:.88rem; margin:0; }
.cc-engine-showcase { margin: 1.4rem 0 1.8rem; padding: 1.15rem; border-radius: 24px; background: linear-gradient(135deg, rgba(255,255,255,.8), rgba(232,247,235,.95)); border: 1px solid var(--cc-border); box-shadow: 0 10px 22px var(--cc-shadow); }
.cc-engine-header { display:flex; align-items:center; justify-content:space-between; gap:1rem; margin-bottom: .8rem; }
.cc-engine-header .cc-eyebrow { margin:0; }
.cc-engine-header h3 { margin:0; font-size:1.18rem; color:var(--cc-text)!important; }
.cc-engine-grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:.8rem; }
.cc-engine-card { padding: 1rem .9rem; border-radius: 18px; border: 1px solid var(--cc-border); background: var(--cc-surface); min-height: 146px; position:relative; overflow:hidden; }
.cc-engine-card::after { content:""; position:absolute; width:110px; height:110px; right:-28px; bottom:-42px; border-radius:50%; background: rgba(93,159,105,.09); }
.cc-engine-card.warm { background: linear-gradient(160deg, #fffaf3 0%, #fff 100%); }
.cc-engine-card.green { background: linear-gradient(160deg, #f1fbf4 0%, #fff 100%); }
.cc-engine-card.orange { background: linear-gradient(160deg, #fff3eb 0%, #fff 100%); }
.cc-engine-card.slate { background: linear-gradient(160deg, #f4f7f3 0%, #fff 100%); }
.cc-engine-card .chip { display:inline-flex; align-items:center; justify-content:center; min-width: 38px; height: 32px; padding: 0 .5rem; border-radius: 10px; background: rgba(46,184,114,.12); color: var(--cc-green-deep)!important; font-weight:900; font-size:.74rem; margin-bottom:.55rem; }
.cc-engine-card h4 { margin:0 0 .4rem; font-size:.88rem; color:var(--cc-text)!important; }
.cc-engine-card p { margin:0; color:var(--cc-muted)!important; font-size:.76rem; line-height:1.55; position:relative; z-index:1; }
.cc-premium-shell { background: linear-gradient(180deg, rgba(255,255,255,0.76) 0%, rgba(255,255,255,0.56) 100%); border-radius: 32px; padding: 0.7rem 0.8rem 1.2rem; border: 1px solid rgba(79, 110, 82, 0.14); box-shadow: 0 18px 32px rgba(34, 71, 51, .08); }
.cc-hero-premium { display:grid; grid-template-columns: minmax(0,1.35fr) minmax(300px,.95fr); gap:1.2rem; align-items:stretch; padding: 1.15rem; background: linear-gradient(120deg, rgba(238,249,237,.9), rgba(255,248,233,.84)); border-radius: 28px; border: 1px solid var(--cc-border); overflow:hidden; position:relative; }
.cc-hero-premium::before { content:""; position:absolute; inset:auto auto -130px -80px; width:280px; height:280px; border-radius:50%; background: rgba(93,159,105,.08); }
.cc-hero-copy { position:relative; z-index:1; padding: 1rem .3rem .8rem .2rem; }
.cc-hero-copy .cc-eyebrow { display:inline-flex; align-items:center; gap:.5rem; padding:.48rem .8rem; border-radius:999px; background: rgba(255,255,255,.8); border: 1px solid rgba(90,127,96,.12); }
.cc-hero-copy h1 { font-size: clamp(2.3rem, 4vw, 4.2rem); line-height: .94; letter-spacing:-.065em; max-width: 530px; margin: 1rem 0 .85rem; color: #1f3d2e !important; }
.cc-hero-copy h1 em { color: var(--cc-green-deep)!important; font-style: normal; }
.cc-hero-copy p { max-width: 560px; color: var(--cc-muted)!important; font-size: 1.02rem; line-height: 1.8; }
.cc-hero-cta-row { display:flex; gap:.8rem; margin-top:1.2rem; align-items:center; flex-wrap:wrap; }
.cc-hero-button { display:inline-flex; align-items:center; gap:.55rem; padding:.82rem 1.15rem; border-radius:999px; background: linear-gradient(135deg, var(--cc-primary) 0%, #f29653 100%); color:#fff !important; text-decoration:none; font-weight:800; box-shadow: 0 10px 20px rgba(232,106,58,.25); }
.cc-hero-button.secondary { background: rgba(255,255,255,.75); color: var(--cc-green-deep)!important; border: 1px solid rgba(100,130,102,.18); box-shadow:none; }
.cc-hero-meta { display:flex; gap:.8rem; flex-wrap:wrap; margin-top:1rem; }
.cc-meta-pill { display:inline-flex; align-items:center; gap:.45rem; padding:.42rem .68rem; border:1px solid rgba(86,120,92,.16); background: rgba(255,255,255,.72); border-radius:999px; color: var(--cc-text)!important; font-size:.72rem; font-weight:700; }
.cc-hero-visual { position:relative; border-radius:24px; background: linear-gradient(180deg, rgba(127,190,128,.15), rgba(255,248,233,.8)); border: 1px solid rgba(92,125,90,.12); min-height: 340px; display:flex; justify-content:center; align-items:center; overflow:hidden; }
.cc-hero-visual::before { content:""; position:absolute; inset: 0; background: radial-gradient(ellipse at 50% 20%, rgba(255,250,214,.96), rgba(255,250,214,0) 42%); }
.cc-hero-visual svg { position:relative; z-index:1; width: min(100%, 480px); height: auto; }
.cc-spot-badge { position:absolute; z-index:2; background:rgba(255,255,255,.8); border:1px solid rgba(92,125,90,.14); border-radius:16px; padding:.6rem .8rem; box-shadow:0 8px 18px rgba(39,76,46,.08); color:var(--cc-text)!important; font-size:.72rem; font-weight:800; }
.cc-spot-badge.left { left:1rem; top:1rem; }
.cc-spot-badge.right { right:1rem; bottom:1rem; }
.cc-spot-badge span { display:block; color:var(--cc-muted)!important; font-size:.65rem; margin-top:.18rem; }
.cc-dashboard-shell { background: rgba(255,255,255,.74); border: 1px solid rgba(99,127,98,.12); border-radius: 26px; padding: 1rem; box-shadow: 0 18px 34px rgba(46,92,69,.06); }
.cc-dashboard-head { display:flex; align-items:center; justify-content:space-between; gap:1rem; margin-bottom:1rem; }
.cc-dashboard-head h3 { margin:0; font-size:1.2rem; color:var(--cc-text)!important; }
.cc-status { display:inline-flex; align-items:center; gap:.45rem; padding:.38rem .7rem; border-radius:999px; background: rgba(46,184,114,.1); color: var(--cc-green-deep)!important; font-size:.72rem; font-weight:800; }
.cc-dashboard-grid { display:grid; grid-template-columns: minmax(0,1.25fr) minmax(260px,.75fr); gap:1rem; }
.cc-form-card { background: linear-gradient(180deg, rgba(255,255,255,.96), rgba(244,249,240,.8)); border:1px solid var(--cc-border); border-radius:24px; padding: 1rem; }
.cc-side-panel { background: linear-gradient(180deg, rgba(245,251,246,.9), rgba(255,255,255,.95)); border:1px solid var(--cc-border); border-radius:24px; padding: 1rem; }
.cc-lite-list { display:flex; flex-direction:column; gap:.75rem; }
.cc-lite-item { display:flex; gap:.75rem; align-items:flex-start; border:1px solid rgba(99,127,98,.12); background: rgba(255,255,255,.75); border-radius:14px; padding:.7rem .75rem; }
.cc-lite-index { display:grid; place-items:center; width:28px; height:28px; border-radius:10px; background: rgba(46,184,114,.12); color: var(--cc-green-deep)!important; font-weight:900; font-size:.72rem; }
.cc-lite-item h4 { margin:0 0 .14rem; font-size:.82rem; color:var(--cc-text)!important; }
.cc-lite-item p { margin:0; color:var(--cc-muted)!important; font-size:.72rem; line-height:1.5; }
.cc-result-hero { padding: 1.3rem 1.35rem; border-radius: 28px; background: linear-gradient(135deg, rgba(222,247,228,.9), rgba(255,255,255,.98)); border:1px solid var(--cc-border); box-shadow: 0 16px 30px rgba(46,92,69,.08); }
.cc-diagnosis-panel { margin:1rem 0 1.1rem; padding:1.1rem 1.2rem; border:1px solid var(--cc-border); border-radius:22px; background:linear-gradient(145deg,#fff 0%,#f2f8ef 100%); box-shadow:0 12px 26px rgba(35,82,54,.08); }
.cc-diagnosis-heading { display:flex; align-items:flex-end; justify-content:space-between; gap:1rem; margin-bottom:.9rem; }
.cc-diagnosis-heading h3 { margin:0!important; font-size:1.05rem!important; color:var(--cc-text)!important; }
.cc-diagnosis-heading p { margin:.2rem 0 0!important; color:var(--cc-muted)!important; font-size:.75rem!important; }
.cc-diagnosis-row { display:grid; grid-template-columns:minmax(130px,1fr) minmax(120px,1.5fr) auto; gap:.85rem; align-items:center; padding:.78rem .85rem; border-top:1px solid rgba(91,117,97,.13); }
.cc-diagnosis-label { display:flex; align-items:center; gap:.55rem; min-width:0; }
.cc-diagnosis-rank { display:grid; place-items:center; width:28px; height:28px; flex:0 0 28px; border-radius:9px; background:var(--cc-green-soft); color:var(--cc-green-deep)!important; font-size:.7rem; font-weight:900; }
.cc-diagnosis-label strong { overflow:hidden; text-overflow:ellipsis; color:var(--cc-text)!important; font-size:.8rem; }
.cc-diagnosis-track { height:9px; overflow:hidden; border-radius:99px; background:#E3EDE0; }
.cc-diagnosis-track span { display:block; height:100%; min-width:2px; border-radius:inherit; background:linear-gradient(90deg,#397A52,#81B36F); }
.cc-diagnosis-value { min-width:104px; text-align:right; color:var(--cc-green-deep)!important; font-size:.72rem; font-weight:850; }
.cc-diagnosis-value small { display:block; color:var(--cc-muted)!important; font-size:.62rem; font-weight:600; margin-top:.12rem; }
.cc-result-banner { background:linear-gradient(120deg,#E4F1E2 0%,#F5F8ED 60%,#fff 100%); border-color:#C9DDC7; }
.cc-recommendation { border-left-color:var(--cc-green); background:linear-gradient(120deg,#F1F7EE,#fff 75%); }
.cc-result-top { display:flex; align-items:center; gap:1rem; }
.cc-result-icon { width:56px; height:56px; display:grid; place-items:center; border-radius:18px; background: linear-gradient(135deg, rgba(46,184,114,.14), rgba(255,255,255,.7)); font-size:1.5rem; }
.cc-result-top h3 { margin:0; font-size:1.45rem; color:var(--cc-text)!important; }
.cc-result-top p { margin:.3rem 0 0; color:var(--cc-muted)!important; font-size:.82rem; }
.cc-result-metrics { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap: .8rem; margin-top:1rem; }
.cc-metric-box { background: rgba(255,255,255,.7); border:1px solid var(--cc-border); border-radius:18px; padding: .9rem 1rem; }
.cc-metric-box .label { display:block; color: var(--cc-muted)!important; font-size:.7rem; text-transform:uppercase; letter-spacing:.08em; }
.cc-metric-box strong { display:block; margin-top:.32rem; font-size:1.35rem; letter-spacing:-.04em; color:var(--cc-text)!important; }
.cc-metric-box small { display:block; margin-top:.2rem; color: var(--cc-muted)!important; font-size:.72rem; }
.cc-confidence-ring { width: 90px; height: 90px; border-radius:50%; display:grid; place-items:center; background: conic-gradient(var(--cc-green) calc(var(--confidence) * 1%), rgba(255,255,255,.7) 0); position:relative; }
.cc-confidence-ring::before { content:""; position:absolute; inset: 12px; background: rgba(255,255,255,.94); border-radius:50%; }
.cc-confidence-ring strong { position:relative; z-index:1; color: var(--cc-text)!important; font-size:1.1rem; }
.cc-why-box { padding: 1rem 1.1rem; border-radius:18px; background: rgba(255,255,255,.75); border:1px solid var(--cc-border); }
.cc-why-box h4 { margin:0 0 .5rem; color:var(--cc-text)!important; font-size:.9rem; }
.cc-why-box ul { margin:0; padding-left:1.15rem; color:var(--cc-muted)!important; line-height:1.7; }
.cc-history-preview { min-height:76px; padding:.72rem .8rem; border:1px solid var(--cc-border); border-radius:14px; background:rgba(255,255,255,.82); }
.cc-history-preview span { display:block; color:var(--cc-muted)!important; font-size:.66rem; font-weight:800; text-transform:uppercase; }
.cc-history-preview strong { display:block; margin-top:.34rem; color:var(--cc-text)!important; font-size:.78rem; line-height:1.5; overflow-wrap:anywhere; }
@media (max-width: 720px) { .cc-diagnosis-row { grid-template-columns:minmax(0,1fr) auto; gap:.5rem; } .cc-diagnosis-track { grid-column:1 / -1; grid-row:2; } .cc-diagnosis-value { min-width:76px; } }
.cc-footer { text-align:center; color:var(--cc-muted)!important; font-size:.75rem; padding:2rem 0 .5rem; }
.cc-footer b { color:var(--cc-green-deep)!important; }

/* Navigation is a row of soft pills instead of the original left-side menu. */
[data-testid="stRadio"] div[role="radiogroup"][aria-orientation="horizontal"] { gap:.38rem; flex-wrap:wrap; }
[data-testid="stRadio"] div[role="radiogroup"][aria-orientation="horizontal"] > label {
  border:1px solid var(--cc-border)!important; border-radius:999px!important; padding:.55rem .95rem!important;
  background:var(--cc-surface)!important; transition:all .16s ease; margin:0!important; box-shadow:0 2px 7px var(--cc-shadow); }
[data-testid="stRadio"] div[role="radiogroup"][aria-orientation="horizontal"] > label:hover { background:var(--cc-select-hover)!important; }
[data-testid="stRadio"] div[role="radiogroup"][aria-orientation="horizontal"] > label:has(input:checked) {
  background:var(--cc-nav-active)!important; border-color:var(--cc-green)!important; }
[data-testid="stRadio"] [data-baseweb="radio"] > div {
    border-color:var(--cc-muted)!important; background-color:var(--cc-surface)!important; }
[data-testid="stRadio"] [data-baseweb="radio"] > div > div { background-color:var(--cc-primary)!important; }
[data-testid="stRadio"] label:has(input:checked) [data-baseweb="radio"] > div {
    border-color:var(--cc-primary)!important; background-color:var(--cc-primary)!important; }
input[type="radio"], input[type="checkbox"] { accent-color:var(--cc-primary)!important; color-scheme:__SCHEME__!important; }

/* Full theme coverage for Streamlit + BaseWeb inputs, menus, popovers and form buttons. */
input, textarea, select, [data-baseweb="input"] > div, [data-baseweb="textarea"] > div,
[data-baseweb="select"] > div, [data-testid="stTextInputRootElement"], [data-testid="stTextAreaRootElement"] {
  background:var(--cc-input)!important; color:var(--cc-input-text)!important; border-color:var(--cc-input-border)!important;
  border-radius:13px!important; color-scheme:__SCHEME__!important; box-shadow:none!important;
}
[data-testid="stTextInput"] [data-baseweb="input"], [data-testid="stTextInput"] [data-baseweb="input"] > div,
[data-testid="stNumberInput"] [data-baseweb="input"], [data-testid="stNumberInput"] [data-baseweb="input"] > div,
[data-testid="stTextArea"] [data-baseweb="textarea"], [data-testid="stTextArea"] [data-baseweb="textarea"] > div,
[data-testid="stTextInputRootElement"], [data-testid="stTextAreaRootElement"],
[data-testid="stSelectbox"] [data-baseweb="select"], [data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stMultiSelect"] [data-baseweb="select"], [data-testid="stMultiSelect"] [data-baseweb="select"] > div {
  background:var(--cc-input)!important; color:var(--cc-input-text)!important; border-color:var(--cc-input-border)!important;
  border-radius:13px!important; box-shadow:none!important;
}
[data-testid="stTextInput"] input, [data-testid="stNumberInput"] input, [data-testid="stTextArea"] textarea,
[data-baseweb="input"] input, [data-baseweb="textarea"] textarea, [data-baseweb="select"] input {
  background:transparent!important; color:var(--cc-input-text)!important; -webkit-text-fill-color:var(--cc-input-text)!important;
  caret-color:var(--cc-primary)!important; }
input::placeholder, textarea::placeholder { color:var(--cc-muted)!important; -webkit-text-fill-color:var(--cc-muted)!important; opacity:1!important; }
[data-baseweb="select"] [role="combobox"], [data-baseweb="select"] [role="button"] { background:transparent!important; color:var(--cc-input-text)!important; }
[data-baseweb="select"] svg, [data-baseweb="input"] svg, [data-baseweb="textarea"] svg { fill:var(--cc-muted)!important; color:var(--cc-muted)!important; }
[data-testid="stPopover"], [data-baseweb="popover"], [data-baseweb="menu"], [data-baseweb="select"] ul,
[role="listbox"], [role="option"], [data-baseweb="calendar"] { background:var(--cc-surface)!important; color:var(--cc-text)!important; }
[role="option"] * { color:var(--cc-text)!important; }
[role="option"]:hover, [role="option"][aria-selected="true"] { background:var(--cc-select-hover)!important; }
[data-testid="stMultiSelect"] [data-baseweb="tag"] { background:var(--cc-green-soft)!important; border:1px solid var(--cc-border)!important; border-radius:999px!important; }
[data-testid="stMultiSelect"] [data-baseweb="tag"] span { color:var(--cc-input-text)!important; }
[data-testid="stSlider"] [data-baseweb="slider"] div { color:var(--cc-text)!important; }
[data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] { background:var(--cc-primary)!important; border-color:var(--cc-primary)!important; }
[data-testid="stButton"] button, [data-testid="stFormSubmitButton"] button, [data-testid="stDownloadButton"] button {
  border-radius:999px!important; border:1px solid var(--cc-border)!important; font-weight:780!important;
  background:linear-gradient(135deg,#FFFFFF 0%,#F3FBEF 100%)!important; color:var(--cc-green-deep)!important; min-height:2.8rem;
  transition:transform .15s ease, box-shadow .15s ease, background .15s ease; }
[data-testid="stButton"] button:hover, [data-testid="stDownloadButton"] button:hover { transform:translateY(-2px); box-shadow:0 8px 18px var(--cc-shadow); }
[data-testid="stFormSubmitButton"] button[kind="primary"], [data-testid="stButton"] button[kind="primary"] {
  background:linear-gradient(135deg,#FF7E5F 0%,#FF5E5B 52%,#F98D36 100%)!important; color:#FFFFFF!important; border-color:transparent!important; box-shadow:0 10px 22px rgba(255,106,61,.28)!important; }
[data-testid="stFormSubmitButton"] button[kind="primary"]:hover, [data-testid="stButton"] button[kind="primary"]:hover { background:linear-gradient(135deg,#FF7150 0%,#F5544B 50%,#EE7E2A 100%)!important; }
[data-testid="stFormSubmitButton"] button:disabled { opacity:.5; }
[data-testid="stExpander"] { border:1px solid var(--cc-border)!important; border-radius:16px!important; background:var(--cc-surface)!important; }
[data-testid="stExpander"] summary { color:var(--cc-text)!important; }
[data-testid="stDataFrame"], [data-testid="stTable"] { border:1px solid var(--cc-border)!important; border-radius:14px!important; overflow:hidden; }
[data-testid="stMetric"] { background:var(--cc-surface)!important; border:1px solid var(--cc-border)!important; padding:.9rem 1rem!important; border-radius:17px!important; }
[data-testid="stMetricLabel"], [data-testid="stMetricValue"], [data-testid="stMetricDelta"] { color:var(--cc-text)!important; }
[data-testid="stMarkdownContainer"] code { color:var(--cc-green-deep)!important; background:var(--cc-green-soft)!important; padding:.12rem .35rem; border-radius:5px; }

@media (max-width: 850px) {
  [data-testid="stMainBlockContainer"] { padding: .8rem 1rem 2rem; }
  .cc-hero { grid-template-columns:1fr; padding:1.5rem; }
  .cc-hero-art { min-height:160px; }
  .cc-art-plate { min-height:155px; max-width:210px; }
  .cc-hero h1 { font-size:2.15rem; }
  .cc-caption-extra { display:none; }
}

/* ───────── Botanical Studio / richer editorial layout ───────── */
.stApp {
    background-color:var(--cc-page)!important;
    background-image:
        repeating-linear-gradient(118deg, transparent 0 64px, rgba(42,103,55,.085) 65px 66px, transparent 67px 116px),
        repeating-linear-gradient(62deg, transparent 0 82px, rgba(160,184,91,.12) 83px 84px, transparent 85px 148px),
        linear-gradient(135deg,#d6e9ce 0%,#c5dfbf 48%,#e0ebc2 100%)!important;
}
[data-testid="stMainBlockContainer"] { max-width: 1490px; padding-top: 1.1rem; padding-bottom: 3.2rem; }
[data-testid="stHeader"] { height: .5rem; }
[data-testid="stMainBlockContainer"] > div:first-child {
    background-color: rgba(229,242,222,.84);
    background-image:
        repeating-linear-gradient(122deg, transparent 0 104px, rgba(55,119,67,.055) 105px 106px, transparent 107px 176px),
        repeating-linear-gradient(58deg, transparent 0 132px, rgba(162,183,93,.075) 133px 134px, transparent 135px 216px);
    border: 1px solid rgba(65, 118, 69, 0.28);
  border-radius: 30px;
  padding: 0.55rem 0.9rem 1rem;
  box-shadow: 0 14px 28px rgba(38, 79, 52, .08);
}
.cc-brand-icon { border-radius: 18px 18px 18px 7px; background: linear-gradient(145deg, #E6F8EA, #FFF4D8 100%); transform: rotate(-2deg); }
.cc-brand-name { font-size: 1.5rem; }
.cc-header-caption { font-size: .68rem; }
.cc-live-dot { box-shadow: 0 0 0 5px color-mix(in srgb, var(--cc-green) 14%, transparent); }
.cc-rule { height: 1px; background: linear-gradient(90deg, transparent, var(--cc-border) 10%, var(--cc-border) 90%, transparent); margin: .5rem 0 1.2rem; }
.cc-hero { min-height: 360px; grid-template-columns: minmax(0,1.15fr) minmax(340px,.85fr); gap: 1.5rem; padding: 2.35rem 2.6rem; border-radius: 34px; background: linear-gradient(115deg,var(--cc-hero-a) 0%,var(--cc-hero-b) 57%,var(--cc-surface) 100%); box-shadow: 0 19px 42px var(--cc-shadow); }
.cc-hero:before { content:""; position:absolute; left:-75px; bottom:-150px; width:280px; height:280px; border:1px solid color-mix(in srgb, var(--cc-green) 28%, transparent); border-radius:48% 52% 47% 53%; transform:rotate(35deg); pointer-events:none; }
.cc-hero:after { content:""; position:absolute; width:350px; height:350px; right:0; top:-46%; border-radius:50%; background:radial-gradient(circle, color-mix(in srgb, var(--cc-green) 12%, transparent), transparent 66%); opacity:1; pointer-events:none; }
.cc-hero > div:first-child { position:relative; z-index:2; }
.cc-hero h1 { max-width:720px; font-size:clamp(2.35rem,3.7vw,3.7rem); line-height:1.03; margin:.8rem 0 1rem; }
.cc-hero h1 em { color:var(--cc-primary)!important; }
.cc-hero p { font-size:1.02rem; max-width:630px; line-height:1.75; }
.cc-hero .cc-eyebrow { display:inline-flex; align-items:center; gap:.5rem; padding:.42rem .72rem; border-radius:999px; background:var(--cc-surface); border:1px solid var(--cc-border); }
.cc-hero-pills { margin-top:1.35rem; }
.cc-pill { padding:.52rem .85rem; font-size:.76rem; box-shadow:0 3px 9px var(--cc-shadow); }
.cc-hero-art { min-height:285px; }
.cc-art-plate { width:100%; max-width:440px; min-height:300px; border-radius:36px; background:radial-gradient(ellipse at 50% 53%, var(--cc-surface) 0, color-mix(in srgb, var(--cc-green-soft) 82%, transparent) 52%, transparent 74%); overflow:visible; }
.cc-art-plate svg { width:min(100%,420px); max-height:350px; }
.cc-art-label { right:-.2rem; bottom:.05rem; border-radius:17px; border-left:4px solid var(--cc-primary); }
.cc-floating-tag { position:absolute; z-index:3; padding:.65rem .85rem; border:1px solid var(--cc-border); border-radius:16px; background:var(--cc-surface); box-shadow:0 8px 25px var(--cc-shadow); color:var(--cc-text)!important; font-size:.77rem; font-weight:800; }
.cc-floating-tag span { display:block; color:var(--cc-muted)!important; font-weight:500; font-size:.66rem; margin-top:.14rem; }
.cc-floating-tag.tag-left { left:-.35rem; top:1rem; }
.cc-floating-tag.tag-right { right:-.25rem; top:2rem; }
.cc-hero-cta { display:inline-flex; align-items:center; gap:.5rem; margin-top:1.25rem; padding:.78rem 1.15rem; border-radius:999px; background:var(--cc-primary); color:white!important; font-size:.82rem; font-weight:850; text-decoration:none!important; box-shadow:0 7px 17px color-mix(in srgb, var(--cc-primary) 25%, transparent); transition:transform .16s ease; }
.cc-hero-cta:hover { transform:translateY(-2px); background:var(--cc-primary-hover); }
.cc-alert { border-radius:20px; padding:1rem 1.2rem; box-shadow:0 5px 16px var(--cc-shadow); }
.cc-stat { position:relative; overflow:hidden; min-height:112px; padding:1.15rem 1.2rem; border-radius:21px; background:linear-gradient(140deg,var(--cc-surface),var(--cc-surface-alt)); }
.cc-stat:after { content:""; position:absolute; width:85px;height:85px; right:-30px;bottom:-35px;border-radius:50%;border:13px solid color-mix(in srgb,var(--cc-green) 12%,transparent); }
.cc-stat strong { font-size:1.65rem; position:relative; z-index:1; }
.cc-stat span { position:relative; z-index:1; }
.cc-section { margin-top:2.05rem; }
.cc-section .cc-eyebrow { display:block; margin-bottom:.35rem; }
.cc-section h2 { font-size:1.75rem; }
.cc-mini-card { min-height:150px; border-radius:22px; box-shadow:0 5px 18px var(--cc-shadow); transition:transform .18s ease, box-shadow .18s ease; position:relative; overflow:hidden; }
.cc-mini-card:hover { transform:translateY(-3px); box-shadow:0 12px 25px var(--cc-shadow); }
.cc-mini-card .mini-icon { width:46px;height:46px;border-radius:16px;font-size:1.25rem; box-shadow:inset 0 0 0 1px var(--cc-border); }
.cc-page-hero { margin-top:1.6rem; padding:1.55rem 1.7rem; border-radius:25px; box-shadow:0 8px 24px var(--cc-shadow); }
.cc-page-icon { border-radius:18px 18px 18px 7px; font-size:1.65rem; width:62px;height:62px; flex-basis:62px; }
.cc-nutrient-section { margin:2rem 0 1.2rem; }
.cc-nutrient-grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:1rem; margin-top:.9rem; }
.cc-nutrient-card { position:relative; min-height:154px; overflow:hidden; padding:1.15rem 1.2rem; border:1px solid var(--cc-border); border-radius:23px; background:var(--cc-surface); box-shadow:0 6px 18px var(--cc-shadow); }
.cc-nutrient-card:after { content:""; position:absolute; width:130px;height:130px;right:-40px;bottom:-65px;border-radius:50%; background:var(--accent-soft); opacity:.9; }
.cc-nutrient-top { position:relative; z-index:1; display:flex; align-items:center; gap:.75rem; }
.cc-nutrient-badge { display:grid; place-items:center; width:48px;height:48px; flex:0 0 48px; border-radius:17px; background:var(--accent-soft); color:var(--accent-ink)!important; font-size:1.05rem; font-weight:950; box-shadow:inset 0 0 0 1px color-mix(in srgb,var(--accent-ink) 13%,transparent); }
.cc-nutrient-name { color:var(--cc-text)!important; font-size:.98rem; font-weight:900; letter-spacing:-.02em; }
.cc-nutrient-kind { display:block; color:var(--cc-muted)!important; font-size:.72rem; margin-top:.1rem; }
.cc-nutrient-card p { position:relative;z-index:1; color:var(--cc-muted)!important; font-size:.79rem; line-height:1.55; margin:.9rem 0 0; max-width:91%; }
.cc-nutrient-tag { position:relative;z-index:1;display:inline-flex;margin-top:.6rem;padding:.26rem .52rem;border-radius:999px;background:var(--cc-surface-alt);color:var(--cc-text)!important;font-size:.65rem;font-weight:800; }
.cc-consult-head { display:flex; gap:.9rem; align-items:center; margin-bottom:.8rem; }
.cc-consult-head-icon { width:48px;height:48px;display:grid;place-items:center;border-radius:17px;background:var(--cc-green-soft);font-size:1.4rem; }
.cc-consult-head h3 { margin:0!important; font-size:1.12rem!important; }
.cc-consult-head p { margin:.12rem 0 0!important; color:var(--cc-muted)!important; font-size:.78rem!important; }
.cc-step-card { display:flex; align-items:flex-start; gap:.75rem; padding:.85rem 0; border-bottom:1px dashed var(--cc-border); }
.cc-step-card:last-child { border-bottom:0; }
.cc-step-number { width:32px;height:32px;display:grid;place-items:center;flex:0 0 32px;border-radius:12px;background:var(--cc-green-soft);color:var(--cc-green-deep)!important;font-weight:900;font-size:.8rem; }
.cc-step-card strong { display:block;font-size:.82rem;color:var(--cc-text)!important; }
.cc-step-card small { display:block;color:var(--cc-muted)!important;line-height:1.5;margin-top:.14rem;font-size:.73rem; }
.cc-rule-grid { display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.85rem;margin:.8rem 0 1rem; }
.cc-rule-card { padding:1rem 1.05rem;border:1px solid var(--cc-border);border-radius:19px;background:var(--cc-surface);box-shadow:0 4px 13px var(--cc-shadow); }
.cc-rule-top { display:flex;align-items:center;justify-content:space-between;gap:.5rem;margin-bottom:.7rem; }
.cc-rule-id { background:var(--cc-green-soft);color:var(--cc-green-deep)!important;padding:.3rem .55rem;border-radius:9px;font-size:.68rem;font-weight:900; }
.cc-rule-cf { color:var(--cc-primary)!important;font-size:.75rem;font-weight:900; }
.cc-rule-nutrient { font-size:1rem;font-weight:900;color:var(--cc-text)!important;margin-bottom:.35rem; }
.cc-rule-if { color:var(--cc-muted)!important;font-size:.77rem;line-height:1.55; }
.cc-rule-bar { height:6px;background:var(--cc-surface-alt);border-radius:99px;margin-top:.75rem;overflow:hidden; }
.cc-rule-bar span { display:block;height:100%;background:linear-gradient(90deg,var(--cc-green),var(--cc-primary));border-radius:99px; }
.cc-result-banner { padding:1.3rem 1.35rem; border-radius:23px; box-shadow:0 6px 18px var(--cc-shadow); }
.cc-result-icon { width:50px;height:50px;border-radius:17px;font-size:1.35rem; }
.cc-recommendation { border-left-width:6px; border-radius:20px; box-shadow:0 5px 14px var(--cc-shadow); }
.cc-footer { border-top:1px solid var(--cc-border); margin-top:2.5rem; }
[data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stMultiSelect"] [data-baseweb="select"] > div,
[data-testid="stTextInput"] [data-baseweb="input"] > div,
[data-testid="stTextArea"] [data-baseweb="textarea"] > div,
[data-testid="stNumberInput"] [data-baseweb="input"] > div { min-height:2.8rem; border:1px solid var(--cc-input-border)!important; }
[data-testid="stSelectbox"] [data-baseweb="select"] > div:focus-within,
[data-testid="stMultiSelect"] [data-baseweb="select"] > div:focus-within,
[data-testid="stTextInput"] [data-baseweb="input"] > div:focus-within,
[data-testid="stTextArea"] [data-baseweb="textarea"] > div:focus-within { border-color:var(--cc-green)!important; box-shadow:0 0 0 3px color-mix(in srgb,var(--cc-green) 17%,transparent)!important; }
[data-testid="stRadio"] label > div:first-child { color:var(--cc-primary)!important; }
[data-testid="stRadio"] input { accent-color:var(--cc-primary)!important; }
@media (max-width: 1050px) { .cc-hero { grid-template-columns:1fr .8fr; padding:1.7rem; } .cc-hero-art { min-height:230px; } .cc-nutrient-grid { grid-template-columns:repeat(2,minmax(0,1fr)); } }
@media (max-width: 720px) { .cc-hero { grid-template-columns:1fr; padding:1.3rem; } .cc-hero-art { min-height:210px; } .cc-hero h1 { font-size:2.1rem; } .cc-nutrient-grid, .cc-rule-grid { grid-template-columns:1fr; } .cc-art-label { right:.1rem; } [data-testid="stMainBlockContainer"] { padding:.6rem .8rem 2rem; } }


/* FINAL LIGHT-ONLY OVERRIDES
   Streamlit/BaseWeb can keep dark-mode backgrounds on inner widget layers.
   These rules force each interactive control to use the same warm light palette. */
html, body, .stApp, .stApp > div, [data-testid="stAppViewContainer"],
[data-testid="stMain"], [data-testid="stMainBlockContainer"],
[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stBottom"],
[data-testid="stSidebar"], [data-testid="stSidebar"] > div,
[data-testid="stSidebarContent"], [data-testid="stForm"],
[data-testid="stVerticalBlockBorderWrapper"] {
  color-scheme: light !important;
}

/* Text, number, and long-text inputs: paint both the BaseWeb wrapper and its inner field. */
[data-testid="stTextInput"] [data-baseweb="input"],
[data-testid="stTextInput"] [data-baseweb="input"] > div,
[data-testid="stNumberInput"] [data-baseweb="input"],
[data-testid="stNumberInput"] [data-baseweb="input"] > div,
[data-testid="stTextArea"] [data-baseweb="textarea"],
[data-testid="stTextArea"] [data-baseweb="textarea"] > div,
[data-testid="stTextInputRootElement"], [data-testid="stTextAreaRootElement"],
[data-testid="stNumberInputContainer"] {
    background: #F3F8EF !important;
    background-color: #F3F8EF !important;
  color: #263C2A !important;
  border-color: #CEDBC3 !important;
  box-shadow: none !important;
}
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea,
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea {
  background: transparent !important;
  background-color: transparent !important;
  color: #263C2A !important;
  -webkit-text-fill-color: #263C2A !important;
    caret-color: var(--cc-green) !important;
  color-scheme: light !important;
}
[data-testid="stTextInput"] input::placeholder,
[data-testid="stNumberInput"] input::placeholder,
[data-testid="stTextArea"] textarea::placeholder,
[data-baseweb="input"] input::placeholder,
[data-baseweb="textarea"] textarea::placeholder {
  color: #71806A !important;
  -webkit-text-fill-color: #71806A !important;
  opacity: 1 !important;
}

/* Selectbox and multiselect controls. */
[data-testid="stSelectbox"] [data-baseweb="select"],
[data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stSelectbox"] [data-baseweb="select"] > div > div,
[data-testid="stSelectbox"] [data-baseweb="select"] [role="combobox"],
[data-testid="stMultiSelect"] [data-baseweb="select"],
[data-testid="stMultiSelect"] [data-baseweb="select"] > div,
[data-testid="stMultiSelect"] [data-baseweb="select"] > div > div,
[data-testid="stMultiSelect"] [data-baseweb="select"] [role="combobox"] {
    background: #F3F8EF !important;
    background-color: #F3F8EF !important;
  color: #263C2A !important;
  border-color: #CEDBC3 !important;
  box-shadow: none !important;
  color-scheme: light !important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] *,
[data-testid="stMultiSelect"] [data-baseweb="select"] * {
  color: #263C2A !important;
  -webkit-text-fill-color: #263C2A !important;
}
[data-testid="stMultiSelect"] [data-baseweb="tag"],
[data-testid="stMultiSelect"] [data-baseweb="tag"] > span {
  background: #E1EACF !important;
  background-color: #E1EACF !important;
  color: #2F5834 !important;
  -webkit-text-fill-color: #2F5834 !important;
  border-color: #CEDBC3 !important;
}
[data-baseweb="select"] svg, [data-baseweb="input"] svg,
[data-baseweb="textarea"] svg, [data-baseweb="spinner"] svg {
  color: #6B7D68 !important;
  fill: #6B7D68 !important;
}

/* Dropdown portals are rendered outside the widget DOM in some Streamlit versions. */
[data-baseweb="popover"], [data-baseweb="menu"], [data-testid="stPopover"],
[data-testid="stSelectboxVirtualDropdown"], [role="listbox"], [role="listbox"] ul,
[role="option"], [data-baseweb="popover"] > div {
    background: #F2F7ED !important;
    background-color: #F2F7ED !important;
  color: #263C2A !important;
  color-scheme: light !important;
  border-color: #D8E2CD !important;
}
[role="option"] *, [role="listbox"] *, [data-baseweb="menu"] * {
  color: #263C2A !important;
  -webkit-text-fill-color: #263C2A !important;
}
[role="option"]:hover, [role="option"][aria-selected="true"],
[role="option"][aria-selected="true"] *, [role="option"]:hover * {
    background-color: #DDEFD7 !important;
  color: #2F5834 !important;
  -webkit-text-fill-color: #2F5834 !important;
}

/* Number-input stepper buttons and ordinary controls. */
[data-testid="stNumberInput"] button,
[data-testid="stButton"] button,
[data-testid="stDownloadButton"] button,
[data-testid="stFormSubmitButton"] button,
[data-testid="stBaseButton-secondary"],
button[kind="secondary"] {
    background: #F1F7EC !important;
    background-color: #F1F7EC !important;
  color: #2F5834 !important;
  border: 1px solid #D8E2CD !important;
  box-shadow: none !important;
}
[data-testid="stNumberInput"] button svg,
[data-testid="stNumberInput"] button span {
  color: #2F5834 !important;
  fill: #2F5834 !important;
}
[data-testid="stFormSubmitButton"] button[kind="primary"],
[data-testid="stButton"] button[kind="primary"],
[data-testid="stBaseButton-primary"], button[kind="primary"] {
    background: var(--cc-primary) !important;
    background-color: var(--cc-primary) !important;
  color: #FFFFFF !important;
  -webkit-text-fill-color: #FFFFFF !important;
    border-color: var(--cc-primary) !important;
}
[data-testid="stFormSubmitButton"] button[kind="primary"] *,
[data-testid="stButton"] button[kind="primary"] *,
[data-testid="stBaseButton-primary"] * {
  color: #FFFFFF !important;
  -webkit-text-fill-color: #FFFFFF !important;
}

/* Radio/checkbox markers: avoid black dots against the cream UI. */
[data-testid="stRadio"] [data-baseweb="radio"] > div:first-child,
[data-testid="stRadio"] label > div:first-child,
[data-testid="stCheckbox"] [data-baseweb="checkbox"] > div:first-child {
    border-color: #A7B59A !important;
    background-color: #FFFEF9 !important;
    color: var(--cc-green) !important;
  color-scheme: light !important;
}
[data-testid="stRadio"] label:has(input:checked) [data-baseweb="radio"] > div:first-child {
    border-color: var(--cc-green) !important;
    background-color: var(--cc-green) !important;
}
[data-testid="stRadio"] [data-baseweb="radio"] > div > div {
    background-color: var(--cc-green) !important;
}
[data-testid="stRadio"] label:has(input:checked) [data-baseweb="radio"] > div {
    border-color: var(--cc-green) !important;
    background-color: var(--cc-green) !important;
}
[data-testid="stRadio"] input, [data-testid="stCheckbox"] input {
    accent-color: var(--cc-green) !important;
  color-scheme: light !important;
}

/* Native details/expander, alerts, dataframe borders and metric shells. */
[data-testid="stExpander"], [data-testid="stExpander"] details,
[data-testid="stExpander"] summary, [data-testid="stAlert"],
[data-testid="stMetric"], [data-testid="stVerticalBlockBorderWrapper"] {
  color: #263C2A !important;
  border-color: #D8E2CD !important;
}
[data-testid="stExpander"], [data-testid="stExpander"] details,
[data-testid="stMetric"] {
    background: #F3F8EF !important;
    background-color: #F3F8EF !important;
}
[data-testid="stDataFrame"], [data-testid="stTable"] {
    background: #F3F8EF !important;
  border-color: #D8E2CD !important;
  color-scheme: light !important;
}

/* Keep text and icons in every Streamlit widget readable even when user browser prefers dark. */
[data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] *,
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] *,
[data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li,
[data-testid="stRadio"] label, [data-testid="stCheckbox"] label,
[data-testid="stSlider"] label {
  color: #263C2A !important;
}
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] * {
  color: #6B7D68 !important;
}

</style>
"""

replacements = {
    "SCHEME": theme["scheme"], "PAGE": theme["page"], "SIDEBAR": theme["sidebar"],
    "SURFACE": theme["surface"], "SURFACE_ALT": theme["surface_alt"], "WIDGET": theme["widget"],
    "TEXT": theme["text"], "MUTED": theme["muted"], "BORDER": theme["border"],
    "PRIMARY": theme["primary"], "PRIMARY_HOVER": theme["primary_hover"], "GREEN": theme["green"],
    "GREEN_DEEP": theme["green_deep"], "GREEN_SOFT": theme["green_soft"],
    "INFO_BG": theme["info_bg"], "INFO_TEXT": theme["info_text"], "TABLE_HEAD": theme["table_head"],
    "SHADOW": theme["shadow"], "INPUT": theme["input"], "INPUT_TEXT": theme["input_text"],
    "INPUT_BORDER": theme["input_border"], "NAV_ACTIVE": theme["nav_active"],
    "NAV_ACTIVE_TEXT": theme["nav_active_text"], "HERO_A": theme["hero_a"], "HERO_B": theme["hero_b"],
    "SELECT_HOVER": theme["select_hover"],
}
css = CSS_TEMPLATE
for token, value in replacements.items():
    css = css.replace(f"__{token}__", value)
st.markdown(css, unsafe_allow_html=True)
st.markdown('<div class="cc-rule"></div>', unsafe_allow_html=True)

# ─── Navigation ────────────────────────────────────────────────────────────
nav_col, nav_spacer, nav_hint = st.columns([3.4, 1.6, 2.0], vertical_alignment="center")
with nav_col:
    page = st.radio(
        "Navigasi utama",
        ["Konsultasi", "Basis Pengetahuan", "Riwayat", "Tentang"],
        horizontal=True,
        key="cc_main_navigation",
        label_visibility="collapsed",
        format_func=lambda value: {
            "Konsultasi": "Cek tanaman", "Basis Pengetahuan": "Panduan gejala",
            "Riwayat": "Riwayat", "Tentang": "Tentang CabaiCare",
        }[value],
    )
with nav_hint:
    st.markdown('<div style="text-align:right;color:var(--cc-muted);font-size:.76rem;padding:.4rem 0">● Sistem siap digunakan</div>', unsafe_allow_html=True)

# ─── Small rendering helpers ────────────────────────────────────────────────
def section_heading(kicker: str, title: str, desc: str = "") -> None:
    st.markdown(
        f'<div class="cc-section"><div class="cc-eyebrow">{html.escape(kicker)}</div><h2>{html.escape(title)}</h2>'
        + (f'<p>{html.escape(desc)}</p>' if desc else "") + '</div>',
        unsafe_allow_html=True,
    )


def page_heading(icon: str, kicker: str, title: str, desc: str) -> None:
    st.markdown(
        f'<div class="cc-page-hero"><div class="cc-page-icon">{icon}</div><div><div class="cc-eyebrow">{html.escape(kicker)}</div>'
        f'<h1>{html.escape(title)}</h1><p>{html.escape(desc)}</p></div></div>',
        unsafe_allow_html=True,
    )


def stat_card(label: str, value: str, note: str = "") -> None:
    st.markdown(
        f'<div class="cc-stat"><span>{html.escape(label)}</span><strong>{html.escape(value)}</strong>'
        + (f'<span style="margin-top:.25rem">{html.escape(note)}</span>' if note else '') + '</div>',
        unsafe_allow_html=True,
    )


def display_result(result: dict, selected_symptoms: list[str]) -> None:
    section_heading("HASIL PENGECEKAN", "Apa yang mungkin terjadi?", "Berikut kemungkinan yang paling sesuai dengan tanda yang kamu pilih.")
    top = result["diagnoses"][0] if result["diagnoses"] else None
    if top:
        st.markdown(
            f'<div class="cc-result-banner"><div class="cc-result-icon">🌿</div><div><strong>{html.escape(top["nutrient"])} — kemungkinan yang paling sesuai</strong>'
            f'<p>Tanda yang kamu pilih paling sesuai dengan kemungkinan ini.</p></div></div>',
            unsafe_allow_html=True,
        )
        m1, m2, m3 = st.columns(3)
        with m1:
            stat_card("Dugaan utama", top["nutrient"])
        with m2:
            confidence_pct = max(0, min(100, float(top["confidence"]) * 100))
            st.markdown(
                f'<div class="cc-stat"><span>Kecocokan tanda</span><div class="cc-confidence-wrap"><div class="cc-confidence-ring" style="--confidence:{confidence_pct:.1f}"><strong>{confidence_pct:.0f}%</strong></div><div class="cc-confidence-meta"><b>{confidence_pct:.1f}%</b><span>Skor dari tanda yang dipilih</span></div></div></div>',
                unsafe_allow_html=True,
            )
        with m3:
            stat_card("Panduan yang cocok", str(len(result["matched_rules"])), "Mendukung dugaan utama")
        diagnosis_rows = []
        for rank, diagnosis in enumerate(result["diagnoses"], start=1):
            diagnosis_pct = max(0, min(100, float(diagnosis["confidence"]) * 100))
            matched_count = len(diagnosis.get("matched_rules", []))
            diagnosis_rows.append(
                f'<div class="cc-diagnosis-row"><div class="cc-diagnosis-label">'
                f'<span class="cc-diagnosis-rank">{rank:02d}</span>'
                f'<strong>{html.escape(diagnosis["nutrient"])}</strong></div>'
                f'<div class="cc-diagnosis-track" role="img" aria-label="Kecocokan tanda {diagnosis_pct:.1f}%">'
                f'<span style="width:{diagnosis_pct:.1f}%"></span></div>'
                f'<div class="cc-diagnosis-value">{diagnosis_pct:.1f}%'
                f'<small>{matched_count} tanda pendukung</small></div></div>'
            )
        st.markdown(
            '<div class="cc-diagnosis-panel"><div class="cc-diagnosis-heading"><div>'
            '<h3>Perbandingan kemungkinan</h3>'
            '<p>Skor menunjukkan seberapa cocok tanda yang dipilih dengan tiap kemungkinan.</p>'
            '</div><span class="cc-status">🧠 Sudah dibandingkan</span></div>'
            + "".join(diagnosis_rows) + '</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="cc-result-banner"><div class="cc-result-icon">🔎</div><div><strong>Belum ada kemungkinan yang cukup sesuai</strong>'
            '<p>Coba periksa kembali tanda yang dipilih dan kondisi tanaman lainnya.</p></div></div>',
            unsafe_allow_html=True,
        )
    st.markdown(
        f'<div class="cc-recommendation"><div class="cc-rec-title">🌱 Saran awal</div><p>{html.escape(result["recommendation"])}</p></div>',
        unsafe_allow_html=True,
    )
    st.caption("Skor ini hanya menunjukkan kecocokan dengan panduan di aplikasi, bukan kepastian penyebab atau peluang akurasi. Periksa juga kondisi tanaman dan tanah.")

    with st.expander("💬 Kenapa saya diminta memilih tanda ini?", expanded=False):
        if selected_symptoms:
            for symptom in selected_symptoms:
                item = kb["symptoms"].get(symptom, {})
                st.markdown(f'**{html.escape(item.get("label", symptom))}**')
                st.write(item.get("why", "Tanda ini membantu aplikasi membandingkan beberapa kemungkinan."))
        else:
            st.write("Tidak ada gejala yang dipilih. Sistem tidak akan memaksakan kesimpulan.")
    with st.expander("🧠 Bagaimana hasil ini dibuat?", expanded=False):
        st.write("CabaiCare membandingkan tanda yang kamu pilih dengan pola yang tercatat, lalu mengurutkan kemungkinan yang paling sesuai.")
        if result["matched_rules"]:
            rule_table = pd.DataFrame([
                {
                    "Kode catatan": rule["id"],
                    "Tanda yang sesuai": " dan ".join(kb["symptoms"].get(symptom, {}).get("label", symptom) for symptom in rule["if"]),
                    "Kemungkinan": rule["nutrient"],
                }
                for rule in result["matched_rules"]
            ])
            st.dataframe(rule_table, use_container_width=True, hide_index=True)
            with st.expander("Lihat rincian perhitungan", expanded=False):
                st.caption("Bagian ini memuat istilah teknis untuk pengguna yang ingin memeriksa cara kerja sistem.")
                for line in result["trace"]:
                    st.markdown(f"- {line}")
        else:
            st.info("Belum ada tanda yang cukup sesuai. Coba periksa kembali pilihanmu.")
    with st.expander("🔍 Kemungkinan lainnya", expanded=False):
        if result["diagnoses"]:
            for item in result["diagnoses"]:
                st.markdown(f'**{html.escape(item["nutrient"])} · {item["confidence"] * 100:.1f}%**')
                st.write(item["recommendation"])
        else:
                st.write("Belum ada kemungkinan lain yang cukup sesuai dengan tanda yang dipilih.")

    report = [
        "HASIL PENGECEKAN TANAMAN CABAI",
        f"Waktu: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}",
        f"Fase: {result['phase']}",
        "Gejala: " + (", ".join(kb["symptoms"].get(symptom, {}).get("label", symptom) for symptom in selected_symptoms) if selected_symptoms else "Tidak ada"),
        "Kemungkinan utama: " + result["conclusion"],
        "Saran awal: " + result["recommendation"],
        "", "CATATAN: Hasil adalah petunjuk awal. Periksa juga kondisi tanah, air, akar, hama, dan penyakit.",
    ]
    st.download_button("⬇️  Simpan hasil pengecekan (.txt)", "\n".join(report), file_name="hasil_konsultasi_cabai.txt", mime="text/plain")


# ─── New UI: consultation dashboard ─────────────────────────────────────────
if page == "Konsultasi":
    pepper_svg = '''<svg viewBox="0 0 520 390" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Ilustrasi kebun cabai dengan daun sehat dan buah merah">
  <defs>
    <linearGradient id="sceneSky" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#FDF4D5"/><stop offset="1" stop-color="#E3EFD7"/></linearGradient>
    <linearGradient id="leafBright" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#B4D782"/><stop offset=".56" stop-color="#68A348"/><stop offset="1" stop-color="#39733D"/></linearGradient>
    <linearGradient id="leafDark" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#6FA75A"/><stop offset="1" stop-color="#285D35"/></linearGradient>
    <linearGradient id="pepperRed" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#FF9A72"/><stop offset=".48" stop-color="#E65037"/><stop offset="1" stop-color="#B82E26"/></linearGradient>
    <linearGradient id="soil" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#A56D48"/><stop offset="1" stop-color="#70452F"/></linearGradient>
    <linearGradient id="potter" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#D7A16C"/><stop offset="1" stop-color="#B66E4F"/></linearGradient>
    <filter id="softShadow" x="-25%" y="-25%" width="150%" height="160%"><feDropShadow dx="0" dy="9" stdDeviation="8" flood-color="#385D37" flood-opacity=".15"/></filter>
  </defs>
  <rect x="28" y="18" width="464" height="348" rx="36" fill="url(#sceneSky)"/>
  <circle cx="390" cy="74" r="35" fill="#F6D47B" opacity=".92"/><circle cx="390" cy="74" r="52" fill="#F8D98C" opacity=".2"/>
  <path d="M28 187 Q105 107 182 166 T340 155 T492 165 L492 315 L28 315Z" fill="#B9CE9B" opacity=".75"/>
  <path d="M28 219 Q97 157 184 207 T337 205 T492 194 L492 326 L28 326Z" fill="#85AB70" opacity=".68"/>
  <path d="M28 265 Q119 212 217 249 T381 235 T492 246 L492 336 L28 336Z" fill="#668E55" opacity=".63"/>
  <g opacity=".35" stroke="#E8F0D7" stroke-width="2" fill="none"><path d="M40 284 Q150 250 260 287 T480 278"/><path d="M44 302 Q150 274 265 305 T475 298"/></g>
  <g fill="#FDF9E9" opacity=".88"><circle cx="78" cy="87" r="4"/><circle cx="112" cy="55" r="3"/><circle cx="448" cy="127" r="4"/><circle cx="428" cy="165" r="2.8"/></g>
  <g filter="url(#softShadow)">
    <ellipse cx="261" cy="333" rx="124" ry="18" fill="#385C38" opacity=".15"/>
    <path d="M173 270 Q260 289 348 270 L327 326 Q260 348 194 326Z" fill="url(#potter)"/>
    <ellipse cx="260" cy="270" rx="88" ry="20" fill="#E2B27F"/><ellipse cx="260" cy="269" rx="70" ry="13" fill="url(#soil)"/>
    <path d="M256 268 C259 224 247 190 260 154 C270 124 268 95 254 69" fill="none" stroke="#3E783F" stroke-width="9" stroke-linecap="round"/>
    <path d="M257 210 C224 198 195 174 176 145" fill="none" stroke="#467E42" stroke-width="5" stroke-linecap="round"/>
    <path d="M260 184 C296 166 320 141 334 111" fill="none" stroke="#467E42" stroke-width="5" stroke-linecap="round"/>
    <path d="M257 150 C227 134 211 111 210 87" fill="none" stroke="#467E42" stroke-width="4" stroke-linecap="round"/>
    <path d="M260 222 C298 214 329 194 350 169" fill="none" stroke="#467E42" stroke-width="4" stroke-linecap="round"/>
    <path d="M253 206 C211 213 168 190 150 157 C191 146 232 163 253 206Z" fill="url(#leafBright)"/>
    <path d="M258 177 C287 136 333 127 366 144 C353 179 305 195 258 177Z" fill="url(#leafDark)"/>
    <path d="M254 139 C217 133 187 105 186 76 C218 73 245 101 254 139Z" fill="url(#leafBright)"/>
    <path d="M261 112 C266 74 296 48 326 50 C328 83 302 111 261 112Z" fill="url(#leafDark)"/>
    <path d="M266 233 C304 229 341 242 354 270 C317 279 285 263 266 233Z" fill="url(#leafBright)"/>
    <path d="M253 237 C220 258 180 252 159 229 C187 204 228 212 253 237Z" fill="url(#leafDark)"/>
    <path d="M253 206 Q205 183 163 162 M258 177 Q312 157 352 146 M254 139 Q220 111 194 87 M261 112 Q299 79 319 61 M266 233 Q318 242 345 261 M253 237 Q204 227 170 231" fill="none" stroke="#C4E3A2" stroke-width="2.4" opacity=".8" stroke-linecap="round"/>
    <path d="M297 183 C326 189 338 218 322 244 C309 265 287 256 286 235 C284 214 288 197 297 183Z" fill="url(#pepperRed)"/>
    <path d="M295 184 Q287 171 300 164 Q308 175 300 188Z" fill="#38723B"/>
    <path d="M304 205 Q314 226 299 246" stroke="#FFB49A" stroke-width="3" fill="none" opacity=".85" stroke-linecap="round"/>
    <path d="M220 166 C196 179 187 203 199 224 C210 244 230 230 231 212 C232 192 227 177 220 166Z" fill="url(#pepperRed)"/>
    <path d="M222 168 Q226 156 215 151 Q209 161 219 171Z" fill="#38723B"/>
    <path d="M214 188 Q207 208 220 221" stroke="#FFB49A" stroke-width="2.5" fill="none" opacity=".8" stroke-linecap="round"/>
  </g>
  <g fill="#D7E5BC"><path d="M77 222 Q59 202 47 213 Q58 234 77 222Z"/><path d="M447 218 Q464 198 477 211 Q469 234 447 218Z"/></g>
  <g stroke="#7DA568" stroke-width="2" fill="none" opacity=".8"><path d="M45 217 Q63 218 76 230"/><path d="M478 215 Q462 218 448 230"/></g>
  <path d="M48 314 Q90 306 127 315" stroke="#F9F6E7" stroke-width="3" opacity=".65" fill="none" stroke-linecap="round"/>
</svg>'''
    st.markdown(
        f'''<section class="cc-hero"><div class="cc-hero-copy"><div class="cc-eyebrow">🌿 CABAI CARE · BOTANICAL STUDIO</div>
        <h1>Rawat cabai sepenuh hati, mulai dari <em>tanda kecil.</em></h1>
        <p>Amati daunnya, kenali kebutuhannya. Pilih tanda yang terlihat, lalu dapatkan beberapa kemungkinan penyebab dan saran awal yang mudah dipahami.</p>
        <div class="cc-hero-pills"><span class="cc-pill">🔎 Pilih tanda tanaman</span><span class="cc-pill">🌿 Lihat kemungkinan</span><span class="cc-pill">🌱 Dapatkan saran awal</span></div>
        <a class="cc-hero-cta" href="#cc-consultation">Mulai cek tanaman <span>↗</span></a></div>
        <div class="cc-hero-art"><div class="cc-art-plate">{pepper_svg}</div>
        <div class="cc-floating-tag tag-left">🌿 Tumbuh lebih terarah<span>Baca tanda sebelum bertindak</span></div>
        <div class="cc-floating-tag tag-right">🧩 {len(kb["rules"])} panduan tersedia<span>Untuk mencocokkan tanda tanaman</span></div>
        <div class="cc-art-label"><strong>Setiap daun punya cerita 🍃</strong><small>Amati · Cocokkan · Verifikasi</small></div></div></section>''',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="cc-alert"><div class="cc-alert-icon">💡</div><div><strong>Catatan kecil sebelum mulai</strong><p>Gejala yang sama bisa memiliki beberapa penyebab. Hasil di sini adalah petunjuk awal; periksa juga kondisi tanah, air, akar, hama, dan penyakit sebelum menentukan pupuk atau dosis.</p></div></div>',
        unsafe_allow_html=True,
    )
    st.markdown('''<div class="cc-engine-showcase">
        <div class="cc-engine-header"><div class="cc-eyebrow">LANGKAH PENGECEKAN</div><h3>Bagaimana CabaiCare membantu</h3></div>
        <div class="cc-engine-grid">
            <article class="cc-engine-card warm"><div class="chip">01</div><h4>Pilih tanda</h4><p>Pilih perubahan yang benar-benar terlihat, seperti daun menguning atau pertumbuhan lambat.</p></article>
            <article class="cc-engine-card green"><div class="chip">02</div><h4>Bandingkan pola</h4><p>CabaiCare membandingkan tanda tersebut dengan panduan yang tersedia.</p></article>
            <article class="cc-engine-card orange"><div class="chip">03</div><h4>Lihat kecocokan</h4><p>Hasil menunjukkan kemungkinan yang paling sesuai, bukan kepastian penyebab.</p></article>
            <article class="cc-engine-card slate"><div class="chip">04</div><h4>Baca saran awal</h4><p>Tinjau alasan dan saran, lalu periksa kondisi tanaman sebelum mengambil tindakan.</p></article>
        </div>
    </div>''', unsafe_allow_html=True)
    # At-a-glance cards
    stats = st.columns(3)
    with stats[0]:
        stat_card("Gejala yang dikenali", str(len(kb["symptoms"])), "Tanda visual tanaman cabai")
    with stats[1]:
        stat_card("Panduan tersedia", str(len(kb["rules"])), "Untuk mencocokkan tanda")
    with stats[2]:
        stat_card("Cara kerja", "Cek tanda", "Dari pengamatan ke saran")

    section_heading("KENALI POLA DAUN", "Lihat petunjuk yang sering diamati", "Kartu ini membantu mengenali gejala umum. Tanda visual bukan bukti pasti kekurangan unsur hara.")
    nutrient_cards = [
        ("N", "Nitrogen", "Pertumbuhan daun", "Daun yang lebih tua menguning atau tampak pucat.", "#DCEBCB", "#315E35", "🌿"),
        ("P", "Fosfor", "Akar & energi", "Bagian tanaman tampak keunguan dan pertumbuhan melambat.", "#E9E0F5", "#60468A", "🌱"),
        ("K", "Kalium", "Ketahanan tanaman", "Tepi daun menguning atau mengering kecokelatan.", "#F7E7B8", "#86631B", "🍃"),
        ("Mg", "Magnesium", "Warna daun", "Area di antara tulang daun tua tampak menguning.", "#D7ECE5", "#256C59", "☘️"),
        ("Fe", "Besi", "Daun muda", "Area antartulang daun muda menguning, tulang tetap hijau.", "#DCEAF3", "#2C6584", "🌱"),
        ("?", "Perlu diperiksa", "Faktor lain", "Daun keriting dapat terkait air, akar, hama, atau penyakit.", "#F8DED4", "#9A4A36", "🔎"),
    ]
    nutrient_html = ['<div class="cc-nutrient-grid">']
    for badge, name, kind, desc, soft, ink, icon in nutrient_cards:
        nutrient_html.append(
            f'<article class="cc-nutrient-card" style="--accent-soft:{soft};--accent-ink:{ink}">'
            f'<div class="cc-nutrient-top"><div class="cc-nutrient-badge">{badge}</div><div><div class="cc-nutrient-name">{icon} {name}</div>'
            f'<span class="cc-nutrient-kind">{kind}</span></div></div><p>{desc}</p>'
            f'<span class="cc-nutrient-tag">Petunjuk awal</span></article>'
        )
    nutrient_html.append('</div>')
    st.markdown(''.join(nutrient_html), unsafe_allow_html=True)

    st.markdown('<div id="cc-consultation"></div>', unsafe_allow_html=True)
    section_heading("MULAI DI SINI", "Yuk, cek kondisi tanamanmu", "Pilih tahap pertumbuhan dan tanda yang benar-benar terlihat. Kamu bisa memilih lebih dari satu tanda.")
    form_col, info_col = st.columns([1.65, 1], gap="large")
    labels_to_id = {item["label"]: symptom_id for symptom_id, item in kb["symptoms"].items()}
    with form_col:
        with st.container(border=True):
            st.markdown('''<div class="cc-consult-head"><div class="cc-consult-head-icon">🪴</div><div><h3>Ceritakan kondisi tanaman</h3><p>Mulai dari tanda yang benar-benar terlihat di kebun.</p></div></div>''', unsafe_allow_html=True)
            st.caption("Tidak perlu menebak penyebabnya. Cukup pilih perubahan yang kamu lihat.")
            with st.form("cc_consultation_form", clear_on_submit=False):
                phase = st.radio(
                    "Tahap pertumbuhan tanaman",
                    ["Vegetatif", "Generatif"],
                    horizontal=True,
                    help="Pilih 'Vegetatif' saat tanaman banyak menumbuhkan akar, batang, dan daun. Pilih 'Generatif' saat tanaman mulai berbunga atau berbuah.",
                    key="cc_phase",
                )
                selected_labels = st.multiselect(
                    "Perubahan apa yang terlihat?",
                    options=list(labels_to_id.keys()),
                    help="Pilih satu atau beberapa perubahan yang benar-benar kamu lihat. Tidak yakin? Pilih tanda yang paling jelas.",
                    key="cc_symptoms",
                    placeholder="Pilih tanda yang terlihat…",
                )
                user_cf = st.slider(
                    "Seberapa yakin kamu melihat tanda tersebut?",
                    min_value=0.1, max_value=1.0, value=0.8, step=0.05,
                    help="Pilih nilai rendah jika masih ragu, dan nilai tinggi jika tanda terlihat jelas. Ini bukan ukuran tingkat kerusakan tanaman.",
                    key="cc_user_cf",
                    format="%.2f",
                )
                submitted = st.form_submit_button("🌿  Cek rekomendasi", type="primary", use_container_width=True)
            if submitted:
                selected = [labels_to_id[label] for label in selected_labels]
                if not selected:
                    st.warning("Pilih setidaknya satu tanda yang terlihat agar CabaiCare bisa mulai memeriksa.")
                else:
                    system = ExpertSystem(
                        kb["rules"], kb["symptoms"], kb.get("phase_guidance"), kb.get("rule_sources")
                    )
                    result = system.diagnose(selected, user_cf, phase)
                    result["selected_symptoms"] = selected
                    try:
                        append_history(result)
                        st.session_state["cc_last_result"] = result
                        st.session_state["cc_last_selected"] = selected
                        st.session_state["cc_last_phase"] = phase
                        st.success("Selesai! Hasil pengecekan sudah disimpan ke riwayat.")
                    except OSError as exc:
                        st.session_state["cc_last_result"] = result
                        st.session_state["cc_last_selected"] = selected
                        st.warning(f"Hasil berhasil dihitung, tetapi riwayat belum dapat disimpan: {exc}")

    with info_col:
        with st.container(border=True):
            st.markdown("#### 🌾 Panduan singkat")
            st.markdown('''<div class="cc-step-card"><span class="cc-step-number">01</span><div><strong>Amati daun & batang</strong><small>Perhatikan warna, tepi daun, tulang daun, dan pertumbuhan.</small></div></div>
            <div class="cc-step-card"><span class="cc-step-number">02</span><div><strong>Pilih tanda yang sesuai</strong><small>Pilih hanya perubahan yang benar-benar terlihat pada tanaman.</small></div></div>
            <div class="cc-step-card"><span class="cc-step-number">03</span><div><strong>Baca hasil & alasannya</strong><small>Lihat kemungkinan utama dan saran awal sebelum mengambil tindakan.</small></div></div>''', unsafe_allow_html=True)
        st.markdown('<div style="height:.65rem"></div>', unsafe_allow_html=True)
        st.markdown('''<div class="cc-mini-card"><div class="mini-icon">🧪</div><h3>Periksa sebelum memupuk</h3><p>Gejala serupa bisa dipicu air, pH, akar, hama, atau penyakit. Gunakan hasil sebagai petunjuk awal, bukan penentu dosis.</p></div>''', unsafe_allow_html=True)

    if st.session_state.get("cc_last_result"):
        display_result(st.session_state["cc_last_result"], st.session_state.get("cc_last_selected", []))

elif page == "Basis Pengetahuan":
    page_heading("📚", "PANDUAN TANAMAN", "Panduan gejala dan kemungkinan", "Lihat tanda tanaman yang digunakan CabaiCare untuk menyusun saran.")
    st.markdown(
        '<div class="cc-alert"><div class="cc-alert-icon">🧩</div><div><strong>Bagian pengelolaan panduan</strong><p>Perubahan di sini akan memengaruhi saran yang muncul berikutnya. Tambahkan atau ubah panduan hanya jika informasinya sudah diperiksa dari sumber tepercaya.</p></div></div>',
        unsafe_allow_html=True,
    )
    rules = kb["rules"]
    labels_to_id = {value["label"]: key for key, value in kb["symptoms"].items()}
    reverse_labels = {key: label for label, key in labels_to_id.items()}
    summary_cols = st.columns(3)
    with summary_cols[0]:
        stat_card("Jumlah panduan", str(len(rules)), "Untuk memeriksa tanda")
    with summary_cols[1]:
        stat_card("Tanda tanaman", str(len(kb["symptoms"])), "Yang bisa dipilih")
    with summary_cols[2]:
        stat_card("Kemungkinan", str(len({rule.get("then") for rule in rules})), "Yang dapat disarankan")
    section_heading("PANDUAN YANG DIGUNAKAN", "Tanda dan kemungkinan", "Cari tanda tanaman atau kemungkinan yang ingin kamu lihat.")
    rule_search = st.text_input("Cari panduan", placeholder="Cari tanda, kemungkinan, atau saran…", key="cc_rule_search")
    rule_rows = []
    for rule in rules:
        row = {
            "Kode": rule["id"],
            "Tanda yang diperiksa": " dan ".join(kb["symptoms"].get(symptom, {}).get("label", symptom) for symptom in rule["if"]),
            "Kemungkinan": rule["nutrient"], "Saran awal": rule["recommendation"],
            "Sumber rujukan": ", ".join(kb.get("rule_sources", {}).get(rule["id"], [])),
        }
        rule_rows.append(row)
    df_rules = pd.DataFrame(rule_rows)
    if rule_search:
        mask = df_rules.astype(str).apply(lambda col: col.str.contains(rule_search, case=False, na=False, regex=False)).any(axis=1)
        df_rules = df_rules[mask]
    visible_rules = [rule for rule in rules if not rule_search or rule_search.lower() in (
        str(rule.get("id", "")) + " " + str(rule.get("nutrient", "")) + " " + str(rule.get("recommendation", "")) + " " +
        " ".join(kb["symptoms"].get(symptom, {}).get("label", symptom) for symptom in rule.get("if", []))
    ).lower()]
    rule_html = ['<div class="cc-rule-grid">']
    for rule in visible_rules:
        if_text = " + ".join(kb["symptoms"].get(symptom, {}).get("label", symptom) for symptom in rule.get("if", []))
        cf_pct = max(0, min(100, int(float(rule.get("cf", 0)) * 100)))
        rule_html.append(
            f'<article class="cc-rule-card"><div class="cc-rule-top"><span class="cc-rule-id">{html.escape(rule["id"])}</span>'
            f'<span class="cc-rule-cf">Kekuatan panduan {cf_pct}%</span></div>'
            f'<div class="cc-rule-nutrient">🌿 {html.escape(rule.get("nutrient", "Kesimpulan"))}</div>'
            f'<div class="cc-rule-if"><b>JIKA</b> {html.escape(if_text)}<br><b>MAKA</b> sistem mempertimbangkan kemungkinan tersebut.'
            f'<br><b>SUMBER</b> {html.escape(", ".join(kb.get("rule_sources", {}).get(rule["id"], [])) or "Belum dipetakan")}</div>'
            f'<div class="cc-rule-bar"><span style="width:{cf_pct}%"></span></div></article>'
        )
    rule_html.append('</div>')
    st.markdown(''.join(rule_html), unsafe_allow_html=True)
    st.caption(f"Menampilkan {len(visible_rules)} dari {len(rules)} panduan. Nilai kekuatan membantu mengurutkan hasil, bukan jaminan penyebab.")
    with st.expander("📋 Lihat daftar lengkap", expanded=False):
        st.dataframe(df_rules, use_container_width=True, hide_index=True)

    section_heading("PENGELOLAAN", "Perbarui panduan", "Bagian ini untuk mengubah panduan yang digunakan aplikasi.")
    action = st.radio(
        "Pilih tindakan",
        ["Tambah rule", "Edit rule", "Hapus rule"],
        horizontal=True,
        key="cc_rule_action",
        format_func=lambda value: {
            "Tambah rule": "Tambah panduan",
            "Edit rule": "Ubah panduan",
            "Hapus rule": "Hapus panduan",
        }[value],
    )
    if action == "Tambah rule":
        with st.container(border=True):
            with st.form("cc_add_rule_form", clear_on_submit=False):
                c1, c2 = st.columns(2)
                with c1:
                    rule_id = st.text_input("Kode panduan", placeholder="R11", help="Kode ini hanya dipakai untuk mengenali panduan di dalam aplikasi.").strip().upper()
                    selected_if_labels = st.multiselect("Tanda yang perlu terlihat", list(labels_to_id.keys()), placeholder="Pilih satu atau beberapa tanda…")
                    then_code = st.text_input("Kode kemungkinan", placeholder="DEF_N", help="Kode internal untuk mengelompokkan kemungkinan.").strip()
                    source_id = st.selectbox(
                        "Sumber rujukan", list(kb.get("sources", {})),
                        format_func=lambda item: f"{item} · {kb['sources'][item]['title']}",
                    )
                with c2:
                    nutrient = st.text_input("Nama kemungkinan", placeholder="Contoh: Kekurangan Nitrogen (N)").strip()
                    cf = st.slider("Kekuatan panduan", 0.0, 1.0, 0.6, 0.05, help="Nilai ini mengatur seberapa kuat panduan dipakai saat tanda cocok. Ini bukan persentase kepastian.", key="cc_new_rule_cf")
                    recommendation = st.text_area("Saran awal", height=135, placeholder="Tulis saran awal dengan batasan yang jelas…").strip()
                add_submitted = st.form_submit_button("＋  Simpan aturan", type="primary", use_container_width=True)
            if add_submitted:
                if not rule_id or not selected_if_labels or not then_code or not nutrient or not recommendation:
                    st.error("Semua kolom wajib diisi.")
                elif any(item["id"] == rule_id for item in rules):
                    st.error("Kode panduan sudah digunakan. Pilih kode yang berbeda.")
                else:
                    kb["rules"].append({"id": rule_id, "if": [labels_to_id[label] for label in selected_if_labels], "then": then_code,
                                        "nutrient": nutrient, "cf": cf, "recommendation": recommendation})
                    kb.setdefault("rule_sources", {})[rule_id] = [source_id]
                    try:
                        save_knowledge_base(kb)
                        st.success("Aturan berhasil ditambahkan.")
                        st.rerun()
                    except (OSError, ValueError) as exc:
                        st.error(f"Aturan gagal disimpan: {exc}")
    elif action == "Edit rule":
        if not rules:
            st.info("Belum ada panduan yang bisa diubah.")
        else:
            chosen_id = st.selectbox("Pilih panduan yang ingin diubah", [rule["id"] for rule in rules], key="cc_edit_rule_select")
            current = next(rule for rule in rules if rule["id"] == chosen_id)
            with st.container(border=True):
                with st.form("cc_edit_rule_form"):
                    c1, c2 = st.columns(2)
                    with c1:
                        selected_if_labels = st.multiselect("Tanda yang perlu terlihat", list(labels_to_id.keys()), default=[reverse_labels[symptom] for symptom in current["if"] if symptom in reverse_labels])
                        then_code = st.text_input("Kode kemungkinan", current["then"], help="Kode internal untuk mengelompokkan kemungkinan.").strip()
                        nutrient = st.text_input("Nama kemungkinan", current["nutrient"]).strip()
                        selected_source_ids = st.multiselect(
                            "Sumber rujukan", list(kb.get("sources", {})),
                            default=kb.get("rule_sources", {}).get(chosen_id, []),
                            format_func=lambda item: f"{item} · {kb['sources'][item]['title']}",
                        )
                    with c2:
                        cf = st.slider("Kekuatan panduan", 0.0, 1.0, float(current["cf"]), 0.05, help="Nilai ini mengatur seberapa kuat panduan dipakai saat tanda cocok. Ini bukan persentase kepastian.", key="cc_edit_rule_cf")
                        recommendation = st.text_area("Saran awal", current["recommendation"], height=135).strip()
                    edit_submitted = st.form_submit_button("Simpan perubahan", type="primary", use_container_width=True)
                if edit_submitted:
                    if not selected_if_labels or not then_code or not nutrient or not recommendation or not selected_source_ids:
                        st.error("Semua kolom wajib diisi.")
                    else:
                        current.update({"if": [labels_to_id[label] for label in selected_if_labels], "then": then_code,
                                        "nutrient": nutrient, "cf": cf, "recommendation": recommendation})
                        kb.setdefault("rule_sources", {})[chosen_id] = selected_source_ids
                        try:
                            save_knowledge_base(kb)
                            st.success("Aturan berhasil diperbarui.")
                            st.rerun()
                        except (OSError, ValueError) as exc:
                            st.error(f"Perubahan gagal disimpan: {exc}")
    else:
        if not rules:
            st.info("Tidak ada panduan untuk dihapus.")
        else:
            chosen_id = st.selectbox("Pilih panduan yang akan dihapus", [rule["id"] for rule in rules], key="cc_delete_rule_select")
            st.warning("Menghapus panduan akan mengubah saran yang muncul berikutnya.")
            confirm_delete = st.checkbox(f"Saya yakin ingin menghapus panduan {chosen_id}", key="cc_confirm_delete")
            if st.button("Hapus panduan terpilih", type="primary", disabled=not confirm_delete):
                kb["rules"] = [rule for rule in kb["rules"] if rule["id"] != chosen_id]
                kb.get("rule_sources", {}).pop(chosen_id, None)
                try:
                    save_knowledge_base(kb)
                    st.success(f"Rule {chosen_id} berhasil dihapus.")
                    st.rerun()
                except (OSError, ValueError) as exc:
                    st.error(f"Rule gagal dihapus: {exc}")

elif page == "Riwayat":
    page_heading("🕘", "CATATAN TANAMAN", "Riwayat konsultasi", "Cari kembali konsultasi yang pernah dilakukan dan unduh datanya untuk dokumentasi.")
    if not HISTORY_PATH.exists() or HISTORY_PATH.stat().st_size == 0:
        st.markdown(
            '<div class="cc-alert"><div class="cc-alert-icon">🌱</div><div><strong>Belum ada riwayat konsultasi</strong><p>Setelah kamu menyelesaikan konsultasi, catatannya akan muncul di sini.</p></div></div>',
            unsafe_allow_html=True,
        )
    else:
        try:
            history = pd.read_csv(HISTORY_PATH)
            display_history = history.rename(columns={
                "timestamp": "Waktu",
                "phase": "Tahap tanaman",
                "symptoms": "Tanda yang dipilih",
                "conclusion": "Ringkasan",
                "top_nutrient": "Kemungkinan utama",
                "confidence": "Tingkat kecocokan",
                "matched_rules": "Jumlah panduan cocok",
            }).copy()
            if "Tanda yang dipilih" in display_history:
                display_history["Tanda yang dipilih"] = display_history["Tanda yang dipilih"].fillna("").map(
                    lambda value: ", ".join(
                        kb["symptoms"].get(code, {}).get("label", code)
                        for code in str(value).split(";") if code
                    ) or "Tidak ada tanda"
                )
            if "Tingkat kecocokan" in display_history:
                display_history["Tingkat kecocokan"] = pd.to_numeric(
                    display_history["Tingkat kecocokan"], errors="coerce"
                ).map(lambda value: f"{value:.0%}" if pd.notna(value) else "—")
            if "Jumlah panduan cocok" in display_history:
                display_history["Jumlah panduan cocok"] = display_history["Jumlah panduan cocok"].fillna("").map(
                    lambda value: str(len([code for code in str(value).split(";") if code]))
                )
            history_cols = st.columns([2.4, 1, 1])
            with history_cols[0]:
                query = st.text_input("Cari riwayat", placeholder="Tanda, ringkasan, atau kemungkinan…", key="cc_history_query")
            with history_cols[1]:
                stat_card("Total konsultasi", str(len(history)))
            with history_cols[2]:
                latest = str(history.iloc[-1]["timestamp"])[:10] if not history.empty and "timestamp" in history else "—"
                stat_card("Tanggal terakhir", latest)
            filtered = history
            filtered_display = display_history
            if query:
                mask = display_history.astype(str).apply(lambda col: col.str.contains(query, case=False, na=False, regex=False)).any(axis=1)
                filtered = history.loc[mask]
                filtered_display = display_history.loc[mask]
            chart_col, insight_col = st.columns([1.1, 1.3], gap="large")
            with chart_col:
                st.markdown("#### 📊 Ringkasan hasil sebelumnya")
                if "top_nutrient" in history.columns and not history.empty:
                    counts = (
                        history["top_nutrient"]
                        .fillna("Tidak diketahui")
                        .value_counts()
                        .rename_axis("Kemungkinan")
                        .reset_index(name="Jumlah")
                    )
                    st.caption("Berapa kali setiap kemungkinan utama muncul pada hasil sebelumnya.")
                    st.bar_chart(
                        counts,
                        x="Kemungkinan",
                        y="Jumlah",
                        horizontal=True,
                        color=theme["green"],
                        x_label="Unsur hara utama",
                        y_label="Jumlah konsultasi",
                        height=max(190, min(360, 64 * len(counts))),
                    )
                    st.dataframe(
                        counts,
                        use_container_width=True,
                        hide_index=True,
                        height=min(220, 38 * (len(counts) + 1)),
                    )
                else:
                    st.info("Belum ada data untuk divisualisasikan.")
            with insight_col:
                st.markdown("#### 🌱 Catatan dari riwayat")
                st.markdown('''<div class="cc-mini-card"><div class="mini-icon">🗂️</div><h3>Catatan pengecekan tersimpan</h3><p>Bandingkan tanda dan saran dari waktu ke waktu. Catatan ini belum memastikan penyebab tanaman di kebun.</p></div>''', unsafe_allow_html=True)
            with st.container(border=True):
                st.dataframe(filtered_display, use_container_width=True, hide_index=True)
            st.caption(f"Menampilkan {len(filtered)} dari {len(history)} catatan.")
            with st.expander("🗑️ Hapus satu catatan", expanded=False):
                if filtered.empty:
                    st.caption("Tidak ada catatan yang cocok untuk dihapus.")
                else:
                    selected_index = st.selectbox(
                        "Pilih catatan yang akan dihapus",
                        options=filtered.index.tolist(),
                        format_func=lambda row_index: (
                            f"{history.at[row_index, 'timestamp']} · "
                            f"{history.at[row_index, 'top_nutrient'] if 'top_nutrient' in history else 'Tidak diketahui'}"
                        ),
                        key="cc_history_delete_selection",
                    )
                    selected_record = history.loc[selected_index]
                    selected_symptoms = [
                        kb["symptoms"].get(code, {}).get("label", code)
                        for code in str(selected_record.get("symptoms", "")).split(";")
                        if code
                    ]
                    preview_fields = [
                        ("Waktu", str(selected_record.get("timestamp", "—"))),
                        ("Fase", str(selected_record.get("phase", "—"))),
                        ("Gejala", ", ".join(selected_symptoms) or "Tidak ada gejala"),
                        ("Kemungkinan utama", str(selected_record.get("top_nutrient", "Tidak diketahui"))),
                    ]
                    preview_columns = st.columns([1.2, .8, 2, 1.1])
                    for column, (label, value) in zip(preview_columns, preview_fields):
                        with column:
                            st.markdown(
                                f'<div class="cc-history-preview"><span>{html.escape(label)}</span>'
                                f'<strong>{html.escape(value)}</strong></div>',
                                unsafe_allow_html=True,
                            )
                    confirm_key = f"cc_confirm_history_delete_{selected_index}_{history.at[selected_index, 'timestamp']}"
                    confirm_delete = st.checkbox(
                        "Saya yakin ingin menghapus catatan ini.", key=confirm_key
                    )
                    if st.button(
                        "Hapus catatan terpilih",
                        type="primary",
                        disabled=not confirm_delete,
                        key="cc_delete_history_record",
                    ):
                        try:
                            history.drop(index=selected_index).to_csv(HISTORY_PATH, index=False)
                            st.success("Catatan konsultasi berhasil dihapus.")
                            st.rerun()
                        except OSError as exc:
                            st.error(f"Catatan gagal dihapus: {exc}")
            st.download_button("⬇️  Simpan riwayat (.csv)", filtered_display.to_csv(index=False).encode("utf-8-sig"), file_name="riwayat_konsultasi_cabai.csv", mime="text/csv")
        except (OSError, pd.errors.ParserError, pd.errors.EmptyDataError) as exc:
            st.error(f"Riwayat tidak dapat dibaca: {exc}")

else:
    page_heading("🌿", "TENTANG CABAI CARE", "Cara kerja dan sumber", "Kenali cara aplikasi membaca tanda tanaman, menyusun saran awal, dan sumber informasi yang digunakan.")
    section_heading("LANGKAH PENGECEKAN", "Dari tanda sampai saran", "CabaiCare menunjukkan alasan di balik hasil agar kamu bisa memeriksanya kembali.")
    feature_cols = st.columns(3)
    feature_data = [
        ("👀", "1. Pilih tanda", "Pilih perubahan yang terlihat dan tahap pertumbuhan tanaman."),
        ("🧠", "2. Bandingkan pola", "Aplikasi membandingkan tanda pilihanmu dengan panduan yang tersedia."),
        ("✨", "3. Tinjau saran", "Lihat kemungkinan yang paling sesuai, alasan, dan saran awal."),
    ]
    for col, (icon, title, desc) in zip(feature_cols, feature_data):
        with col:
            st.markdown(f'<div class="cc-mini-card"><div class="mini-icon">{icon}</div><h3>{title}</h3><p>{desc}</p></div>', unsafe_allow_html=True)
    section_heading("SUMBER INFORMASI", "Bahan bacaan", "Sumber berikut menjadi bahan penyusunan panduan. Hasil aplikasi tetap perlu diperiksa dengan kondisi tanaman yang sebenarnya.")
    with st.container(border=True):
        for source_id, source in kb.get("sources", {}).items():
            st.markdown(f"**{source_id}. {source['title']}** · {source['publisher']}")
            st.markdown(f"[Buka sumber]({source['url']})")
            st.caption(source["scope"])
    st.caption("Sumber-sumber ini memberi informasi umum tentang budidaya, tanda pada tanaman, dan tahap pertumbuhannya.")
    st.markdown(
        '<div class="cc-alert"><div class="cc-alert-icon">⚠️</div><div><strong>Gunakan hasil sebagai petunjuk awal</strong><p>Gejala visual tidak selalu berarti kekurangan unsur hara. Periksa tanah, air, pH, akar, hama, dan penyakit. Aplikasi tidak menentukan dosis pupuk otomatis; konsultasikan dengan penyuluh atau gunakan hasil uji tanah.</p></div></div>',
        unsafe_allow_html=True,
    )

st.markdown('<div class="cc-footer"><b>🌶️ CabaiCare</b> · Panduan awal merawat tanaman cabai · UTS Kelompok 6</div>', unsafe_allow_html=True)

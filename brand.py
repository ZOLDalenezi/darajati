"""Darajati visual identity. All UI is rendered by the Python application."""
import base64
from pathlib import Path
import streamlit as st

ASSETS = Path(__file__).parent / 'assets'

def logo_uri():
    p = ASSETS / 'darajati-logo.png'
    return 'data:image/png;base64,' + base64.b64encode(p.read_bytes()).decode() if p.exists() else ''

def apply_theme():
    st.markdown('''<style>
    @font-face{font-family:Darajati;src:url('app/static/NotoSansArabic.ttf') format('truetype');font-display:swap}
    :root{--navy:#153e52;--teal:#16877c;--muted:#667b84;--gold:#c5a365}
    html,body,[data-testid="stAppViewContainer"],button,input,textarea,select{font-family:Darajati,Tahoma,Arial,sans-serif;direction:rtl}
    .stApp{background:#f5f7f7;color:#153e52}
    .block-container{max-width:1140px;padding-top:1.3rem;padding-bottom:3rem}
    header[data-testid="stHeader"]{background:transparent}
    [data-testid="stToolbar"]{display:none}
    h1,h2,h3,h4{color:#153e52;letter-spacing:-.035em;font-family:Darajati,Tahoma,sans-serif!important}
    p,li{line-height:1.85}
    .stApp p,.stApp li,.stApp label,.stApp button,.stApp input,.stApp textarea,.stApp small,.stApp span:not([data-testid="stIconMaterial"]),.stApp td,.stApp th{font-family:Darajati,Tahoma,Arial,sans-serif}
    [data-testid="stMarkdownContainer"] p{font-size:1rem}
    a{color:#16877c}
    .brandbar{display:flex;align-items:center;justify-content:space-between;margin:0 0 1.2rem;padding:0 0 1rem;border-bottom:1px solid #dce5e6}
    .brand{display:flex;align-items:center;gap:12px}.brand img{width:64px;height:64px;object-fit:contain}.brand strong{display:block;font-size:1.5rem;line-height:1.4}.brand small{color:#667b84;font-size:.7rem;letter-spacing:.13em}
    .brand-note{color:#667b84;font-size:.76rem}
    .hero{display:grid;grid-template-columns:1.4fr 1fr;gap:32px;align-items:center;padding:2.8rem 2.6rem;background:#e8f1ef;border:1px solid #d5e5e0;border-radius:28px;margin:1.4rem 0 1.5rem;position:relative;overflow:hidden}
    .eyebrow{font-size:.78rem;color:#16877c;font-weight:700;display:block;margin-bottom:12px}
    .hero h1{font-size:clamp(2.3rem,5vw,3.7rem);font-weight:800;line-height:1.35;margin:0 0 1rem}.hero h1 em{color:#16877c;font-style:normal}.hero p{font-size:1rem;color:#4e6871;max-width:470px;margin:0}
    .hero-preview{background:#fff;border:1px solid #d9e6e4;border-radius:22px;padding:1.5rem;transform:rotate(-3deg);box-shadow:0 18px 35px #153e5210;max-width:325px;margin:auto;width:100%}
    .preview-label{color:#667b84;font-size:.8rem}.preview-number{font-family:Arial,sans-serif;font-size:3.3rem;font-weight:700;direction:ltr;color:#153e52;line-height:1.3;margin:12px 0}.preview-number small{font-size:1.2rem;color:#16877c}
    .progress-track{height:8px;background:#edf2f1;border-radius:10px;margin:16px 0}.progress-fill{height:8px;background:#16877c;width:87%;border-radius:10px}.preview-note{padding:10px 12px;background:#edf6f1;border-radius:12px;color:#237969;font-size:.78rem}
    .section-caption{font-size:.85rem;color:#667b84;margin-bottom:1rem}
    .feature{padding:1.5rem;border:1px solid #dce5e6;border-radius:20px;background:white;min-height:174px;margin-bottom:.8rem}.feature .num{display:inline-block;color:#16877c;font:700 .75rem Arial;margin-bottom:13px}.feature h3{font-size:1.12rem;margin:0 0 .5rem}.feature p{font-size:.85rem;color:#667b84;margin:0}
    .mishal-callout{background:#153e52;border-radius:23px;padding:1.7rem 2rem;margin-top:1rem;color:#fff}.mishal-callout h3{color:#fff;margin:0 0 .5rem;font-size:1.35rem}.mishal-callout p{color:#d3e6e5;margin:0;font-size:.9rem}
    .pagehead{margin:1.7rem 0 1.4rem}.pagehead h1{font-size:2.05rem;margin:0 0 .25rem}.pagehead p{color:#667b84;margin:0;font-size:.92rem}
    .stat{background:#fff;border:1px solid #dce5e6;border-radius:19px;padding:1.25rem;margin-bottom:.75rem}.stat b{display:block;font:700 2.4rem Arial;color:#16877c;direction:ltr;text-align:right}.stat span{display:block;font-size:.82rem;color:#667b84;margin-top:.4rem}
    .subject-line{display:flex;justify-content:space-between;align-items:center;gap:12px;border-bottom:1px solid #e5ecec;padding:.8rem 0}.subject-line strong{font-size:.9rem}.subject-line span{font-size:.8rem;color:#667b84}
    .note{padding:1rem 1.2rem;background:#eaf3f1;border-right:3px solid #16877c;border-radius:12px;font-size:.85rem;line-height:1.9;margin:.8rem 0;color:#365d61}
    .footer{border-top:1px solid #dce5e6;padding-top:1.3rem;margin-top:2.6rem;color:#75868c;font-size:.73rem;text-align:center;line-height:1.9}
    [data-testid="stButton"] button,[data-testid="stDownloadButton"] button{border-radius:12px;min-height:46px;font-weight:600;border-color:#d4e1df;transition:.15s}
    [data-testid="stButton"] button[kind="primary"],[data-testid="stDownloadButton"] button[kind="primary"]{background:#16877c;border-color:#16877c;color:#fff}
    [data-testid="stButton"] button:hover{border-color:#16877c;color:#16877c;background:#edf6f3}
    [data-testid="stNumberInput"] input,[data-testid="stTextInput"] input{min-height:44px;text-align:right}
    [data-testid="stNumberInput"] input{font-family:Arial,sans-serif;direction:ltr}
    [data-testid="stVerticalBlockBorderWrapper"]{border-radius:18px}
    [data-testid="stChatMessage"]{background:white;border:1px solid #dce5e6;border-radius:18px;margin-bottom:.8rem}
    [data-testid="stChatInput"] textarea{direction:rtl;text-align:right}
    [data-testid="stTable"] th,[data-testid="stTable"] td{text-align:right!important}
    .st-key-navigation [data-testid="stHorizontalBlock"]{flex-wrap:nowrap;gap:.35rem}
    .st-key-navigation button{font-size:.8rem;min-height:42px;padding:.3rem .4rem}
    .st-key-navigation [data-testid="stColumn"]{min-width:0!important}
    @media(max-width:700px){
      .block-container{padding-top:.7rem;padding-left:1rem;padding-right:1rem}
      .brand-note{display:none}.brand img{width:51px;height:51px}
      .hero{grid-template-columns:1fr;padding:1.7rem 1.4rem;gap:26px;margin-top:1rem}.hero h1{font-size:2.5rem}.hero-preview{max-width:290px;transform:rotate(-2deg);padding:1.15rem}
      .feature{min-height:0;padding:1.15rem}.mishal-callout{padding:1.4rem}.pagehead h1{font-size:1.7rem}
      .st-key-navigation [data-testid="stHorizontalBlock"]{flex-wrap:wrap!important}
      .st-key-navigation [data-testid="stColumn"]{width:30%!important;flex:1 1 30%!important}
      .stat b{font-size:2rem}
    }
    </style>''', unsafe_allow_html=True)

def header():
    st.markdown(f'<div class="brandbar"><div class="brand"><img src="{logo_uri()}" alt="شعار درجتي"><div><strong>درجتي</strong><small>DARAJATI</small></div></div><span class="brand-note">خطوتك الجاية تبدأ بفهم درجتك.</span></div>',unsafe_allow_html=True)

def heading(title, subtitle=''):
    st.markdown(f'<div class="pagehead"><h1>{title}</h1><p>{subtitle}</p></div>',unsafe_allow_html=True)

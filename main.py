import streamlit as st
import pandas as pd
import os
import datetime
from enum import Enum

# ---- Language & Health Advice Dictionaries ----
LANGS = {
    # ... [Same as you pasted: en, hi, hi_en] ...
}

HEALTH_ADVICE = {
    # ... [Same as you pasted] ...
}
GENERAL_HEALTH_WARNING = "If any parameter FAILS: Boil or filter water before use. Consult water safety experts. For infants/pregnant/ill, strict care needed!"

ALL_PARAMS = [ ... ] # [Your parameter list]
STP_PARAMS = [ ... ] # [Your STP parameter list]
PARAMS_LIMITS = { ... } # [Your limits dictionary]

def get_csv_path(fname):
    if os.path.exists(fname): return fname
    if os.path.exists(f"data/{fname}"): return f"data/{fname}"
    return None

@st.cache_data
def load_pincode_df():
    path = get_csv_path("pincode.csv")
    if not path:
        st.error("pincode.csv missing! Upload to root or data/")
        return pd.DataFrame()
    df = pd.read_csv(path)
    df['pincode'] = df['pincode'].astype(str)
    return df

# ---- ROUTING setup
class Page(Enum):
    HOME = 1
    SAFE_WATER = 2
    HAND_WASHING = 3
    HYGIENE_EDUC = 4
    DISASTER = 5
    AI_BOT = 6
    JJM_INSIGHTS = 7
    ANALYTICS = 8
    FEEDBACK = 9

if 'page' not in st.session_state:
    st.session_state.page = Page.HOME
def go_to(page): st.session_state.page = page

# ---- Modules for home page
modules = [
    {'title': 'Safe Water', 'desc': 'Check and predict water quality.', 'icon': '💧', 'page': Page.SAFE_WATER},
    {'title': 'Hand Washing', 'desc': 'Learn best hand hygiene practices.', 'icon': '🧼', 'page': Page.HAND_WASHING},
    {'title': 'Hygiene Education', 'desc': 'Hygiene info & training.', 'icon': '📚', 'page': Page.HYGIENE_EDUC},
    {'title': 'Disaster Response', 'desc': 'Emergency guidance & help.', 'icon': '🚨', 'page': Page.DISASTER},
    {'title': 'Water AI Chatbot', 'desc': 'Ask JJM/Water Q&A from AI!', 'icon': '🤖', 'page': Page.AI_BOT},
    {'title': 'JJM Insights', 'desc': 'Explore Jal Jeevan Mission tips.', 'icon': '🇮🇳', 'page': Page.JJM_INSIGHTS},
    {'title': 'Data Analytics', 'desc': 'Charts & batch uploads.', 'icon': '📊', 'page': Page.ANALYTICS},
    {'title': 'Feedback', 'desc': 'Give ideas or report any issue.', 'icon': '📝', 'page': Page.FEEDBACK},
]

# ---- Home Page Function ----
def home_page():
    st.markdown("<h1 style='text-align:center;color:#0073b1'>JalMitr AI Home</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align:center;'>All Water & Hygiene Modules, One Click Away</h4>", unsafe_allow_html=True)
    cols = st.columns(4)
    for i, m in enumerate(modules):
        with cols[i%4]:
            st.markdown(f"<div style='background:#f5f8fa;border-radius:12px;padding:24px;text-align:center;box-shadow:0 2px 12px #e0e8ef;'>"
                        f"<div style='font-size:45px'>{m['icon']}</div>"
                        f"<div style='font-size:18px;font-weight:600'>{m['title']}</div>"
                        f"<div style='font-size:14px;color:#555'>{m['desc']}</div></div>", unsafe_allow_html=True)
            if st.button(m['title'], key=m['title']):
                go_to(m['page'])
    st.info("JalMitr par saare features ek jagah.")

# ---- Safe Water Prediction Module ----
def safe_water_module():
    st.button("⬅️ Back", on_click=lambda: go_to(Page.HOME))
    st.title("💧 Safe Water Quality Prediction")

    lang_code = st.selectbox("🌐 "+LANGS['en']["select_lang"], ["en", "hi_en", "hi"], format_func=lambda x: {"en":"English","hi_en":"Hinglish","hi":"हिन्दी"}[x])
    msg = LANGS[lang_code]

    pincode = st.text_input(msg['pin_label'], key='pin')
    stype = st.selectbox(msg['sample_type'], ["GROUND","RIVER","TAP","RO","STP"], key="stype")

    if 'old_pin' not in st.session_state: st.session_state['old_pin'] = ''
    if 'old_stype' not in st.session_state: st.session_state['old_stype'] = ''
    if pincode != st.session_state['old_pin'] or stype != st.session_state['old_stype']:
        for p in set(ALL_PARAMS + STP_PARAMS): st.session_state[f"param_{p}"] = None
        st.session_state['old_pin'] = pincode
        st.session_state['old_stype'] = stype

    pincode_df = load_pincode_df()
    if not pincode:
        st.info(msg['pin_label'])
        st.stop()
    row = pincode_df[pincode_df['pincode']==pincode]
    if row.empty:
        st.error(msg['pin_not_found'])
        st.stop()
    else:
        st.info(f"{msg['district']}: {row.iloc[0]['district']} | {msg['state']}: {row.iloc[0]['statename']} | {msg['office']}: {row.iloc[0]['officename']}")

    params = STP_PARAMS if stype == "STP" else ALL_PARAMS
    min_params = 3 if stype == "STP" else 5

    st.header(msg['params_entry'])
    vals = {}
    param_cols = st.columns(4)
    for idx, pname in enumerate(params):
        l,u,std = PARAMS_LIMITS.get(pname, (0.0,1000.0,0.0))
        dtype_float = any(isinstance(v, float) for v in (l,u)) or isinstance(std, float) or (isinstance(std,tuple) and isinstance(std[0],float))
        defval = st.session_state.get(f"param_{pname}", None)
        mv = 0.01 if dtype_float else 1
        minv = float(l) if dtype_float else int(l)
        maxv = float(u) if dtype_float else int(u)
        with param_cols[idx % 4]:
            vals[pname] = st.number_input(
                pname, min_value=minv, max_value=maxv,
                value=defval if defval not in (None,"") else None,
                step=mv, key=f"param_{pname}", format="%.3f" if dtype_float else "%d"
            )
    if st.button(msg["predict_btn"]):
        filled = [v for v in vals.values() if v not in (None,0,"")]
        tds_ok = (stype=="STP") or (vals.get("TDS",0) not in (None,0,""))
        if not tds_ok:
            st.error(msg["tds_req"])
            st.stop()
        if len(filled) < min_params:
            st.warning(msg["fill_warn"].format(n=min_params))
            st.stop()
        st.success(msg["prediction_result"])
        table, fail = [], []
        for pname in params:
            val = vals[pname]
            l,u,std = PARAMS_LIMITS.get(pname,(0.0,1000.0,0.0))
            if val in (None,0,""):
                status, sval, slimit = msg["not_entered"], "--", f"{std[0]}–{std[1]}" if isinstance(std,tuple) else f"≤{std}"
            else:
                sval = val
                if pname=="pH" and isinstance(std,tuple):
                    status = msg["pass"] if std[0]<=val<=std[1] else msg["fail"]
                    slimit = f"{std[0]}–{std[1]}"
                else:
                    status = msg["pass"] if val<=std else msg["fail"]
                    slimit = f"≤{std}"
                if status in (msg["fail"],"❌ Fail","❌ असफल","Fail"):
                    fail.append(pname)
            table.append({'Parameter': pname,'Value': sval,'Standard': slimit,'Status': status,
                          'Health Advice': (HEALTH_ADVICE[pname] if status==msg["fail"] and pname in HEALTH_ADVICE else "-")})
        st.table(pd.DataFrame(table))
        st.header(msg["advice_heading"])
        if stype == "STP":
            if not fail: st.success(msg["stp_ok"])
            else:
                st.error(msg["stp_not_ok"]+": "+", ".join(fail))
                for f in fail:
                    st.write(f"- {f}: {HEALTH_ADVICE.get(f, 'Check treatment plant process, reconsider reuse.')}")
                st.info(GENERAL_HEALTH_WARNING)
        else:
            if not fail: st.success(msg["safe_water"])
            else:
                st.error(msg["unsafe_water"])
                for f in fail:
                    st.write(f"- {f}: {HEALTH_ADVICE.get(f, 'Check for local contaminants and avoid raw consumption.')}")
                st.info(GENERAL_HEALTH_WARNING)
        csv = pd.DataFrame(table).to_csv(index=False).encode('utf-8')
        st.download_button(label=msg["download"], data=csv, file_name=f"JalMitr_Report_{datetime.date.today()}.csv", mime='text/csv')

# ---- Dummy Module Placeholders (copy pattern to expand) ----
def hand_washing_module():
    st.button("⬅️ Back", on_click=lambda: go_to(Page.HOME))
    st.title("🧼 Hand Washing")
    st.info("Hand hygiene module coming soon.")

def hygiene_education_module():
    st.button("⬅️ Back", on_click=lambda: go_to(Page.HOME))
    st.title("📚 Hygiene Education")
    st.info("All about hygiene for kids/families (coming soon).")

def disaster_response_module():
    st.button("⬅️ Back", on_click=lambda: go_to(Page.HOME))
    st.title("🚨 Disaster Response")
    st.info("Water disaster and crisis help will be here.")

def ai_bot_module():
    st.button("⬅️ Back", on_click=lambda: go_to(Page.HOME))
    st.title("🤖 Water AI Chatbot")
    st.info("Chat with OpenAI/Gemini/JJM Assistant (coming soon).")

def jjm_insights_module():
    st.button("⬅️ Back", on_click=lambda: go_to(Page.HOME))
    st.title("🇮🇳 JJM Insights")
    st.info("India's Jal Jeevan Mission tips, Q&A.")

def analytics_module():
    st.button("⬅️ Back", on_click=lambda: go_to(Page.HOME))
    st.title("📊 Data Analytics")
    st.info("Charts, batch uploads, trends module coming soon.")

def feedback_module():
    st.button("⬅️ Back", on_click=lambda: go_to(Page.HOME))
    st.title("📝 Feedback")
    st.info("Feedback/complaint/contact form coming soon.")

# ---- Main Router ----
if st.session_state.page == Page.HOME:
    home_page()
elif st.session_state.page == Page.SAFE_WATER:
    safe_water_module()
elif st.session_state.page == Page.HAND_WASHING:
    hand_washing_module()
elif st.session_state.page == Page.HYGIENE_EDUC:
    hygiene_education_module()
elif st.session_state.page == Page.DISASTER:
    disaster_response_module()
elif st.session_state.page == Page.AI_BOT:
    ai_bot_module()
elif st.session_state.page == Page.JJM_INSIGHTS:
    jjm_insights_module()
elif st.session_state.page == Page.ANALYTICS:
    analytics_module()
elif st.session_state.page == Page.FEEDBACK:
    feedback_module()


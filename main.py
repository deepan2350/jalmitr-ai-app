import streamlit as st
import pandas as pd
import os
import datetime
from enum import Enum

# ---------------------- Language & Health Dictionaries ----------------------
LANGS = {
    "en": {
        "select_lang": "Select Language",
        "pin_label": "Enter Pincode (Required):",
        "pin_not_found": "Pincode not found!",
        "district": "District",
        "state": "State",
        "office": "Office",
        "sample_type": "Sample Type",
        "params_entry": "Enter Water Parameters",
        "predict_btn": "Predict",
        "prediction_result": "Prediction Result",
        "pass": "✔️ Pass",
        "fail": "❌ Fail",
        "not_entered": "Not Entered",
        "fill_warn": "Fill at least {n} parameters (with TDS).",
        "tds_req": "TDS is compulsory.",
        "safe_water": "Water is SAFE as per standards.",
        "unsafe_water": "Water is NOT SAFE!",
        "advice_heading": "Advice",
        "stp_ok": "STP running well!",
        "stp_not_ok": "STP not OK, fix needed.",
        "download": "Download CSV"
    }
}

HEALTH_ADVICE = {
    "TDS": "High TDS harms kidneys, especially infants.",
    "BOD": "High BOD: organic pollution.",
    "pH": "Imbalanced pH: can corrode pipes, harm gut."
}

GENERAL_HEALTH_WARNING = (
    "If any parameter FAILS: Boil/filter water before use. Infants/ill—extra care. Consult water experts if needed."
)

ALL_PARAMS = ["pH", "TDS", "BOD"]
STP_PARAMS = ["pH", "TDS"]
PARAMS_LIMITS = {
    "pH": (0.0, 14.0, (6.5, 8.5)),
    "TDS": (0.0, 5000.0, 2000.0),
    "BOD": (0.0, 100.0, 10.0)
}

# ---------------------- Helper: Resolve CSV Path ----------------------
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

# ---------------------- Enum & Routing Setup ----------------------
class Page(Enum):
    HOME = 1
    SAFE_WATER = 2
    PLANT_OPERATIONS = 3
    WASH = 4
    DISASTER = 5
    Q_BOX = 6
    JJM_INSIGHTS = 7
    ANALYTICS = 8
    FEEDBACK = 9

if 'page' not in st.session_state:
    st.session_state.page = Page.HOME
def go_to(page):
    st.session_state.page = page

modules = [
    {"title": "Safe Water", "desc": "Clean water quality AI", "icon": "💧", "page": Page.SAFE_WATER},
    {"title": "Plant Operations", "desc": "WTP, STP, ETP plant ops & performance.", "icon": "🏭", "page": Page.PLANT_OPERATIONS},
    {"title": "WASH", "desc": "Hygiene awareness, tips, training.", "icon": "🧼", "page": Page.WASH},
    {"title": "Disaster Response", "desc": "Emergency guidance & help.", "icon": "🚨", "page": Page.DISASTER},
    {"title": "Q Box", "desc": "Ask Water Q&A from AI!", "icon": "🤖", "page": Page.Q_BOX},
    {'title': 'JJM Insights', 'desc': 'Explore Jal Jeevan Mission tips.', 'icon': '🇮🇳', 'page': Page.JJM_INSIGHTS},
    {'title': 'Data Analytics', 'desc': 'Charts & batch uploads.', 'icon': '📊', 'page': Page.ANALYTICS},
    {'title': 'Feedback', 'desc': 'Give ideas or report any issue.', 'icon': '📝', 'page': Page.FEEDBACK},
]

# ----------------------- Home Page Cards -----------------------
def home_page():
    st.markdown("<h1 style='text-align:center;color:#0073b1'>JalMitr AI Home</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align:center;'>All Water & Hygiene Modules, One Click Away</h4>", unsafe_allow_html=True)
    cols = st.columns(4)
    for i, m in enumerate(modules):
        with cols[i % 4]:
            st.markdown(
                f"<div style='background:#f5f8fa;border-radius:12px;padding:24px;text-align:center;"
                f"box-shadow:0 2px 12px #e0e8ef;'>"
                f"<div style='font-size:45px'>{m['icon']}</div>"
                f"<div style='font-size:18px;font-weight:600'>{m['title']}</div>"
                f"<div style='font-size:14px;color:#555'>{m['desc']}</div></div>",
                unsafe_allow_html=True
            )
            if st.button(m['title'], key=m['title']):
                go_to(m['page'])
    st.info("JalMitr – All Features, One Destination")

# --------------------- Safe Water Prediction Module ---------------------
def safe_water_module():
    st.button("⬅️ Back", on_click=lambda: go_to(Page.HOME))
    st.title("💧 Safe Water Quality Prediction")
    lang_code = st.selectbox(
        "🌐 "+LANGS['en']["select_lang"],
        ["en"],  # Aap other langs tabhi dijiye jab data bhar lein
        format_func=lambda x: {"en": "English"}[x]
    )
    msg = LANGS[lang_code]
    pincode = st.text_input(msg['pin_label'], key='pin')
    stype = st.selectbox(msg['sample_type'], ["GROUND", "RIVER", "TAP", "RO", "STP"], key="stype")

    if 'old_pin' not in st.session_state: st.session_state['old_pin'] = ''
    if 'old_stype' not in st.session_state: st.session_state['old_stype'] = ''
    if pincode != st.session_state['old_pin'] or stype != st.session_state['old_stype']:
        for p in set(ALL_PARAMS + STP_PARAMS):
            st.session_state[f"param_{p}"] = None
        st.session_state['old_pin'] = pincode
        st.session_state['old_stype'] = stype

    pincode_df = load_pincode_df()
    if not pincode:
        st.info(msg['pin_label'])
        st.stop()
    row = pincode_df[pincode_df['pincode'] == pincode]
    if row.empty:
        st.error(msg['pin_not_found'])
        st.stop()
    else:
        st.info(f"{msg['district']}: {row.iloc[0]['district']} | "
                f"{msg['state']}: {row.iloc[0]['statename']} | "
                f"{msg['office']}: {row.iloc[0]['officename']}")
    params = STP_PARAMS if stype == "STP" else ALL_PARAMS
    min_params = 3 if stype == "STP" else 5
    st.header(msg['params_entry'])
    vals = {}
    param_cols = st.columns(4)
    for idx, pname in enumerate(params):
        l, u, std = PARAMS_LIMITS.get(pname, (0.0, 1000.0, 0.0))
        dtype_float = any(isinstance(v, float) for v in (l, u)) or isinstance(std, float) or (isinstance(std, tuple) and isinstance(std[0], float))
        defval = st.session_state.get(f"param_{pname}", None)
        mv = 0.01 if dtype_float else 1
        minv = float(l) if dtype_float else int(l)
        maxv = float(u) if dtype_float else int(u)
        with param_cols[idx % 4]:
            vals[pname] = st.number_input(
                pname,
                min_value=minv,
                max_value=maxv,
                value=defval if defval not in (None, "") else None,
                step=mv,
                key=f"param_{pname}",
                format="%.3f" if dtype_float else "%d"
            )
    if st.button(msg["predict_btn"]):
        filled = [v for v in vals.values() if v not in (None, 0, "")]
        tds_ok = (stype == "STP") or (vals.get("TDS", 0) not in (None, 0, ""))
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
            l, u, std = PARAMS_LIMITS.get(pname, (0.0, 1000.0, 0.0))
            if val in (None, 0, ""):
                status, sval, slimit = msg["not_entered"], "--", f"{std[0]}–{std[1]}" if isinstance(std, tuple) else f"≤{std}"
            else:
                sval = val
                if pname == "pH" and isinstance(std, tuple):
                    status = msg["pass"] if std[0] <= val <= std[1] else msg["fail"]
                    slimit = f"{std[0]}–{std[1]}"
                else:
                    status = msg["pass"] if val <= std else msg["fail"]
                    slimit = f"≤{std}"
                if status in (msg["fail"], "❌ Fail"):
                    fail.append(pname)
            table.append({
                'Parameter': pname,
                'Value': sval,
                'Standard': slimit,
                'Status': status,
                'Health Advice': HEALTH_ADVICE[pname] if status == msg["fail"] and pname in HEALTH_ADVICE else "-"
            })
        st.table(pd.DataFrame(table))
        st.header(msg["advice_heading"])
        if stype == "STP":
            if not fail:
                st.success(msg["stp_ok"])
            else:
                st.error(msg["stp_not_ok"] + ": " + ", ".join(fail))
                for f in fail:
                    st.write(f"- {f}: {HEALTH_ADVICE.get(f, 'Check treatment plant process, reconsider reuse.')}")
                st.info(GENERAL_HEALTH_WARNING)
        else:
            if not fail:
                st.success(msg["safe_water"])
            else:
                st.error(msg["unsafe_water"])
                for f in fail:
                    st.write(f"- {f}: {HEALTH_ADVICE.get(f, 'Check for local contaminants and avoid raw consumption.')}")
                st.info(GENERAL_HEALTH_WARNING)
        csv = pd.DataFrame(table).to_csv(index=False).encode('utf-8')
        st.download_button(
            label=msg["download"],
            data=csv,
            file_name=f"JalMitr_Report_{datetime.date.today()}.csv",
            mime='text/csv'
        )

# --------------------- Dummy Module Placeholders ---------------------
def plant_operations_module():
    st.button("⬅️ Back", on_click=lambda: go_to(Page.HOME))
    st.header("🏭 Plant Operations")
    st.info("Coming soon: Logging, performance & AI help.")

def wash_module():
    st.button("⬅️ Back", on_click=lambda: go_to(Page.HOME))
    st.header("🧼 WASH - Water, Sanitation, Hygiene")
    st.info("Coming soon: Hygiene guides and AI help.")

def disaster_response_module():
    st.button("⬅️ Back", on_click=lambda: go_to(Page.HOME))
    st.title("🚨 Disaster Response")
    st.info("Coming soon: Disaster water help.")

def q_box_module():
    st.button("⬅️ Back", on_click=lambda: go_to(Page.HOME))
    st.title("🤖 Water AI Chatbot")
    st.info("Coming soon: AI Water Q&A.")

def jjm_insights_module():
    st.button("⬅️ Back", on_click=lambda: go_to(Page.HOME))
    st.title("🇮🇳 JJM Insights")
    st.info("Coming soon: Jal Jeevan Mission guides.")

def analytics_module():
    st.button("⬅️ Back", on_click=lambda: go_to(Page.HOME))
    st.title("📊 Data Analytics")
    st.info("Coming soon: Uploads, trends, graphs.")

def feedback_module():
    st.button("⬅️ Back", on_click=lambda: go_to(Page.HOME))
    st.title("📝 Feedback")
    st.info("Coming soon: Feedback/contact form.")

# ------------------------- Main Router -------------------------
if st.session_state.page == Page.HOME:
    home_page()
elif st.session_state.page == Page.SAFE_WATER:
    safe_water_module()
elif st.session_state.page == Page.PLANT_OPERATIONS:
    plant_operations_module()
elif st.session_state.page == Page.WASH:
    wash_module()
elif st.session_state.page == Page.DISASTER:
    disaster_response_module()
elif st.session_state.page == Page.Q_BOX:
    q_box_module()
elif st.session_state.page == Page.JJM_INSIGHTS:
    jjm_insights_module()
elif st.session_state.page == Page.ANALYTICS:
    analytics_module()
elif st.session_state.page == Page.FEEDBACK:
    feedback_module()

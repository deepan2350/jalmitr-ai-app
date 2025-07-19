import streamlit as st
import pandas as pd
import os

# ------------ Language Block --------------
LANGS = {
    "en": {
        "select_lang":"Select Language", "pin_label":"Enter Pincode (Required):", "pin_not_found":"Pincode not found!",  "district":"District",  "state":"State",  "office":"Office",
        "sample_type":"Sample Type", "params_entry":"Water Parameter Entry", "predict_btn":"Predict", "prediction_result":"Prediction Result",  "pass":"✔️ Pass", "fail":"❌ Fail", "not_entered":"Not Entered",
        "fill_warn":"Please fill at least {n} parameters (including TDS).", "tds_req":"TDS value is compulsory.", "safe_water":"Water quality is SAFE as per standards.",
        "unsafe_water":"Water is NOT SAFE! See details below.", "advice_heading":"Advice", "stp_ok":"STP is functioning properly; water is safe.", "stp_not_ok":"STP is NOT functioning properly; maintenance needed."
    },
    "hi": {
        "select_lang":"भाषा चुनें", "pin_label":"पिनकोड दर्ज करें (आवश्यक):", "pin_not_found":"पिनकोड नहीं मिला!",  "district":"जिला",  "state":"राज्य",  "office":"कार्यालय",
        "sample_type":"सैम्पल का प्रकार", "params_entry":"जल गुणवत्ता पैरामीटर दर्ज करें", "predict_btn":"जांचें", "prediction_result":"परिणाम",
        "pass":"✔️ पास", "fail":"❌ असफल", "not_entered":"पूरा नहीं", "fill_warn":"कम से कम {n} पैरामीटर (TDS सहित) भरें।", "tds_req":"TDS आवश्यक है।",
        "safe_water":"जल गुणवत्ता मानकों के अनुसार सुरक्षित है।", "unsafe_water":"जल सुरक्षित नहीं! विवरण देखें।", "advice_heading":"सलाह", "stp_ok":"एसटीपी मानकों पे है; पानी सुरक्षित है।", "stp_not_ok":"एसटीपी ठीक नहीं चल रहा, सुधार आवश्यक।"
    },
    "hi_en": {
        "select_lang":"Language choose karo", "pin_label":"Pincode (Zaruri):", "pin_not_found":"Data me pincode nahi!",  "district":"District",  "state":"State",  "office":"Office",
        "sample_type":"Sample Type", "params_entry":"Water ka parameter daalein", "predict_btn":"Predict karo", "prediction_result":"Result", "pass":"✔️ Pass", "fail":"❌ Fail", "not_entered":"Nahi bhara",
        "fill_warn":"{n} parameter TDS samet bharo.", "tds_req":"TDS jaruri hai.", "safe_water":"Pani safe hai standard ke hisab se.", "unsafe_water":"Pani safe nahi! Niche dekhein.", "advice_heading":"Advice", "stp_ok":"STP sahi hai; pani safe hai.", "stp_not_ok":"STP problem, maintenance karo."
    }
}

ALL_PARAMS = [
    "pH", "Conductivity", "DO", "BOD", "COD", "TDS", "Total Hardness", "Total Alkalinity", "Nitrate", "Fluoride",
    "Ammonia", "Sulphate", "Iron", "Fecal Coliform", "Total Coliform", "Turbidity", "Calcium", "Chloride",
    "Carbonate", "Magnesium", "Calcium hardness", "Bicarbonate", "Potassium", "Sodium", "Magnesium hardness",
    "Total Suspended Solids", "Total Organic Carbon", "Zinc", "Arsenic", "Odour", "Lead"
]
STP_PARAMS = [
    "pH", "BOD", "COD", "Turbidity", "Ammonia", "Nitrate", "Fecal Coliform", "Chloride", "Iron", "TDS", "Total Alkalinity"
]

PARAMS_LIMITS = {
    "pH": (0.0,14.0,(6.5,8.5)), "Conductivity": (0.0,5000.0,2000.0), "DO": (0.0,14.0,5.0), "BOD": (0.0,100.0,10.0), "COD": (0.0,500.0,50.0),
    "TDS": (0.0,5000.0,2000.0), "Total Hardness": (0.0,2000.0,200.0), "Total Alkalinity": (0.0,600.0,200.0), "Nitrate": (0.0,100.0,10.0),
    "Fluoride": (0.0,5.0,1.0), "Ammonia": (0.0,10.0,5.0), "Sulphate": (0.0,1000.0,200.0), "Iron": (0.0,10.0,0.3), "Fecal Coliform": (0.0,10000.0,1000.0),
    "Total Coliform": (0.0,10000.0,1000.0), "Turbidity": (0.0,100.0,2.0), "Calcium": (0.0,200.0,75.0), "Chloride": (0.0,1500.0,250.0),
    "Carbonate": (0.0,500.0,200.0), "Magnesium": (0.0,150.0,30.0), "Calcium hardness": (0.0,500.0,75.0), "Bicarbonate": (0.0,500.0,200.0),
    "Potassium": (0.0,50.0,10.0), "Sodium": (0.0,200.0,50.0), "Magnesium hardness": (0.0,200.0,30.0), "Total Suspended Solids": (0.0,1000.0,20.0),
    "Total Organic Carbon": (0.0,50.0,2.0), "Zinc": (0.0,15.0,5.0), "Arsenic": (0.0,0.05,0.01), "Odour": (0.0,1.0,0.0), "Lead": (0.0,1.0,0.01)
}

def get_csv_path(fname):
    if os.path.exists(fname): return fname
    if os.path.exists(f"data/{fname}"): return f"data/{fname}"
    return None

@st.cache_data
def load_pincode_df():
    path = get_csv_path("pincode.csv")
    if not path:
        st.error("pincode.csv missing! Put in root or data/ folder.")
        return pd.DataFrame()
    df = pd.read_csv(path)
    df['pincode'] = df['pincode'].astype(str)
    return df

# ---------------- UI LOGIC -----------------
st.set_page_config(page_title="JalMitr Water AI", page_icon="💧")
st.title("💧 JalMitr – Water AI")

lang_code = st.selectbox("🌐 "+LANGS['en']["select_lang"], ["en", "hi", "hi_en"], format_func=lambda x: {'en':"English",'hi':"हिन्दी",'hi_en':"Hinglish"}[x])
msg = LANGS[lang_code]

# Inputs
pincode = st.text_input(msg['pin_label'], key='pin')
stype = st.selectbox(msg['sample_type'], ["GROUND", "RIVER", "TAP", "RO", "STP"], key="stype")

# Auto-reset fields on pincode/sample type change
if 'old_pin' not in st.session_state: st.session_state['old_pin'] = ''
if 'old_stype' not in st.session_state: st.session_state['old_stype'] = ''
if pincode != st.session_state['old_pin'] or stype != st.session_state['old_stype']:
    for p in set(ALL_PARAMS + STP_PARAMS):
        st.session_state[f"param_{p}"] = None
    st.session_state['old_pin'] = pincode
    st.session_state['old_stype'] = stype

# Pincode info
pincode_df = load_pincode_df()
if not pincode:
    st.info(msg['pin_label'])
    st.stop()
row = pincode_df[pincode_df['pincode'] == pincode]
if row.empty:
    st.error(msg['pin_not_found'])
    st.stop()
else:
    d, state, office = row.iloc[0]['district'], row.iloc[0]['statename'], row.iloc[0]['officename']
    st.success(f"{msg['district']}: {d} | {msg['state']}: {state} | {msg['office']}: {office}")

# Dynamic form
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
    key = f"param_{pname}"
    with param_cols[idx % 4]:
        vals[pname] = st.number_input(
            pname,
            min_value=minv, max_value=maxv,
            value=defval if defval not in (None,"") else None,
            step=mv,
            key=key,
            format="%.3f" if dtype_float else "%d"
        )

# Prediction/report
if st.button(msg["predict_btn"]):
    filled = [v for v in vals.values() if v not in (None,0,"")]
    tds_ok = True if stype == "STP" else (vals.get("TDS", 0) not in (None,0,""))
    if not tds_ok:
        st.error(msg['tds_req'])
        st.stop()
    if len(filled) < min_params:
        st.warning(msg['fill_warn'].format(n=min_params))
        st.stop()
    st.success(msg["prediction_result"])
    table, fail = [], []
    for pname in params:
        val = vals[pname]
        l, u, std = PARAMS_LIMITS.get(pname, (0.0,1000.0,0.0))
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
            if status in (msg["fail"], "❌ Fail", "❌ असफल", "Fail"):
                fail.append(pname)
        table.append({'Parameter': pname, 'Value': sval, 'Standard': slimit, 'Status': status})
    st.table(pd.DataFrame(table))
    st.header(msg["advice_heading"])
    if stype == "STP":
        if not fail: st.success(msg["stp_ok"])
        else:
            st.error(msg["stp_not_ok"] + ": " + ", ".join(fail))
            for f in fail:
                if f == "BOD": st.write("- Check aeration, microbial dosing.")
                if f == "COD": st.write("- Boost oxidation, remove sludge.")
                if f == "Turbidity": st.write("- Clean filters and clarify tanks.")
                if f == "Fecal Coliform": st.write("- Dose more disinfectant.")
                if f == "Ammonia": st.write("- Nitrification/aeration improvement.")
                if f == "pH": st.write("- pH control, acid/alkali dosing.")
    else:
        if not fail: st.success(msg["safe_water"])
        else:
            st.error(msg["unsafe_water"])
            for f in fail:
                if f == "TDS": st.write("- Use RO filter for drinking.")
                if f == "Iron": st.write("- Use iron-removal filter.")
                if f == "Ammonia": st.write("- Check contamination, aerate water.")
                if f == "Nitrate": st.write("- Avoid for infants, prefer RO.")
                if f == "Fluoride": st.write("- Nalgonda/RO filter.")
                if f == "Lead": st.write("- Change old pipe, use RO+carbon.")

# --------- END -------------

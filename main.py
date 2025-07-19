import streamlit as st
import pandas as pd
import os
import datetime

# --------- LANGUAGE DICTIONARY -----------------
LANGS = {
    "en": { "select_lang":"Select Language", "pin_label":"Enter Pincode (Required):", "pin_not_found":"Pincode not found!",  "district":"District",  "state":"State",  "office":"Office", "sample_type":"Sample Type", "params_entry":"Water Parameter Entry", "predict_btn":"Predict", "prediction_result":"Prediction Result",  "pass":"✔️ Pass", "fail":"❌ Fail", "not_entered":"Not Entered",  "fill_warn":"Please fill at least {n} parameters (including TDS).", "tds_req":"TDS value is compulsory.", "safe_water":"Water quality is SAFE as per standards.", "unsafe_water":"Water is NOT SAFE! See details below.", "advice_heading":"Advice", "stp_ok":"STP is functioning properly; water is safe.", "stp_not_ok":"STP is NOT functioning properly; maintenance needed." },
    "hi": { "select_lang":"भाषा चुनें", "pin_label":"पिनकोड दर्ज करें (आवश्यक):", "pin_not_found":"पिनकोड नहीं मिला!",  "district":"जिला",  "state":"राज्य",  "office":"कार्यालय", "sample_type":"सैम्पल का प्रकार", "params_entry":"जल गुणवत्ता पैरामीटर दर्ज करें", "predict_btn":"जांचें", "prediction_result":"परिणाम", "pass":"✔️ पास", "fail":"❌ असफल", "not_entered":"पूरा नहीं", "fill_warn":"कम से कम {n} पैरामीटर (TDS सहित) भरें।", "tds_req":"TDS आवश्यक है।", "safe_water":"जल गुणवत्ता मानकों के अनुसार सुरक्षित है।", "unsafe_water":"जल सुरक्षित नहीं! विवरण देखें।", "advice_heading":"सलाह", "stp_ok":"एसटीपी मानकों पे है; पानी सुरक्षित है।", "stp_not_ok":"एसटीपी ठीक नहीं चल रहा, सुधार आवश्यक।" },
    "hi_en": { "select_lang":"Language choose karo", "pin_label":"Pincode (Zaruri):", "pin_not_found":"Data me pincode nahi!",  "district":"District",  "state":"State",  "office":"Office", "sample_type":"Sample Type", "params_entry":"Water ka parameter daalein", "predict_btn":"Predict karo", "prediction_result":"Result", "pass":"✔️ Pass", "fail":"❌ Fail", "not_entered":"Nahi bhara", "fill_warn":"{n} parameter TDS samet bharo.", "tds_req":"TDS jaruri hai.", "safe_water":"Pani safe hai standard ke hisab se.", "unsafe_water":"Pani safe nahi! Niche dekhein.", "advice_heading":"Advice", "stp_ok":"STP sahi hai; pani safe hai.", "stp_not_ok":"STP problem, maintenance karo." }
}

ALL_PARAMS = ["pH", "Conductivity", "DO", "BOD", "COD", "TDS", "Total Hardness", "total Alkalinity", "Nitrate", "Fluoride", "Ammonia", "Sulphate", "Iron", "Fecal Coliform", "Total Coliform", "Turbidity", "Calcium", "Chloride", "Carbonate", "Magnesium", "Calcium Hardness", "Bicarbonate", "Potassium", "Sodium", "Magnesium Hardness", "Total Suspended Solids", "Total Organic Carbon", "Zinc", "Arsenic", "Odour", "Lead"]
STP_PARAMS = ["pH", "BOD", "COD", "Turbidity", "Ammonia", "Nitrate", "Fecal Coliform", "Chloride", "Iron", "TDS", "total Alkalinity"]

PARAMS_LIMITS = {
    "pH": (0,14,(6.5,8.5)), "Conductivity": (0,5000,2000), "DO": (0,14,5), "BOD": (0,100,10), "COD": (0,500,50),
    "TDS": (0,5000,2000), "Total Hardness": (0,2000,200), "total Alkalinity": (0,600,200), "Nitrate": (0,100,10),
    "Fluoride": (0,5,1), "Ammonia": (0,10,5), "Sulphate": (0,1000,200), "Iron": (0,10,0.3), "Fecal Coliform": (0,10000,1000),
    "Total Coliform": (0,10000,1000), "Turbidity": (0,100,2), "Calcium": (0,200,75), "Chloride": (0,1500,250),
    "Carbonate": (0,500,200), "Magnesium": (0,150,30), "Calcium Hardness": (0,500,75), "Bicarbonate": (0,500,200),
    "Potassium": (0,50,10), "Sodium": (0,200,50), "Magnesium Hardness": (0,200,30), "Total Suspended Solids": (0,1000,20),
    "Total Organic Carbon": (0,50,2), "Zinc": (0,15,5), "Arsenic": (0,0.05,0.01), "Odour": (0,1,0), "Lead": (0,1,0.01)
}

# ------------- FLEXIBLE FILE LOADER ---------------
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

# ------------- UI START -------------
st.set_page_config(page_title="JalMitr Water AI", page_icon="💧")
st.title("💧 JalMitR – Water Quality AI")

lang_code = st.selectbox("🌐 "+LANGS['en']["select_lang"], ["en", "hi", "hi_en"], format_func=lambda x: {"en":"English","hi":"हिंदी","hi_en":"Hinglish"}[x])
msg = LANGS[lang_code]

# --- User input for pincode and sample ---
pincode = st.text_input(msg['pin_label'], key='pin')
stype = st.selectbox(msg['sample_type'], ["GROUND", "RIVER", "TAP", "RO", "STP"], key="stype")

# --- Reset on change ---
if 'old_pin' not in st.session_state: st.session_state['old_pin'] = ''
if 'old_stype' not in st.session_state: st.session_state['old_stype'] = ''
if pincode != st.session_state['old_pin'] or stype != st.session_state['old_stype']:
    for p in set(ALL_PARAMS + STP_PARAMS):
        st.session_state[f"param_{p}"] = 0
    st.session_state['old_pin'] = pincode
    st.session_state['old_stype'] = stype

# --- PINCODE Lookup & Info ---
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

# --- Parameter Entry Form ---
params = STP_PARAMS if stype == "STP" else ALL_PARAMS
min_params = 3 if stype == "STP" else 5
st.header(msg['params_entry'])
vals = {}
param_cols = st.columns(4)
for idx, pname in enumerate(params):
    l, u, std = PARAMS_LIMITS.get(pname, (0, 1000, 0))
    with param_cols[idx % 4]:
        vals[pname] = st.number_input(pname, min_value=l, max_value=u, value=st.session_state.get(f"param_{pname}", 0), key=f"param_{pname}")

# --- Predict & Report ---
if st.button(msg["predict_btn"]):
    filled = [v for v in vals.values() if v not in (None, 0, "")]
    tds_ok = True if stype == "STP" else (vals.get("TDS", 0) != 0)
    if not tds_ok:
        st.error(msg['tds_req'])
        st.stop()
    if len(filled) < min_params:
        st.warning(msg['fill_warn'].format(n=min_params))
        st.stop()
    st.success(msg["prediction_result"])
    table = []
    for pname in params:
        val = vals[pname]
        l, u, std = PARAMS_LIMITS.get(pname, (0, 1000, 0))
        if val in (None, 0, ""):
            status, sval, slimit = msg["not_entered"], "--", f"{std[0]}–{std[1]}" if isinstance(std,tuple) else f"≤{std}"
        else:
            sval = val
            if pname == "pH" and isinstance(std, tuple):
                status, slimit = (msg["pass"], f"{std[0]}–{std[1]}") if std[0] <= val <= std[1] else (msg["fail"], f"{std[0]}–{std[1]}")
            else:
                status = msg["pass"] if val <= std else msg["fail"]
                slimit = f"≤{std}"
        table.append({'Parameter': pname, 'Value': sval, 'Standard': slimit, 'Status': status})
    st.table(pd.DataFrame(table))
    fail = [r['Parameter'] for r in table if r['Status'].startswith("❌") or r['Status'].startswith("असफल") or r['Status'].startswith("Fail")]
    st.header(msg["advice_heading"])
    if stype == "STP":
        if not fail:
            st.success(msg["stp_ok"])
        else:
            st.error(msg["stp_not_ok"] + ": " + ", ".join(fail))
            for f in fail:
                if f == "BOD": st.write("- Check aeration, microbial dosing.")
                if f == "COD": st.write("- Boost oxidation, remove sludge.")
                if f == "Turbidity": st.write("- Clean filters and clarify tanks.")
                if f == "Fecal Coliform": st.write("- Improve disinfection, check chlorine dose.")
                if f == "Ammonia": st.write("- Enhance nitrification and aeration.")
                if f == "pH": st.write("- Adjust chemical dosing for pH balance.")
    else:
        if not fail:
            st.success(msg["safe_water"])
        else:
            st.error(msg["unsafe_water"])
            for f in fail:
                if f == "TDS": st.write("- Use RO purifier for drinking.")
                if f == "Iron": st.write("- Use iron removal filters.")
                if f == "Ammonia": st.write("- Check contamination, aerate water.")
                if f == "Nitrate": st.write("- Avoid for infants, use RO filter.")
                if f == "Fluoride": st.write("- Use defluoridation/RO methods.")
                if f == "Lead": st.write("- Replace pipes, use carbon filter.")

# --- End Main ---

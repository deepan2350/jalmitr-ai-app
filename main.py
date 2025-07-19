import streamlit as st
import pandas as pd
import os
import datetime

# ----------- Language & Advice Dicts -----------
LANGS = {
    "en": {
        "select_lang": "Select Language",
        "pin_label": "Enter Pincode (Required):",
        "pin_not_found": "Pincode not found in records!",
        "district": "District", "state": "State", "office": "Office",
        "sample_type": "Sample Type",
        "params_entry": "Enter Water Parameters",
        "predict_btn": "Predict",
        "prediction_result": "Prediction Result",
        "pass": "✔️ Pass", "fail": "❌ Fail", "not_entered": "Not Entered",
        "fill_warn": "Please fill at least {n} parameters (including TDS).",
        "tds_req": "TDS is compulsory for this sample type.",
        "safe_water": "Water is SAFE as per standards.",
        "unsafe_water": "Water is NOT SAFE! Don't consume untreated.",
        "advice_heading": "Advice / Health Warning",
        "stp_ok": "STP is functioning properly; water is safe.",
        "stp_not_ok": "STP is NOT functioning properly. Fix immediately.",
        "download": "Download Report CSV"
    },
    "hi_en": {
        "select_lang": "Language/Soochna Chuno",
        "pin_label": "Pincode Daalen (Jaruri):",
        "pin_not_found": "Pincode data me nahi mila!",
        "district": "District", "state": "State", "office": "Office",
        "sample_type": "Sample Type",
        "params_entry": "Paanee ke parameter bharen",
        "predict_btn": "Predict Karo",
        "prediction_result": "Prediction Ka Result",
        "pass": "✔️ Pass", "fail": "❌ Fail", "not_entered": "Nahi Bhara",
        "fill_warn": "{n} parameter (TDS ke saath) zaruri hain.",
        "tds_req": "TDS bharna compulsory hai.",
        "safe_water": "Standard ke hisaab se paani safe hai.",
        "unsafe_water": "Paani safe nahi! Bina treatment ke na piyein.",
        "advice_heading": "Advice / Health Salah",
        "stp_ok": "STP sahi se chal raha hai.",
        "stp_not_ok": "STP mein dikkat hai, turant sudhaaren.",
        "download": "Report Download Karo"
    },
    "hi": {
        "select_lang": "भाषा चुनें",
        "pin_label": "पिनकोड डालें (आवश्यक):",
        "pin_not_found": "पिनकोड रिकॉर्ड में नहीं मिला!",
        "district": "जनपद", "state": "राज्य", "office": "कार्यालय",
        "sample_type": "सैम्पल का प्रकार",
        "params_entry": "जल पैरामीटर भरें",
        "predict_btn": "जांचें",
        "prediction_result": "परिणाम",
        "pass": "✔️ पास", "fail": "❌ असफल", "not_entered": "नहीं भरा",
        "fill_warn": "कम से कम {n} पैरामीटर (TDS सहित) भरें।",
        "tds_req": "TDS आवश्यक है।",
        "safe_water": "पानी मानकों के अनुसार सुरक्षित है।",
        "unsafe_water": "पानी सुरक्षित नहीं! उपचार के बिना ना पिएं।",
        "advice_heading": "सलाह / स्वास्थ्य चेतावनी",
        "stp_ok": "STP सही से काम कर रहा है।",
        "stp_not_ok": "STP सही नहीं, तुरंत सुधारें।",
        "download": "सीएसवी डाउनलोड करें"
    }
}

HEALTH_ADVICE = {
    "TDS": "High TDS can cause kidney stress, digestive issues — especially risky for infants/elders.",
    "Iron": "Too much iron may cause hemochromatosis/liver issues.",
    "Fluoride": "High fluoride may cause dental/skeletal fluorosis.",
    "Nitrate": "High nitrate is risky for infants (blue baby syndrome/methemoglobinemia).",
    "Lead": "Lead is highly toxic, damages nerves, slows child brain growth.",
    "Ammonia": "Ammonia is toxic; causes nausea, problems for kidney/liver.",
    "Arsenic": "Carcinogenic, leads to organ/tissue damage.",
    "Chloride": "Too much chloride — salty taste, possible dehydration.",
    "Sulphate": "Causes diarrhea/laxative effect, especially in kids.",
    "Fecal Coliform": "Fecal coliforms mean risk of diarrhea, dysentery, typhoid.",
    "Total Coliform": "High risk of microbial borne disease (cholera etc).",
    "Turbidity": "Turbid water may hide infection/pathogen risk.",
    "pH": "Very low or high pH may corrode pipes, cause stomach upset."
}
GENERAL_HEALTH_WARNING = "If any parameter FAILS: Boil or filter water before use. Consult water safety experts. For infants/pregnant/ill, strict care needed!"

# ---------- Parameter Configs ----------
ALL_PARAMS = ["pH","Conductivity","DO","BOD","COD","TDS","Total Hardness","Total Alkalinity","Nitrate","Fluoride","Ammonia","Sulphate","Iron","Fecal Coliform","Total Coliform","Turbidity","Calcium","Chloride","Carbonate","Magnesium","Calcium hardness","Bicarbonate","Potassium","Sodium","Magnesium hardness","Total Suspended Solids","Total Organic Carbon","Zinc","Arsenic","Odour","Lead"]
STP_PARAMS = ["pH","BOD","COD","Turbidity","Ammonia","Nitrate","Fecal Coliform","Chloride","Iron","TDS","Total Alkalinity"]
PARAMS_LIMITS = {
    "pH": (0.0,14.0,(6.5,8.5)), "Conductivity":(0.0,5000.0,2000.0), "DO":(0.0,14.0,5.0), "BOD":(0.0,100.0,10.0), "COD":(0.0,500.0,50.0), "TDS": (0.0,5000.0,2000.0), "Total Hardness":(0.0,2000.0,200.0), "Total Alkalinity":(0.0,600.0,200.0), "Nitrate":(0.0,100.0,10.0), "Fluoride":(0.0,5.0,1.0), "Ammonia":(0.0,10.0,5.0), "Sulphate":(0.0,1000.0,200.0), "Iron":(0.0,10.0,0.3), "Fecal Coliform":(0.0,10000.0,1000.0), "Total Coliform":(0.0,10000.0,1000.0), "Turbidity":(0.0,100.0,2.0), "Calcium":(0.0,200.0,75.0), "Chloride":(0.0,1500.0,250.0), "Carbonate":(0.0,500.0,200.0), "Magnesium":(0.0,150.0,30.0), "Calcium hardness":(0.0,500.0,75.0), "Bicarbonate":(0.0,500.0,200.0), "Potassium":(0.0,50.0,10.0), "Sodium":(0.0,200.0,50.0), "Magnesium hardness":(0.0,200.0,30.0), "Total Suspended Solids":(0.0,1000.0,20.0), "Total Organic Carbon":(0.0,50.0,2.0), "Zinc":(0.0,15.0,5.0), "Arsenic":(0.0,0.05,0.01), "Odour":(0.0,1.0,0.0), "Lead":(0.0,1.0,0.01)
}

# -------- Flexible File Path Loader -----------
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

# --------- UI & LOGIC STARTS ----------
st.set_page_config(page_title="JalMitr Water AI", page_icon="💧")
st.title("💧 JalMitr – Water Quality AI")

lang_code = st.selectbox("🌐 "+LANGS['en']["select_lang"], ["en", "hi_en", "hi"], format_func=lambda x: {"en":"English","hi_en":"Hinglish","hi":"हिन्दी"}[x])
msg = LANGS[lang_code]

pincode = st.text_input(msg['pin_label'], key='pin')
stype = st.selectbox(msg['sample_type'], ["GROUND","RIVER","TAP","RO","STP"], key="stype")

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
    # Download option
    csv = pd.DataFrame(table).to_csv(index=False).encode('utf-8')
    st.download_button(label=msg["download"], data=csv, file_name=f"JalMitr_Report_{datetime.date.today()}.csv", mime='text/csv')

import streamlit as st
import pandas as pd

st.set_page_config(page_title="💧 JalMitr – Water AI App", page_icon="💧")
st.title("💧 JalMitr – Water AI App")

# ---------- 1. Language Dictionary ----------
LANG_DICT = {
    'en': {
        "select_language": "Select Language",
        "pincode_label": "Pincode (Required):",
        "pincode_not_found": "Pincode not found in file!",
        "district": "District",
        "state": "State",
        "office": "Office",
        "type_of_sample": "Type of Sample:",
        "parameter_entry": "Water Test Parameters Entry",
        "prediction_result": "Prediction Result:",
        "pass": "✔️ Pass",
        "fail": "❌ Fail",
        "not_entered": "Not Entered",
        "fill_more": "Please fill at least {n} parameters for prediction.",
        "tds_required": "TDS value is compulsory!",
        "safe": "All parameters are within safe limits. Water is SAFE.",
        "unsafe": "Unsafe: values out of standard.",
        "advice_title": "Advice:",
        "stp_success": "Your STP/ETP water is within CPCB limits. Plant is functioning well; water can be reused for non-potable purposes.",
        "stp_problem": "STP/ETP Problems found: ",
        "general_advice": "General Water Advice:",
    },
    'hi': {
        "select_language": "भाषा चुनें",
        "pincode_label": "पिनकोड (आवश्यक):",
        "pincode_not_found": "फाइल में पिनकोड नहीं मिला!",
        "district": "जनपद",
        "state": "राज्य",
        "office": "डाकघर",
        "type_of_sample": "नमूने का प्रकार:",
        "parameter_entry": "पानी के परीक्षण पैरामीटर",
        "prediction_result": "परिणाम:",
        "pass": "✔️ पास",
        "fail": "❌ फेल",
        "not_entered": "डाला नहीं गया",
        "fill_more": "कृपया भविष्यवाणी के लिए कम से कम {n} पैरामीटर भरें।",
        "tds_required": "टीडीएस मान अनिवार्य है!",
        "safe": "सारे मानक सही हैं। पानी सुरिक्षत है।",
        "unsafe": "असुरक्षित: मानक से बाहर मान।",
        "advice_title": "सलाह:",
        "stp_success": "आपका एसटीपी/ईटीपी पानी CPCB सीमाओं के भीतर है। संयंत्र ठीक से काम कर रहा है; पानी का पुन: उपयोग किया जा सकता है।",
        "stp_problem": "एसटीपी/ईटीपी में समस्या: ",
        "general_advice": "सामान्य पानी की सलाह:",
    },
    'hi_en': {
        "select_language": "Language / भाषा आप चुनो",
        "pincode_label": "Pincode (Required):",
        "pincode_not_found": "Pincode file me nahi mila!",
        "district": "District",
        "state": "State",
        "office": "Office",
        "type_of_sample": "Type of Sample:",
        "parameter_entry": "Water Test Parameters Entry",
        "prediction_result": "Result:",
        "pass": "✔️ Pass (ठीक)",
        "fail": "❌ Fail (गलत)",
        "not_entered": "नहीं डाला गया",
        "fill_more": "कम से कम {n} parameter भरो।",
        "tds_required": "TDS value compulsory hai!",
        "safe": "Saare parameters safe hain! Paani surakshit hai.",
        "unsafe": "Unsafe: Kayi values limit se bahar.",
        "advice_title": "Advice / समाधान:",
        "stp_success": "Aapka STP/ETP paani limit me hai. Plant sahi hai; isse reuse kar sakte hain.",
        "stp_problem": "STP/ETP mein problem: ",
        "general_advice": "Paani ki general advice:",
    }
}

# -------- FULL Parameter Lists FIRST (order important!) ---------
all_params = [
    "pH", "Conductivity", "DO", "BOD", "COD", "TDS", "Total Hardness", "Total Alkalinity", "Nitrate",
    "Fluoride", "Ammonia", "Sulphate", "Iron", "Fecal Coliform", "Total Coliform", "Turbidity", "Calcium",
    "Chloride", "Carbonate", "Magnesium", "Calcium hardness", "Bicarbonate", "Potassium", "Sodium",
    "Magnesium hardness", "Total Suspended Solids", "Total Organic Carbon", "Zinc", "Arsenic", "Odour", "Lead"
]
stp_params = [
    "pH", "BOD", "COD", "Turbidity", "Ammonia", "Nitrate", "Fecal Coliform", "Chlorine", "TDS",
    "Total Alkalinity", "Chloride"
]

# -------- RESET/REACT Function --------
def reset_param_state(param_list):
    for pname in param_list:
        k = f"param_{pname}"
        if k in st.session_state:
            st.session_state[k] = None

def reset_if_changed():
    if "old_pincode" not in st.session_state:
        st.session_state["old_pincode"] = ""
    if "old_sample_type" not in st.session_state:
        st.session_state["old_sample_type"] = ""
    if (
        st.session_state.get("old_pincode") != st.session_state.get("curr_pincode") or
        st.session_state.get("old_sample_type") != st.session_state.get("curr_sample_type")
    ):
        reset_param_state(all_params + stp_params)
        st.session_state["old_pincode"] = st.session_state.get("curr_pincode")
        st.session_state["old_sample_type"] = st.session_state.get("curr_sample_type")

# -------------- UI Starts -------------

# 1. Language
languages = [
    ("English", "en"),
    ("हिंदी", "hi"),
    ("Hinglish", "hi_en")
]
lang_label, lang_code = st.selectbox(
    LANG_DICT['en']["select_language"] + " / " + LANG_DICT['hi']["select_language"], languages, format_func=lambda x: x[0]
)
msg = LANG_DICT[lang_code]

# 2. Pincode Entry (+ Auto-Reset)
st.text_input(msg["pincode_label"], key="curr_pincode")
# 3. Type of Sample (+ Auto-Reset)
sample_types = [
    "GROUND WATER", "RIVER WATER", "TAP WATER", "RO WATER", "STP/ETP"
]
st.selectbox(msg["type_of_sample"], sample_types, key="curr_sample_type")
reset_if_changed()
pincode = st.session_state.get("curr_pincode", "")
sample_type = st.session_state.get("curr_sample_type", sample_types[0])

# 4. Pincode Lookup
@st.cache_data
def load_pincode_data():
    df = pd.read_csv('data/pincode.csv')
    df["pincode"] = df["pincode"].astype(str)
    return df
pincode_df = load_pincode_data()
district, state, office = None, None, None
if not pincode:
    st.info(msg["pincode_label"])
    st.stop()
row = pincode_df[pincode_df["pincode"] == str(pincode).strip()]
if len(row) > 0:
    district, state, office = (
        row.iloc[0].get("district", ""),
        row.iloc[0].get("statename", ""),
        row.iloc[0].get("officename", ""),
    )
    st.success(
        f"**{pincode}**\n- {msg['district']}: {district}\n- {msg['state']}: {state}\n- {msg['office']}: {office}"
    )
else:
    st.error(msg["pincode_not_found"])

# 5. Parameters Dictionary (no change needed in structure)
params_limits = {
    "pH": (0.0, 14.0, (6.5, 8.5)),
    "Conductivity": (0.0, 5000.0, 2000.0),
    "DO": (0.0, 14.0, 5.0),
    "BOD": (0.0, 100.0, 10.0),
    "COD": (0.0, 500.0, 50.0),
    "TDS": (0, 5000, 2000),
    "Total Hardness": (0, 2000, 200),
    "Total Alkalinity": (0, 600, 200),
    "Nitrate": (0.0, 100.0, 10.0),
    "Fluoride": (0.0, 5.0, 1.0),
    "Ammonia": (0.0, 10.0, 5.0),
    "Sulphate": (0.0, 1000.0, 200.0),
    "Iron": (0.0, 10.0, 0.3),
    "Fecal Coliform": (0, 10000, 1000),
    "Total Coliform": (0, 10000, 1000),
    "Turbidity": (0.0, 100.0, 2.0),
    "Calcium": (0.0, 200.0, 75.0),
    "Chloride": (0.0, 1500.0, 250.0),
    "Carbonate": (0.0, 500.0, 200.0),
    "Magnesium": (0.0, 150.0, 30.0),
    "Calcium hardness": (0.0, 500.0, 75.0),
    "Bicarbonate": (0.0, 500.0, 200.0),
    "Potassium": (0.0, 50.0, 10.0),
    "Sodium": (0.0, 200.0, 50.0),
    "Magnesium hardness": (0.0, 200.0, 30.0),
    "Total Suspended Solids": (0, 1000, 20),
    "Total Organic Carbon": (0.0, 50.0, 2.0),
    "Zinc": (0.0, 15.0, 5.0),
    "Arsenic": (0.0, 0.05, 0.01),
    "Odour": (0.0, 1.0, 0.0),
    "Lead": (0.0, 1.0, 0.01),
    "Chlorine": (0.0, 10.0, 1.0),
}

# 6. Input Fields (dynamic by sample_type)
if sample_type == "STP/ETP":
    selected_params = stp_params
    min_fields = 3
else:
    selected_params = all_params
    min_fields = 5

st.markdown("### " + msg["parameter_entry"])
values = {}
for pname in selected_params:
    llim, ulim, std = params_limits.get(pname, (0, 1000, 0))
    mv = 0.01 if isinstance(llim, float) else 1
    values[pname] = st.number_input(
        pname,
        min_value=llim, max_value=ulim,
        value=st.session_state.get(f"param_{pname}", None),
        step=mv,
        format="%.3f" if isinstance(llim, float) else "%d",
        key=f"param_{pname}"
    )

# 7. Predict + Advice/Reporting
if st.button("Predict Water Quality"):
    filled = [k for k, v in values.items() if v not in (None, "", 0, 0.0)]
    tds_filled = values.get("TDS", None) not in (None, "", 0, 0.0) if "TDS" in values else True
    if sample_type == "STP/ETP":
        if len(filled) < min_fields:
            st.warning(msg["fill_more"].format(n=min_fields))
            st.stop()
    else:
        if not tds_filled:
            st.error(msg["tds_required"])
            st.stop()
        if len(filled) < min_fields:
            st.warning(msg["fill_more"].format(n=min_fields))
            st.stop()
    st.success(msg["prediction_result"])

    report_rows = []
    for pname in selected_params:
        llim, ulim, std = params_limits.get(pname, (0, 1000, 0))
        v = values[pname]
        if v in (None, "", 0, 0.0):
            if pname == "pH" and isinstance(std, tuple):
                std_txt = f"{std[0]}–{std[1]}"
            else:
                std_txt = f"≤ {std}"
            report_rows.append({"Parameter": pname, "Your Value": "--", "Standard": std_txt, "Status": msg["not_entered"]})
        else:
            if pname == "pH" and isinstance(std, tuple):
                passfail = msg["pass"] if std[0] <= v <= std[1] else msg["fail"]
                std_txt = f"{std[0]}–{std[1]}"
            else:
                passfail = msg["pass"] if v <= std else msg["fail"]
                std_txt = f"≤ {std}"
            report_rows.append({"Parameter": pname, "Your Value": v, "Standard": std_txt, "Status": passfail})
    st.table(pd.DataFrame(report_rows))

    fail_list = [row["Parameter"] for row in report_rows if row["Status"].startswith("❌")]
    if sample_type == "STP/ETP":
        st.markdown("#### " + msg["advice_title"])
        if not fail_list:
            st.success(msg["stp_success"])
        else:
            st.error(msg["stp_problem"] + ", ".join(fail_list))
            for fail in fail_list:
                if fail == "BOD":
                    st.markdown("- BOD: Check aeration, microbial dosing, clarifier cleaning.")
                if fail == "COD":
                    st.markdown("- COD: Boost aeration, remove excess sludge.")
                if fail == "Turbidity":
                    st.markdown("- TSS/Turbidity: Clean/replace filter media, clarifyer maintenance.")
                if fail == "Fecal Coliform":
                    st.markdown("- Fecal Coliform: Improve chlorination/UV dosing, inspect dosing units.")
                if fail == "Ammonia":
                    st.markdown("- Ammonia: Enhance nitrification, check aeration.")
                if fail == "pH":
                    st.markdown("- pH abnormal: Adjust acid/alkali dosing, check neutralization units.")
            st.info("Plant operator training & maintenance required. Do not reuse/discharge until compliant.")
    else:
        st.markdown("#### " + msg["general_advice"])
        if not fail_list:
            st.success(msg["safe"])
        else:
            st.error(msg["unsafe"] + " " + ", ".join(fail_list))
            for fail in fail_list:
                if fail == "TDS":
                    st.markdown("- TDS High: Use RO purifier.")
                if fail == "Iron":
                    st.markdown("- Iron High: Install iron removal filter.")
                if fail == "Ammonia":
                    st.markdown("- Ammonia High: Check sewage; aerate source.")
                if fail == "Nitrate":
                    st.markdown("- Nitrate High: RO/ion exchange recommended, infants avoid.")
                if fail == "Fluoride":
                    st.markdown("- Fluoride High: Nalgonda/RO method for removal.")
                if fail == "Lead":
                    st.markdown("- Lead High: Replace pipes, use RO+carbon.")

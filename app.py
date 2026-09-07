import streamlit as st
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent

# =========================================================
# PROJECT RISK MONITORING DASHBOARD
# Streamlit + Random Forest + SHAP + Project Milestones
# =========================================================

st.set_page_config(
    page_title="Project Risk Monitoring Dashboard",
    page_icon="📊",
    layout="wide"
)

# -----------------------------
# FILE PATHS
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "Projects_Report(2).csv"
COST_MODEL_FILE = BASE_DIR / "cost_model(1).pkl"
DELAY_MODEL_FILE = BASE_DIR / "delay_model(1).pkl"


# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_FILE)

    # Fix the newline characters present in the original CSV headers
    df.columns = (
        df.columns
        .str.replace("\n", " ", regex=False)
        .str.strip()
    )

    # Convert dates
    date_cols = [
        "Original Date of Commissioning",
        "Revised Date of Commissioning",
        "Sanction Date"
    ]

    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    # Numeric columns
    numeric_cols = [
        "Original Cost (in cr.)",
        "Revised Cost (in cr.)",
        "Expenditure (in cr.)",
        "Physical Progress (in %)"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


# -----------------------------
# FEATURE ENGINEERING
# -----------------------------
def prepare_features(df):
    x = df.copy()

    # Planned duration is based on the original commissioning date.
    # Negative durations are replaced with 0, matching the preprocessing
    # used for the trained model.
    x["Planned Duration (days)"] = (
        x["Original Date of Commissioning"] - x["Sanction Date"]
    ).dt.days

    x["Planned Duration (days)"] = (
        x["Planned Duration (days)"]
        .replace([np.inf, -np.inf], np.nan)
        .fillna(0)
        .clip(lower=0)
    )

    # Cost base:
    # use revised cost when it is positive; otherwise use original cost.
    cost_base = x["Revised Cost (in cr.)"].where(
        x["Revised Cost (in cr.)"] > 0,
        x["Original Cost (in cr.)"]
    )

    cost_base = cost_base.replace([np.inf, -np.inf], np.nan)

    x["Expenditure Ratio (%)"] = np.where(
        cost_base > 0,
        (x["Expenditure (in cr.)"] / cost_base) * 100,
        0
    )

    x["Expenditure Ratio (%)"] = (
        pd.to_numeric(x["Expenditure Ratio (%)"], errors="coerce")
        .replace([np.inf, -np.inf], np.nan)
        .fillna(0)
    )

    x["Expenditure-Progress Gap (%)"] = (
        x["Expenditure Ratio (%)"] -
        x["Physical Progress (in %)"].fillna(0)
    )

    # Cost Base Anomaly:
    # the training data contained one extreme revised/original cost ratio.
    # Flag the same type of extreme ratio here.
    original = x["Original Cost (in cr.)"]
    revised = x["Revised Cost (in cr.)"]

    x["Cost Base Anomaly"] = (
        (original > 0) &
        (revised > 0) &
        ((revised / original) > 20)
    ).astype(int)

    # Keep exactly the features expected by the saved pipelines.
    prediction_features = [
        "Original Cost (in cr.)",
        "Expenditure (in cr.)",
        "Physical Progress (in %)",
        "Planned Duration (days)",
        "Expenditure Ratio (%)",
        "Expenditure-Progress Gap (%)",
        "Cost Base Anomaly",
        "Sector Name",
        "Line Ministry",
        "Implementing Agency"
    ]

    return x, prediction_features


# -----------------------------
# LOAD MODELS
# -----------------------------
@st.cache_resource
def load_models():
    cost_model = joblib.load(COST_MODEL_FILE)
    delay_model = joblib.load(DELAY_MODEL_FILE)
    return cost_model, delay_model


# -----------------------------
# SHAP
# -----------------------------
def clean_feature_name(name):
    name = str(name)

    if name.startswith("num__"):
        name = name.replace("num__", "", 1)

        replacements = {
            "Original Cost (in cr.)": "Original Cost",
            "Expenditure (in cr.)": "Expenditure",
            "Physical Progress (in %)": "Physical Progress",
            "Planned Duration (days)": "Planned Duration",
            "Expenditure Ratio (%)": "Expenditure Ratio",
            "Expenditure-Progress Gap (%)": "Expenditure-Progress Gap",
            "Cost Base Anomaly": "Cost Base Anomaly"
        }

        return replacements.get(name, name)

    if name.startswith("cat__"):
        name = name.replace("cat__", "", 1)

        # Convert "Sector Name_Roads & Highways"
        # into "Sector Name: Roads & Highways"
        categorical_columns = [
            "Sector Name",
            "Line Ministry",
            "Implementing Agency"
        ]

        for col in categorical_columns:
            prefix = col + "_"
            if name.startswith(prefix):
                return f"{col}: {name[len(prefix):]}"

    return name


def get_shap_explanation(model, input_df, top_n=5):
    try:
        import shap

        preprocessor = model.named_steps["preprocessor"]
        classifier = model.named_steps["classifier"]

        transformed = preprocessor.transform(input_df)

        # SHAP can fail if the transformed sparse/object matrix is not
        # explicitly converted to numeric values.
        transformed = np.asarray(
            transformed.toarray() if hasattr(transformed, "toarray") else transformed,
            dtype=np.float64
        )

        explainer = shap.TreeExplainer(classifier)
        shap_values = explainer.shap_values(transformed)

        # Different SHAP versions return different shapes.
        if isinstance(shap_values, list):
            values = shap_values[1][0]
        else:
            values = np.asarray(shap_values)

            if values.ndim == 3:
                values = values[0, :, 1]
            elif values.ndim == 2:
                values = values[0]
            else:
                values = values.flatten()

        feature_names = preprocessor.get_feature_names_out()

        explanation_df = pd.DataFrame({
            "Feature": [clean_feature_name(x) for x in feature_names],
            "SHAP Value": values
        })

        explanation_df["Absolute Impact"] = explanation_df["SHAP Value"].abs()
        explanation_df = explanation_df.sort_values(
            "Absolute Impact",
            ascending=False
        )

        risk_drivers = (
            explanation_df[explanation_df["SHAP Value"] > 0]
            .sort_values("SHAP Value", ascending=False)
            .head(top_n)
        )

        risk_reducing = (
            explanation_df[explanation_df["SHAP Value"] < 0]
            .sort_values("SHAP Value")
            .head(top_n)
        )

        return explanation_df, risk_drivers, risk_reducing

    except Exception as e:
        return None, None, None


# -----------------------------
# PREDICTION
# -----------------------------
def predict_project_risk(project, cost_model, delay_model):
    input_data = pd.DataFrame([project])

    cost_probability = cost_model.predict_proba(input_data)[0][1]
    cost_prediction = cost_model.predict(input_data)[0]

    delay_probability = delay_model.predict_proba(input_data)[0][1]
    delay_prediction = delay_model.predict(input_data)[0]

    cost_risk = cost_probability * 100
    delay_risk = delay_probability * 100

    overall_score = (
        0.50 * cost_risk +
        0.50 * delay_risk
    )

    if overall_score < 30:
        risk_level = "LOW"
        warning = "PROJECT APPEARS STABLE"
    elif overall_score < 60:
        risk_level = "MEDIUM"
        warning = "CLOSE MONITORING REQUIRED"
    else:
        risk_level = "HIGH"
        warning = "IMMEDIATE ATTENTION REQUIRED"

    return {
        "cost_risk": cost_risk,
        "cost_prediction": cost_prediction,
        "delay_risk": delay_risk,
        "delay_prediction": delay_prediction,
        "overall_score": overall_score,
        "risk_level": risk_level,
        "warning": warning
    }


# -----------------------------
# MILESTONES
# -----------------------------
def milestone_status(progress, milestone_percent):
    if progress >= milestone_percent:
        return "Completed"

    if progress >= max(0, milestone_percent - 10):
        return "In Progress"

    return "Upcoming"


def build_milestones(project_row):
    progress = float(
        project_row["Physical Progress (in %)"]
        if pd.notna(project_row["Physical Progress (in %)"])
        else 0
    )
    progress = max(0, min(progress, 100))

    sanction = project_row["Sanction Date"]
    original_commissioning = project_row["Original Date of Commissioning"]
    revised_commissioning = project_row["Revised Date of Commissioning"]

    # Prefer original commissioning for the planned timeline.
    # If unavailable/invalid, use revised commissioning.
    planned_end = original_commissioning

    if pd.isna(planned_end) or (
        pd.notna(sanction) and planned_end < sanction
    ):
        planned_end = revised_commissioning

    milestones = []

    # Sanction
    milestones.append({
        "Milestone": "Project Sanction",
        "Target Date": sanction,
        "Status": "Completed" if pd.notna(sanction) else "Date unavailable",
        "Basis": "Recorded date"
    })

    # Estimated progress milestones
    # These are target dates derived from the sanction-to-commissioning
    # window; they are NOT actual completion dates.
    if pd.notna(sanction) and pd.notna(planned_end) and planned_end >= sanction:
        total_days = (planned_end - sanction).days

        for pct in [25, 50, 75]:
            target_date = sanction + pd.Timedelta(
                days=int(total_days * pct / 100)
            )

            milestones.append({
                "Milestone": f"{pct}% Physical Progress",
                "Target Date": target_date,
                "Status": milestone_status(progress, pct),
                "Basis": "Estimated from planned timeline"
            })
    else:
        for pct in [25, 50, 75]:
            milestones.append({
                "Milestone": f"{pct}% Physical Progress",
                "Target Date": pd.NaT,
                "Status": milestone_status(progress, pct),
                "Basis": "Progress-based status"
            })

    # Commissioning
    milestones.append({
        "Milestone": "100% / Commissioning",
        "Target Date": planned_end,
        "Status": "Completed" if progress >= 100 else "Upcoming",
        "Basis": "Planned commissioning date"
    })

    # Revised commissioning, if available
    if pd.notna(revised_commissioning):
        milestones.append({
            "Milestone": "Revised Commissioning",
            "Target Date": revised_commissioning,
            "Status": "Completed" if progress >= 100 else "Planned",
            "Basis": "Recorded revised date"
        })

    return pd.DataFrame(milestones)


# =========================================================
# APP START
# =========================================================

st.title("📊 Project Risk Monitoring Dashboard")
st.caption(
    "AI-powered monitoring of cost overrun risk, delay risk, "
    "project milestones and explainable risk factors."
)

# Load everything
try:
    df = load_data()
    df, prediction_features = prepare_features(df)
    cost_model, delay_model = load_models()
except Exception as e:
    st.error("Unable to load the project data or saved models.")
    st.exception(e)
    st.stop()


# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.header("🔎 Project Selection")

project_options = df["Project Name"].fillna(
    "Unnamed Project"
).astype(str)

selected_project = st.sidebar.selectbox(
    "Select Project",
    project_options.unique()
)

matching_rows = df[df["Project Name"].fillna(
    "Unnamed Project"
).astype(str) == selected_project]

if matching_rows.empty:
    st.error("Selected project could not be found.")
    st.stop()

project_row = matching_rows.iloc[0]

# Create model input
project_input = project_row[prediction_features].to_dict()

# Replace missing categorical values with a safe string.
for col in ["Sector Name", "Line Ministry", "Implementing Agency"]:
    if pd.isna(project_input[col]):
        project_input[col] = "Unknown"

# -----------------------------
# PROJECT INFORMATION
# -----------------------------
st.header("📁 Project Information")

info1, info2, info3, info4 = st.columns(4)

with info1:
    st.metric(
        "Project Code",
        str(project_row["Project Code"])
    )

with info2:
    st.metric(
        "Sector",
        str(project_row["Sector Name"])
    )

with info3:
    st.metric(
        "Physical Progress",
        f"{float(project_row['Physical Progress (in %)'] or 0):.1f}%"
    )

with info4:
    st.metric(
        "Expenditure",
        f"₹ {float(project_row['Expenditure (in cr.)'] or 0):,.2f} Cr"
    )

st.write(f"**Project:** {selected_project}")

# -----------------------------
# RISK PREDICTION
# -----------------------------
risk = predict_project_risk(
    project_input,
    cost_model,
    delay_model
)

st.header("🚦 Risk Summary")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "Cost Overrun Risk",
        f"{risk['cost_risk']:.2f}%"
    )

with c2:
    st.metric(
        "Delay Risk",
        f"{risk['delay_risk']:.2f}%"
    )

with c3:
    st.metric(
        "Overall Risk Score",
        f"{risk['overall_score']:.2f} / 100"
    )

with c4:
    st.metric(
        "Risk Level",
        risk["risk_level"]
    )

if risk["risk_level"] == "HIGH":
    st.error(f"⚠️ {risk['warning']}")
elif risk["risk_level"] == "MEDIUM":
    st.warning(f"⚠️ {risk['warning']}")
else:
    st.success(f"✅ {risk['warning']}")

p1, p2 = st.columns(2)

with p1:
    st.write(
        f"**Cost Overrun Prediction:** "
        f"{'YES' if risk['cost_prediction'] == 1 else 'NO'}"
    )

with p2:
    st.write(
        f"**Delay Prediction:** "
        f"{'YES' if risk['delay_prediction'] == 1 else 'NO'}"
    )


# -----------------------------
# PROJECT MILESTONES
# -----------------------------
st.header("🏁 Project Milestones")

milestones = build_milestones(project_row)

display_milestones = milestones.copy()

display_milestones["Target Date"] = display_milestones[
    "Target Date"
].apply(
    lambda x: x.strftime("%d %b %Y")
    if pd.notna(x)
    else "Not available"
)

st.dataframe(
    display_milestones,
    use_container_width=True,
    hide_index=True
)

st.info(
    "The 25%, 50% and 75% milestone dates are estimated from the "
    "sanction-to-planned-commissioning timeline. They are not actual "
    "recorded completion dates."
)


# -----------------------------
# PROGRESS / EXPENDITURE
# -----------------------------
st.header("📈 Project Progress")

g1, g2 = st.columns(2)

with g1:
    progress = float(project_row["Physical Progress (in %)"] or 0)
    progress = max(0, min(progress, 100))

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(["Physical Progress", "Remaining"])
    ax.set_ylim(0, 100)
    ax.set_ylabel("Percentage")
    ax.set_title("Physical Progress")
    ax.text(0, progress / 2, f"{progress:.1f}%", ha="center", va="center")
    ax.text(1, (100 - progress) / 2, f"{100-progress:.1f}%",
            ha="center", va="center")
    st.pyplot(fig)
    plt.close(fig)

with g2:
    expenditure_ratio = float(
        project_row["Expenditure Ratio (%)"]
    )

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(
        ["Expenditure Ratio", "Physical Progress"],
        [expenditure_ratio, progress]
    )
    ax.set_ylabel("Percentage")
    ax.set_title("Expenditure vs Physical Progress")
    st.pyplot(fig)
    plt.close(fig)

st.write(
    f"**Expenditure Ratio:** {expenditure_ratio:.2f}%  |  "
    f"**Expenditure-Progress Gap:** "
    f"{float(project_row['Expenditure-Progress Gap (%)']):.2f}%"
)


# -----------------------------
# DATES
# -----------------------------
st.header("📅 Important Dates")

d1, d2, d3 = st.columns(3)

def show_date(value):
    return value.strftime("%d %b %Y") if pd.notna(value) else "Not available"

with d1:
    st.metric(
        "Sanction Date",
        show_date(project_row["Sanction Date"])
    )

with d2:
    st.metric(
        "Original Commissioning",
        show_date(project_row["Original Date of Commissioning"])
    )

with d3:
    st.metric(
        "Revised Commissioning",
        show_date(project_row["Revised Date of Commissioning"])
    )


# -----------------------------
# EXPLAINABLE AI
# -----------------------------
st.header("🧠 Explainable AI — Why is this project risky?")

cost_exp, cost_drivers, cost_reducing = get_shap_explanation(
    cost_model,
    pd.DataFrame([project_input])
)

delay_exp, delay_drivers, delay_reducing = get_shap_explanation(
    delay_model,
    pd.DataFrame([project_input])
)

tab1, tab2 = st.tabs(["💰 Cost Risk", "⏱️ Delay Risk"])

with tab1:
    if cost_exp is None:
        st.warning(
            "SHAP explanation could not be generated. "
            "Make sure the `shap` package is installed."
        )
    else:
        a, b = st.columns(2)

        with a:
            st.subheader("Risk-Increasing Factors")

            if cost_drivers.empty:
                st.write("No positive SHAP contributors found.")
            else:
                st.dataframe(
                    cost_drivers[["Feature", "SHAP Value"]]
                    .rename(columns={"SHAP Value": "Impact"}),
                    use_container_width=True,
                    hide_index=True
                )

        with b:
            st.subheader("Risk-Reducing Factors")

            if cost_reducing.empty:
                st.write("No negative SHAP contributors found.")
            else:
                st.dataframe(
                    cost_reducing[["Feature", "SHAP Value"]]
                    .rename(columns={"SHAP Value": "Impact"}),
                    use_container_width=True,
                    hide_index=True
                )

with tab2:
    if delay_exp is None:
        st.warning(
            "SHAP explanation could not be generated. "
            "Make sure the `shap` package is installed."
        )
    else:
        a, b = st.columns(2)

        with a:
            st.subheader("Risk-Increasing Factors")

            if delay_drivers.empty:
                st.write("No positive SHAP contributors found.")
            else:
                st.dataframe(
                    delay_drivers[["Feature", "SHAP Value"]]
                    .rename(columns={"SHAP Value": "Impact"}),
                    use_container_width=True,
                    hide_index=True
                )

        with b:
            st.subheader("Risk-Reducing Factors")

            if delay_reducing.empty:
                st.write("No negative SHAP contributors found.")
            else:
                st.dataframe(
                    delay_reducing[["Feature", "SHAP Value"]]
                    .rename(columns={"SHAP Value": "Impact"}),
                    use_container_width=True,
                    hide_index=True
                )

st.caption(
    "SHAP values show how the trained model's features push the selected "
    "project toward or away from the risk class. They describe model "
    "contribution, not proof of causation."
)


# -----------------------------
# RAW PROJECT DATA
# -----------------------------
with st.expander("🔍 View Project Data"):
    st.dataframe(
        project_row.to_frame("Value"),
        use_container_width=True
    )

st.divider()
st.caption(
    "Project Risk Monitoring System | ML Prediction + Explainable AI + "
    "Dashboard + Milestone Tracking"
)

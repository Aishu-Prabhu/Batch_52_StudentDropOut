import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from pathlib import Path

# -------------------------------
# Streamlit page config
# -------------------------------
st.set_page_config(page_title="Student Dropout Dashboard", layout="wide")

# -------------------------------
# Load dataset with caching
# -------------------------------
@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        st.error(f"CSV file not found at {file_path}")
        return pd.DataFrame()

# -------------------------------
# Load data
# -------------------------------
csv_path = Path(r"C:\Users\Aishu\Desktop\Capstone\student_dropout_dataset.csv")
df = load_data(csv_path)

if df.empty:
    st.stop()

# Normalize column names
df.columns = [c.strip().replace(" ", "_").capitalize() for c in df.columns]

# ---------------------------------
# Sidebar Filters
# ---------------------------------
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2910/2910768.png", width=100)
st.sidebar.title("🎛️ Filter Options")

school = st.sidebar.multiselect("🏫 School Type", df["School"].unique())
area = st.sidebar.multiselect("📍 Locality", df["Area"].unique())
gender = st.sidebar.multiselect("⚧ Gender", df["Gender"].unique())
caste = st.sidebar.multiselect("🧑‍🤝‍🧑 Caste / Category", df["Socialcategory"].unique())
grade = st.sidebar.multiselect("🎒 Grade", df["Grade"].unique())

st.sidebar.header("🎨 Theme Options")
theme_option = st.sidebar.radio("Choose Theme", ["Light", "Dark"], index=0)


# -------------------------------
# Theme Styling (Global CSS)
# -------------------------------
if theme_option == "Dark":
    bg_color = "#0E1117"
    text_color = "#FFFFFF"
    chart_colors = px.colors.qualitative.Dark24

    dark_css = """
    <style>
    body, .stApp {
        background-color: #0E1117 !important;
        color: #FFFFFF !important;
    }
    .stSidebar, .st-emotion-cache-1avcm0n {
        background-color: #161A23 !important;
    }
    .stMarkdown, .stText, .stMetric, .stNumberInput, label, h1, h2, h3, h4, h5, h6, p, span {
        color: #FFFFFF !important;
    }
    .stDataFrame {
        background-color: #1E222D !important;
        color: #FFFFFF !important;
    }
    .stDownloadButton > button {
        background-color: #31364C !important;
        color: white !important;
        border-radius: 10px;
    }
    .stSelectbox div[data-baseweb="select"], .stMultiSelect div[data-baseweb="select"] {
        background-color: #1E222D !important;
        color: white !important;
    }
    </style>
    """
    st.markdown(dark_css, unsafe_allow_html=True)

else:
    bg_color = "#FFFFFF"
    text_color = "#000000"
    chart_colors = px.colors.qualitative.Pastel

    light_css = """
    <style>
    body, .stApp {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    .stSidebar, .st-emotion-cache-1avcm0n {
        background-color: #F4F4F4 !important;
    }
    .stDownloadButton > button {
        background-color: #e6e6e6 !important;
        color: #000000 !important;
        border-radius: 10px;
    }
    </style>
    """
    st.markdown(light_css, unsafe_allow_html=True)


# -------------------------------
# Function to apply theme to charts
# -------------------------------
def apply_theme(fig):
    fig.update_layout(
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        font_color=text_color,
        title_font_color=text_color,
        legend_title_font_color=text_color,
        legend_font_color=text_color
    )
    return fig

# -------------------------------
# Apply Filters
# -------------------------------
df_filtered = df.copy()
if school: df_filtered = df_filtered[df_filtered["School"].isin(school)]
if area: df_filtered = df_filtered[df_filtered["Area"].isin(area)]
if gender: df_filtered = df_filtered[df_filtered["Gender"].isin(gender)]
if caste: df_filtered = df_filtered[df_filtered["Socialcategory"].isin(caste)]
if grade: df_filtered = df_filtered[df_filtered["Grade"].isin(grade)]

if df_filtered.empty:
    st.warning("⚠️ No data available for the selected filters.")
    st.stop()

# -------------------------------
# Dashboard Title
# -------------------------------
st.title("📊 Student Dropout Analysis Dashboard")

# -------------------------------
# KPIs
# -------------------------------
total_students = len(df_filtered)
dropouts = df_filtered[df_filtered["Dropout"] == "yes"].shape[0]
dropout_rate = round((dropouts / total_students) * 100, 2) if total_students > 0 else 0

kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("👩‍🎓 Total Students", total_students)
kpi2.metric("📉 Total Dropouts", dropouts)
kpi3.metric("📊 Dropout Rate (%)", dropout_rate)

st.markdown("---")

# -------------------------------
# Charts Layout
# -------------------------------
col1, col2 = st.columns(2)

with col1:
    df_school = df_filtered[df_filtered["Dropout"] == "yes"].groupby("School").size().reset_index(name="Count")
    fig1 = px.bar(df_school, x="School", y="Count", color="School", title="School-wise Dropouts", color_discrete_sequence=chart_colors)
    st.plotly_chart(apply_theme(fig1), use_container_width=True)

    df_caste = df_filtered[df_filtered["Dropout"] == "yes"].groupby("Socialcategory").size().reset_index(name="Count")
    fig2 = px.bar(df_caste, x="Socialcategory", y="Count", color="Socialcategory", title="Caste-wise Dropouts", color_discrete_sequence=chart_colors)
    st.plotly_chart(apply_theme(fig2), use_container_width=True)

with col2:
    df_area = df_filtered[df_filtered["Dropout"] == "yes"]
    if not df_area.empty:
        fig3 = px.pie(df_area, names="Area", title="Area-wise Dropouts", color_discrete_sequence=chart_colors)
        st.plotly_chart(apply_theme(fig3), use_container_width=True)
        
        fig4 = px.pie(df_area, names="Gender", title="Gender-wise Dropouts", color_discrete_sequence=chart_colors)
        st.plotly_chart(apply_theme(fig4), use_container_width=True)

# -------------------------------
# Grade-wise Trend
# -------------------------------
df_trend = df_filtered.groupby("Grade")["Dropout_score"].mean().reset_index()
fig5 = px.line(df_trend, x="Grade", y="Dropout_score", markers=True,
               title="📈 Average Dropout Score by Grade", color_discrete_sequence=["#636EFA"])
st.plotly_chart(apply_theme(fig5), use_container_width=True)

# -------------------------------
# Correlation Heatmap
# -------------------------------
st.markdown("### 🔍 Correlation Heatmap (Numeric Attributes)")
num_cols = df_filtered.select_dtypes(include=[np.number])
if not num_cols.empty:
    corr = num_cols.corr()
    fig6 = px.imshow(corr, text_auto=True, title="Feature Correlation Heatmap", color_continuous_scale="RdBu_r")
    st.plotly_chart(apply_theme(fig6), use_container_width=True)

# -------------------------------
# Insights Section (5 Keys)
# -------------------------------
st.markdown("### 💡 Key Insights Summary")

drop_df = df_filtered[df_filtered["Dropout"] == "yes"]

if not drop_df.empty:
    top_school = drop_df["School"].mode()[0] if "School" in drop_df.columns else "N/A"
    top_area = drop_df["Area"].mode()[0] if "Area" in drop_df.columns else "N/A"
    top_grade = drop_df["Grade"].mode()[0] if "Grade" in drop_df.columns else "N/A"
    top_gender = drop_df["Gender"].mode()[0] if "Gender" in drop_df.columns else "N/A"
    top_caste = drop_df["Socialcategory"].mode()[0] if "Socialcategory" in drop_df.columns else "N/A"
else:
    top_school = top_area = top_grade = top_gender = top_caste = "N/A"

st.info(f"""
🏫 **Most Dropouts by School Type:** {top_school}  
📍 **Most Dropouts by Area:** {top_area}  
🎒 **Most Dropouts by Grade:** {top_grade}  
⚧  **Most Dropouts by Gender:** {top_gender}   
🧑‍🤝‍🧑 **Most Dropouts by Caste/Category:** {top_caste}
""")

# -------------------------------
# Insights Section (5 Key Factors)
# -------------------------------
st.markdown("### 🔑 Key Insights by Category")

col1, col2 = st.columns(2)
col3, col4, col5 = st.columns(3)

# School-wise Dropouts
with col1:
    school_chart = px.bar(
        df_filtered.groupby("School")["Dropout"].count().reset_index(),
        x="School", y="Dropout", color="School",
        title="School-wise Dropouts"
    )
    st.plotly_chart(school_chart, use_container_width=True)

# Area-wise Dropouts
with col2:
    area_chart = px.pie(
        df_filtered, names="Area",
        title="Area-wise Dropouts"
    )
    st.plotly_chart(area_chart, use_container_width=True)

# Caste-wise Dropouts
with col3:
    caste_chart = px.bar(
        df_filtered.groupby("Socialcategory")["Dropout"].count().reset_index(),
        x="Socialcategory", y="Dropout", color="Socialcategory",
        title="Caste-wise Dropouts"
    )
    st.plotly_chart(caste_chart, use_container_width=True)

# Gender-wise Dropouts
with col4:
    gender_chart = px.pie(
        df_filtered, names="Gender",
        title="Gender-wise Dropouts"
    )
    st.plotly_chart(gender_chart, use_container_width=True)

# Grade-wise Dropouts
with col5:
    grade_chart = px.bar(
        df_filtered.groupby("Grade")["Dropout"].count().reset_index(),
        x="Grade", y="Dropout", color="Grade",
        title="Grade-wise Dropouts"
    )
    st.plotly_chart(grade_chart, use_container_width=True)


st.markdown("---")

# -------------------------------
# Download Button
# -------------------------------
st.download_button(
    label="⬇️ Download Filtered Data as CSV",
    data=df_filtered.to_csv(index=False).encode('utf-8'),
    file_name="filtered_dropout_data.csv",
    mime="text/csv"
)

# -------------------------------
# Filtered Data Table
# -------------------------------
st.markdown("### 🧾 Filtered Student Data")
st.dataframe(df_filtered)
st.caption("Developed by Trio Capstone CSE_52 Team | Powered by Streamlit & Plotly")

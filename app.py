import streamlit as st
import pandas as pd

# تحميل البيانات
df = pd.read_excel("wuzzuf_jobs.xlsx")

st.title("لوحة عرض وظائف Wuzzuf")

# فلاتر
city = st.selectbox("اختار المدينة", df["Location"].unique())
field = st.text_input("ابحث عن كلمة في المسمى الوظيفي")
company = st.selectbox("اختار الشركة (اختياري)", ["All"] + df["Company"].unique().tolist())

# تطبيق الفلاتر
filtered = df[
    (df["Location"] == city) &
    (df["Job Title"].str.contains(field, case=False, na=False))
]

if company != "All":
    filtered = filtered[filtered["Company"] == company]

# عرض عدد الوظائف
st.write(f"عدد الوظائف المعروضة: {len(filtered)}")

# عرض الجدول المحسّن
st.dataframe(filtered.style.highlight_max(subset=["Salary"], color="lightgreen"))

# مثال لمخطط: توزيع الوظائف حسب الخبرة
if "Experience" in df.columns:
    st.bar_chart(filtered["Experience"].value_counts())


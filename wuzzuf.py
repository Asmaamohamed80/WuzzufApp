import streamlit as st
import pandas as pd
import plotly.express as px

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Wuzzuf Jobs Dashboard", page_icon="📊", layout="wide")

# --- تحميل البيانات مع التخزين المؤقت ---
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("wuzzuf_jobs.xlsx")
        # تنظيف البيانات الأساسية
        if "Location" in df.columns:
            df["Location"] = df["Location"].astype(str).str.strip()
        if "Company" in df.columns:
            df["Company"] = df["Company"].astype(str).str.strip()
        if "Job Title" in df.columns:
            df["Job Title"] = df["Job Title"].astype(str).str.strip()
        if "Experience Required" in df.columns:
            df["Experience Required"] = df["Experience Required"].astype(str).str.strip()
        return df
    except FileNotFoundError:
        st.error("خطأ: لم يتم العثور على ملف 'wuzzuf_jobs.xlsx'. يرجى التأكد من وجود الملف في نفس المجلد.")
        return None

df = load_data()

# --- إيقاف التطبيق إذا لم يتم تحميل البيانات ---
if df is None:
    st.stop()

# --- الشريط الجانبي للفلاتر ---
st.sidebar.header("🔍 فلاتر البحث")

# فلتر المدينة مع خيار "كل المدن"
if "Location" in df.columns:
    cities = ["كل المدن"] + sorted(df["Location"].dropna().unique().tolist())
else:
    cities = ["كل المدن"]
selected_city = st.sidebar.selectbox("اختر المدينة", cities)

# فلتر الشركة مع خيار "كل الشركات"
if "Company" in df.columns:
    companies = ["كل الشركات"] + sorted(df["Company"].dropna().unique().tolist())
else:
    companies = ["كل الشركات"]
selected_company = st.sidebar.selectbox("اختر الشركة", companies)

# فلتر البحث بالكلمة المفتاحية في المسمى الوظيفي
job_title_query = st.sidebar.text_input("ابحث في المسمى الوظيفي")

# --- تطبيق الفلاتر على البيانات ---
filtered_df = df.copy()

if selected_city != "كل المدن" and "Location" in df.columns:
    filtered_df = filtered_df[filtered_df["Location"] == selected_city]

if selected_company != "كل الشركات" and "Company" in df.columns:
    filtered_df = filtered_df[filtered_df["Company"] == selected_company]

if job_title_query and "Job Title" in df.columns:
    filtered_df = filtered_df[filtered_df["Job Title"].str.contains(job_title_query, case=False, na=False)]

# --- الواجهة الرئيسية ---
st.title("📊 لوحة عرض وتحليل وظائف Wuzzuf")
st.markdown("---")

# --- عرض الإحصائيات الرئيسية ---
total_jobs = len(df)
filtered_jobs = len(filtered_df)
total_companies = len(filtered_df["Company"].unique()) if "Company" in filtered_df.columns else 0

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="إجمالي الوظائف في الملف", value=f"{total_jobs:,}")
with col2:
    st.metric(label="الوظائف المطابقة للبحث", value=f"{filtered_jobs:,}")
with col3:
    st.metric(label="عدد الشركات", value=f"{total_companies:,}")

st.markdown("---")

# --- عرض البيانات والرسوم البيانية ---
if not filtered_df.empty:
    st.subheader("📋 الوظائف المتاحة")
    st.dataframe(
        filtered_df.style.highlight_max(subset=["Salary"], color="#90EE90", axis=0) 
        if "Salary" in filtered_df.columns else filtered_df,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("📈 رسوم بيانية تحليلية")
    col1, col2 = st.columns(2)

    with col1:
        # مخطط توزيع الوظائف حسب مستوى الخبرة
        if "Experience Required" in filtered_df.columns:
            st.write("#### توزيع الوظائف حسب مستوى الخبرة")
            exp_counts = filtered_df["Experience Required"].value_counts()
            fig_exp = px.bar(
                exp_counts,
                x=exp_counts.index,
                y=exp_counts.values,
                title="عدد الوظائف لكل مستوى خبرة",
                labels={'x': 'مستوى الخبرة', 'y': 'عدد الوظائف'},
                color=exp_counts.index,
                text_auto=True
            )
            fig_exp.update_layout(showlegend=False)
            st.plotly_chart(fig_exp, use_container_width=True)

    with col2:
        # مخطط دائري لتوزيع الوظائف على أهم 10 مدن (يظهر فقط عند اختيار "كل المدن")
        if selected_city == "كل المدن" and "Location" in df.columns:
            st.write("#### توزيع الوظائف على أهم 10 مدن")
            top_10_cities = df["Location"].value_counts().nlargest(10)
            fig_city = px.pie(
                values=top_10_cities.values,
                names=top_10_cities.index,
                title="نسبة الوظائف في أهم 10 مدن",
                color_discrete_sequence=px.colors.sequential.RdBu
            )
            fig_city.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_city, use_container_width=True)
        else:
            st.info(f"يتم عرض بيانات مدينة **{selected_city}** فقط. اختر 'كل المدن' لعرض مخطط التوزيع.")

else:
    st.warning("⚠️ لا توجد وظائف تطابق معايير البحث الحالية. حاول تغيير الفلاتر.")


    
    

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import pyreadstat
import os

st.set_page_config(page_title="NDHS 2022 MCH Dashboard", layout="wide")
st.title("🍼 Maternal & Child Health Dashboard")
st.subheader("NDHS 2022 Real Microdata – Weighted Estimates")

# ====================== LOAD & PREPARE DATA ======================
@st.cache_data(persist="disk")
def load_and_prepare():
    province_map = {
        1: 'Koshi', 2: 'Madhesh', 3: 'Bagmati', 4: 'Gandaki',
        5: 'Lumbini', 6: 'Karnali', 7: 'Sudurpashchim'
    }

    ir_dta = "NPIR82FL.dta"
    kr_dta = "NPKR82FL.dta"
    ir_csv = "sample_women.csv"
    kr_csv = "sample_child.csv"

    # ---- Check which data source is available (case‑insensitive) ----
    all_files = os.listdir() if os.path.exists('.') else []
    
    ir_dta_actual = next((f for f in all_files if f.lower() == ir_dta.lower()), None)
    kr_dta_actual = next((f for f in all_files if f.lower() == kr_dta.lower()), None)
    ir_csv_actual = next((f for f in all_files if f.lower() == ir_csv.lower()), None)
    kr_csv_actual = next((f for f in all_files if f.lower() == kr_csv.lower()), None)

    if ir_dta_actual and kr_dta_actual:
        # Real DHS data
        ir_cols = ['caseid', 'v001', 'v002', 'v005', 'v024', 'v025', 'v190', 'v201']
        women, _ = pyreadstat.read_dta(ir_dta_actual, usecols=ir_cols)

        kr_cols = [
            'caseid', 'v001', 'v002', 'v005', 'v024', 'v025', 'v190',
            'bidx', 'midx', 'b3', 'b5', 'b8',
            'hw1', 'hc70', 'hc71', 'hc72', 'hw70', 'hw72',
            'm14', 'm15'
        ]
        available = []
        for col in kr_cols:
            try:
                _ = pyreadstat.read_dta(kr_dta_actual, usecols=[col])
                available.append(col)
            except:
                continue
        child, _ = pyreadstat.read_dta(kr_dta_actual, usecols=available)
        data_source = "✅ Real DHS 2022 Microdata"

    elif ir_csv_actual and kr_csv_actual:
        # Synthetic sample data
        women = pd.read_csv(ir_csv_actual)
        child = pd.read_csv(kr_csv_actual)
        data_source = "⚠️ Synthetic Sample Data (Demo Only)"

    else:
        st.error(f"""
        **❌ No data files found!**

        Looking for either:
        - `{ir_dta}` and `{kr_dta}` (real data), **OR**
        - `{ir_csv}` and `{kr_csv}` (demo data).

        Files in current directory: {all_files}
        """)
        st.stop()

    # ---- Weight ----
    women['weight'] = women['v005'] / 1_000_000.0
    child['weight'] = child['v005'] / 1_000_000.0

    # ---- Province mapping ----
    if 'Province' not in women.columns:
        women['Province'] = women['v024'].map(province_map)
    if 'Province' not in child.columns:
        child['Province'] = child['v024'].map(province_map)

    # ---- Most recent birth ----
    if 'midx' in child.columns:
        recent_flag = 'midx'
    elif 'bidx' in child.columns:
        recent_flag = 'bidx'
    else:
        child_sorted = child.sort_values(['caseid', 'b3'], ascending=[True, False])
        recent_births = child_sorted.groupby('caseid').first().reset_index()
        recent_flag = None

    if recent_flag is not None:
        recent_births = child[child[recent_flag] == 1].copy()

    # ---- ANC 4+ ----
    if 'm14' in recent_births.columns:
        recent_births['anc4'] = (recent_births['m14'] >= 4) & (recent_births['m14'] <= 30)
        recent_births['anc4'] = recent_births['anc4'].astype('boolean')
        recent_births.loc[recent_births['m14'] >= 98, 'anc4'] = pd.NA
    else:
        recent_births['anc4'] = pd.NA

    # ---- Facility delivery ----
    if 'm15' in recent_births.columns:
        facility_codes = list(range(21, 27)) + list(range(31, 37))
        recent_births['facility'] = recent_births['m15'].isin(facility_codes)
        recent_births['facility'] = recent_births['facility'].astype('boolean')
        recent_births.loc[recent_births['m15'] == 99, 'facility'] = pd.NA
    else:
        recent_births['facility'] = pd.NA

    # ---- Stunting ----
    haz_col = None
    for col in ['hc70', 'hc72', 'hw70', 'hw72']:
        if col in recent_births.columns:
            haz_col = col
            break
    if haz_col:
        recent_births['stunted'] = recent_births[haz_col] < -200
        recent_births['stunted'] = recent_births['stunted'].astype('boolean')
        recent_births.loc[recent_births[haz_col] > 9000, 'stunted'] = pd.NA
    else:
        recent_births['stunted'] = pd.NA

    # ---- Fertility ----
    if 'v201' in women.columns:
        women['tceb'] = women['v201']
    else:
        women['tceb'] = pd.NA

    return women, child, recent_births, province_map, data_source


women, child, recent_births, province_map, data_source = load_and_prepare()

# Display data source info
if "Synthetic" in data_source:
    st.warning(data_source)
else:
    st.success(data_source)

# ====================== WEIGHTED AGGREGATION HELPERS ======================
def weighted_mean(df, col, weight_col='weight'):
    valid = df[col].notna() & df[weight_col].notna()
    if valid.sum() == 0:
        return np.nan
    return (df.loc[valid, col] * df.loc[valid, weight_col]).sum() / df.loc[valid, weight_col].sum()

def weighted_percentage(df, bool_col):
    return weighted_mean(df, bool_col) * 100

def province_summary(df, indicator_col, is_bool=True):
    result = []
    for prov in province_map.values():
        sub = df[df['Province'] == prov]
        if is_bool:
            val = weighted_percentage(sub, indicator_col)
        else:
            val = weighted_mean(sub, indicator_col)
        result.append({'Province': prov, 'Value': val if not np.isnan(val) else 0.0})
    return pd.DataFrame(result)

def wealth_summary(df, indicator_col, is_bool=True):
    wealth_labels = {1: 'Poorest', 2: 'Poorer', 3: 'Middle', 4: 'Richer', 5: 'Richest'}
    result = []
    for quint in range(1, 6):
        sub = df[df['v190'] == quint]
        if is_bool:
            val = weighted_percentage(sub, indicator_col)
        else:
            val = weighted_mean(sub, indicator_col)
        result.append({'Wealth': wealth_labels[quint], 'Value': val if not np.isnan(val) else 0.0})
    return pd.DataFrame(result)

# ====================== NATIONAL AVERAGES ======================
anc_natl = weighted_percentage(recent_births, 'anc4')
facility_natl = weighted_percentage(recent_births, 'facility')
stunting_natl = weighted_percentage(recent_births, 'stunted')
fertility_natl = weighted_mean(women, 'tceb')

# ====================== DIAGNOSTIC EXPANDER ======================
with st.expander("🔬 Diagnostic Info"):
    st.write(f"**Total children in KR file:** {len(child):,}")
    st.write(f"**Most recent births (after filter):** {len(recent_births):,}")
    if 'm14' in recent_births.columns:
        st.write("**m14 distribution (recent births):**")
        st.write(recent_births['m14'].value_counts().sort_index().head(20))
    if 'm15' in recent_births.columns:
        st.write("**m15 distribution (recent births):**")
        st.write(recent_births['m15'].value_counts().sort_index().head(20))
    if 'stunted' in recent_births.columns:
        st.write("**Stunting variable summary:**")
        st.write(f"Non‑missing HAZ: {recent_births['stunted'].notna().sum():,}")
        st.write(f"Stunted (unweighted): {recent_births['stunted'].mean()*100:.1f}%")
    st.write("**Columns in KR/child file:**", list(child.columns))
    st.write("**Columns in IR/women file:**", list(women.columns))

# ====================== TABS ======================
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🏔️ By Province", "💰 By Wealth", "📝 Notes"])

with tab1:
    st.markdown("### National Highlights (NDHS 2022)")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("4+ ANC Visits", f"{anc_natl:.1f}%" if not np.isnan(anc_natl) else "N/A")
    c2.metric("Facility Delivery", f"{facility_natl:.1f}%" if not np.isnan(facility_natl) else "N/A")
    c3.metric("Child Stunting", f"{stunting_natl:.1f}%" if not np.isnan(stunting_natl) else "N/A")
    c4.metric("Fertility (TCEB)", f"{fertility_natl:.2f}" if not np.isnan(fertility_natl) else "N/A")
    st.caption("Weighted national estimates | ANC/Delivery based on most recent live birth")

with tab2:
    st.subheader("Indicators by Province")
    indicator = st.selectbox(
        "Select Indicator",
        ["4+ ANC Visits (%)", "Facility Delivery (%)", "Child Stunting (%)", "Fertility (children per woman)"],
        key="prov_indicator"
    )

    if indicator == "4+ ANC Visits (%)":
        df_plot = province_summary(recent_births, 'anc4', is_bool=True)
        title = "4+ ANC Visits (%) by Province"
        color_scale = px.colors.sequential.Blues_r
        y_label = "Percentage (%)"
        y_range = [0, 100]
        text_fmt = '%{text:.1f}%'
    elif indicator == "Facility Delivery (%)":
        df_plot = province_summary(recent_births, 'facility', is_bool=True)
        title = "Facility Delivery (%) by Province"
        color_scale = px.colors.sequential.Teal_r
        y_label = "Percentage (%)"
        y_range = [0, 100]
        text_fmt = '%{text:.1f}%'
    elif indicator == "Child Stunting (%)":
        df_plot = province_summary(recent_births, 'stunted', is_bool=True)
        title = "Child Stunting (%) by Province"
        color_scale = px.colors.sequential.Reds_r
        y_label = "Percentage (%)"
        y_range = [0, 100]
        text_fmt = '%{text:.1f}%'
    else:  # Fertility
        df_plot = province_summary(women, 'tceb', is_bool=False)
        title = "Fertility (Children Ever Born) by Province"
        color_scale = px.colors.sequential.Greens
        y_label = "Average number of children"
        y_range = [0, 3]
        text_fmt = '%{text:.2f}'

    fig = px.bar(
        df_plot, x='Province', y='Value', color='Province',
        title=title, text='Value',
        color_discrete_sequence=color_scale
    )
    fig.update_traces(texttemplate=text_fmt, textposition='outside')
    fig.update_layout(yaxis_title=y_label, yaxis_range=y_range)
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("View Data Table"):
        st.dataframe(df_plot.set_index('Province').round(1))

with tab3:
    st.subheader("Disparities by Wealth Quintile")
    indicator_w = st.selectbox(
        "Select Indicator",
        ["4+ ANC Visits (%)", "Facility Delivery (%)", "Child Stunting (%)", "Fertility (children per woman)"],
        key="wealth_indicator"
    )

    if indicator_w == "4+ ANC Visits (%)":
        df_plot = wealth_summary(recent_births, 'anc4', is_bool=True)
        title = "4+ ANC Visits by Wealth Quintile"
        color_scale = px.colors.sequential.Blues_r
        y_label = "Percentage (%)"
        y_range = [0, 100]
        text_fmt = '%{text:.1f}%'
    elif indicator_w == "Facility Delivery (%)":
        df_plot = wealth_summary(recent_births, 'facility', is_bool=True)
        title = "Facility Delivery by Wealth Quintile"
        color_scale = px.colors.sequential.Teal_r
        y_label = "Percentage (%)"
        y_range = [0, 100]
        text_fmt = '%{text:.1f}%'
    elif indicator_w == "Child Stunting (%)":
        df_plot = wealth_summary(recent_births, 'stunted', is_bool=True)
        title = "Child Stunting by Wealth Quintile"
        color_scale = px.colors.sequential.Reds_r
        y_label = "Percentage (%)"
        y_range = [0, 100]
        text_fmt = '%{text:.1f}%'
    else:  # Fertility
        df_plot = wealth_summary(women, 'tceb', is_bool=False)
        title = "Fertility by Wealth Quintile"
        color_scale = px.colors.sequential.Greens
        y_label = "Average number of children"
        y_range = [0, 3]
        text_fmt = '%{text:.2f}'

    fig = px.bar(
        df_plot, x='Wealth', y='Value', color='Wealth',
        title=title, text='Value',
        color_discrete_sequence=color_scale
    )
    fig.update_traces(texttemplate=text_fmt, textposition='outside')
    fig.update_layout(yaxis_title=y_label, yaxis_range=y_range)
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.markdown("""
    ### 📌 Data Sources & Methodology
    - **Women's Recode (`NPIR82FL.dta`)**: Fertility (`v201`).
    - **Kids Recode (`NPKR82FL.dta`)**: ANC (`m14`), delivery (`m15`), stunting (`hc70`/`hc72`).
    - **Most recent birth**: Identified via `midx` (DHS‑8) or `bidx` (DHS‑7).
    - **Weights**: All estimates use `v005/1,000,000`.
    - **Missing values**: Codes 98/99 are excluded from percentages.

    ---
    ### 📚 Recommended Citation
    Ministry of Health and Population (MoHP), Nepal; New ERA; and ICF. 2023.  
    *Nepal Demographic and Health Survey 2022*. Kathmandu, Nepal: MoHP, Nepal.

    *The microdata used in this dashboard (NPIR82FL.dta and NPKR82FL.dta) were obtained from the DHS Program. The files are not included in this repository. To request access, visit [dhsprogram.com](https://dhsprogram.com/data/dataset_admin/login_main.cfm).*

    ---
    **🔬 Diagnostic Info expander above.**
    """)

    with st.expander("🔍 Columns actually present in your datasets"):
        st.write("**Women (IR) columns:**", list(women.columns))
        st.write("**Recent births (KR subset) columns:**", list(recent_births.columns))

st.caption("NDHS 2022 Real Microdata Dashboard | By Prabhat Kumar Sardar")

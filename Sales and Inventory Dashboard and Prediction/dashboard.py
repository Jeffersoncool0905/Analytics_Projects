import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Sales & Inventory Analytics", layout="wide", initial_sidebar_state="expanded")

# --- DATA LOADING ---
@st.cache_data
def load_data():
    df = pd.read_csv('Store_inventory_data.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    df['Revenue'] = df['Units Sold'] * df['Price']
    df['Discount Value'] = (df['Price'] * df['Units Sold']) * (df['Discount'] / 100)
    return df

df = load_data()

# --- THEME CONTROLS ---
st.sidebar.header("Appearance")
theme_choice = st.sidebar.radio("Chart Theme", ["Dark Mode", "Light Mode"])
plt_template = "plotly_dark" if theme_choice == "Dark Mode" else "plotly_white"

# --- CUSTOM CSS: THE ULTIMATE DESIGN UPGRADE ---
base_css = """
<style>
    /* Smooth fade-in transition and widen layout padding */
    .main .block-container { animation: fadeIn 0.8s cubic-bezier(0.16, 1, 0.3, 1); padding-top: 1.5rem !important; }
    @keyframes fadeIn { 0% { opacity: 0; transform: translateY(20px); } 100% { opacity: 1; transform: translateY(0); } }
    
    /* Clean UI: Hide Streamlit Defaults */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}

    /* Custom Header Banner */
    .title-banner { padding: 25px 35px; border-radius: 12px; margin-bottom: 35px; transition: all 0.3s ease; }
    .title-banner h1 { margin: 0; font-family: 'Segoe UI', system-ui, sans-serif; font-size: 2.8rem; font-weight: 800; letter-spacing: -1px; }
    .title-banner p { margin: 5px 0 0 0; font-size: 1.1rem; font-weight: 500; }
    
    /* Creator Badge */
    .creator-badge { 
        display: inline-block; margin-top: 15px; 
        background: linear-gradient(135deg, #3b82f6, #2563eb); 
        color: #ffffff !important; padding: 6px 18px; 
        border-radius: 20px; font-size: 0.9rem; font-weight: 600; 
        box-shadow: 0 4px 10px rgba(59, 130, 246, 0.4); 
        transition: transform 0.2s ease;
    }
    .creator-badge:hover { transform: translateY(-2px); }

    /* Metric Cards - Elevate them to look like premium containers */
    div[data-testid="metric-container"] { 
        padding: 20px; border-radius: 12px; 
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease; 
    }
    div[data-testid="metric-container"]:hover { transform: translateY(-4px); }
    [data-testid="stMetricValue"] { font-size: 2.2rem !important; font-weight: 800 !important; font-family: 'Segoe UI', sans-serif; }

    /* Modern Pill-Style Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; padding: 8px; border-radius: 14px; border-bottom: none; }
    .stTabs [data-baseweb="tab"] { border-radius: 10px !important; padding: 10px 24px !important; font-size: 1.05rem; font-weight: 600; transition: all 0.3s ease; border: 1px solid transparent; }
    
    /* AI Insight Expander Button Style */
    [data-testid="stExpander"] { border: 1px solid #3b82f6 !important; border-radius: 8px !important; background-color: rgba(59, 130, 246, 0.04) !important; margin-bottom: 20px; }
    [data-testid="stExpander"] p { font-size: 1.05rem; line-height: 1.6; }
</style>
"""

if theme_choice == "Dark Mode":
    theme_css = """
<style>
.title-banner { background: linear-gradient(90deg, #1f2937 0%, #111827 100%); border-left: 6px solid #3b82f6; box-shadow: 0 8px 16px rgba(0,0,0,0.4); }
.title-banner h1 { color: #f9fafb; }
.title-banner p { color: #9ca3af; }

div[data-testid="metric-container"] { background-color: #1f2937; border: 1px solid #374151; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
div[data-testid="metric-container"]:hover { border-color: #3b82f6; box-shadow: 0 8px 15px rgba(59, 130, 246, 0.15); }
div[data-testid="metric-container"] label { color: #9ca3af !important; }
div[data-testid="metric-container"] [data-testid="stMetricValue"] { color: #f9fafb !important; }

.stTabs [data-baseweb="tab-list"] { background-color: #111827; }
.stTabs [data-baseweb="tab"] { color: #9ca3af; }
.stTabs [aria-selected="true"] { background-color: #374151 !important; color: #ffffff !important; border: 1px solid #4b5563 !important; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
</style>
"""
else:
    theme_css = """
<style>
.title-banner { background: linear-gradient(90deg, #ffffff 0%, #f3f4f6 100%); border-left: 6px solid #3b82f6; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
.title-banner h1 { color: #111827; }
.title-banner p { color: #4b5563; }

div[data-testid="metric-container"] { background-color: #ffffff; border: 1px solid #e5e7eb; box-shadow: 0 2px 4px rgba(0,0,0,0.03); }
div[data-testid="metric-container"]:hover { border-color: #3b82f6; box-shadow: 0 8px 15px rgba(59, 130, 246, 0.1); }
div[data-testid="metric-container"] label { color: #6b7280 !important; }
div[data-testid="metric-container"] [data-testid="stMetricValue"] { color: #111827 !important; }

.stTabs [data-baseweb="tab-list"] { background-color: #f3f4f6; }
.stTabs [data-baseweb="tab"] { color: #6b7280; }
.stTabs [aria-selected="true"] { background-color: #ffffff !important; color: #111827 !important; border: 1px solid #e5e7eb !important; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
</style>
"""

st.markdown(base_css + theme_css, unsafe_allow_html=True)

# --- GLOBAL SIDEBAR FILTERS ---
st.sidebar.header("Global Filters")
min_d = df['Date'].min().date()
max_d = df['Date'].max().date()
date_range = st.sidebar.date_input("Date Range", value=(min_d, max_d), min_value=min_d, max_value=max_d)

start_d = date_range[0]
end_d = date_range[1] if len(date_range) > 1 else date_range[0]

selected_categories = st.sidebar.multiselect("Categories", df['Category'].unique(), default=df['Category'].unique())
selected_regions = st.sidebar.multiselect("Regions", df['Region'].unique(), default=df['Region'].unique())

mask = (
    (df['Date'] >= pd.to_datetime(start_d)) & 
    (df['Date'] <= pd.to_datetime(end_d)) &
    (df['Category'].isin(selected_categories)) &
    (df['Region'].isin(selected_regions))
)
filtered_df = df.loc[mask].copy()

# --- SAFEGUARD: EMPTY DATA ---
if filtered_df.empty:
    st.warning("No Data Found. Please adjust your filters.")
    st.stop()

# --- MODAL COMPONENT & CLICK HANDLER ---
@st.dialog("Detailed Data Viewer", width="large")
def show_data_modal(modal_df, context=""):
    st.markdown(f"### Drill-down Analysis: **{context}**")
    display_df = modal_df.copy()
    
    col1, col2 = st.columns(2)
    if 'Category' in modal_df.columns:
        with col1:
            cat_filter = st.multiselect("Filter Category", modal_df['Category'].unique(), default=modal_df['Category'].unique(), key=f"mod_cat_{context}")
            display_df = display_df[display_df['Category'].isin(cat_filter)]
    if 'Region' in modal_df.columns:
        with col2:
            reg_filter = st.multiselect("Filter Region", modal_df['Region'].unique(), default=modal_df['Region'].unique(), key=f"mod_reg_{context}")
            display_df = display_df[display_df['Region'].isin(reg_filter)]
            
    st.dataframe(display_df, use_container_width=True)

# --- AI INSIGHT GENERATOR ---
def generate_ai_insight(df_source, title):
    if df_source.empty:
        return "Not enough data available to generate a clear insight."
        
    clean_title = title.replace("<b>", "").replace("</b>", "")
    numeric_cols = df_source.select_dtypes(include=[np.number]).columns.tolist()
    if not numeric_cols:
        return "This chart simply maps out categories and relationships, showing how everything connects together."
        
    primary_col = numeric_cols[0]
    for col in ['Revenue', 'Units Sold', 'Inventory Level', 'Forecast', 'Discount Value', 'Days']:
        if col in numeric_cols:
            primary_col = col
            break
            
    avg = df_source[primary_col].mean()
    max_val = df_source[primary_col].max()
    
    text = f"**Simple Breakdown:**\n\n"
    text += f"Looking at the data for **{primary_col}**, the normal day-to-day average sits around **{avg:,.0f}**. "
    
    if 'Category' in df_source.columns and len(df_source['Category'].unique()) > 1:
        top_cat = df_source.groupby('Category')[primary_col].sum().idxmax()
        bottom_cat = df_source.groupby('Category')[primary_col].sum().idxmin()
        if top_cat != bottom_cat:
            text += f"When we split this up by department, **{top_cat}** is doing the heavy lifting and driving the most volume, whereas **{bottom_cat}** is currently at the bottom of the pile. "
            
    if 'Region' in df_source.columns and len(df_source['Region'].unique()) > 1:
        top_reg = df_source.groupby('Region')[primary_col].sum().idxmax()
        text += f"On the map, **{top_reg}** is your strongest territory overall. "
        
    if 'Date' in df_source.columns:
        text += f"If we look at the timeline, things fluctuate quite a bit, hitting a peak high of **{max_val:,.0f}** at its best point. "
        
    if 'Forecast' in df_source.columns or 'Proj' in title:
        text += "Since this is a future prediction, this tells us what to expect over the next 30 days if current buying habits don't change. "
        
    if 'Discount' in title:
        text += "This helps us see if dropping prices actually convinces people to buy more, or if it just eats into your profits. "
        
    if 'Inventory' in title and 'Risk' in title:
        text += "This is a warning system—items high on this list are selling faster than you can stock them, meaning you need to reorder them immediately. "
        
    text += "\n\n*💡 AI Recommendation:* Focus your energy on your top performers, and make sure your inventory in the leading regions doesn't run dry!"
    return text

def apply_premium_chart_style(fig):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=40, b=20),
        font=dict(family="Segoe UI, sans-serif")
    )
    grid_color = '#374151' if theme_choice == 'Dark Mode' else '#e5e7eb'
    try:
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor=grid_color, zerolinecolor=grid_color)
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor=grid_color, zerolinecolor=grid_color)
    except:
        pass
    return fig

def handle_click(event, source_df, filter_col, context_prefix):
    if event and getattr(event, 'selection', None):
        points = event.selection.get("points", [])
        if len(points) > 0:
            val = points[0].get("x") or points[0].get("label") or points[0].get("id")
            if val is not None and filter_col in source_df.columns:
                try:
                    if pd.api.types.is_datetime64_any_dtype(source_df[filter_col]):
                        val = pd.to_datetime(val)
                    elif pd.api.types.is_numeric_dtype(source_df[filter_col]):
                        val = type(source_df[filter_col].iloc[0])(val)
                except Exception:
                    pass
                show_data_modal(source_df[source_df[filter_col] == val], f"{context_prefix}: {val}")

def render_clickable_chart(fig, source_df, filter_col, context_prefix, key):
    fig = apply_premium_chart_style(fig)
    event = st.plotly_chart(fig, use_container_width=True, on_select="rerun", key=key)
    
    title = fig.layout.title.text if fig.layout.title and fig.layout.title.text else context_prefix
    with st.expander("✨ View AI Interpretation"):
        st.markdown(generate_ai_insight(source_df, title))
        
    handle_click(event, source_df, filter_col, context_prefix)

def render_static_chart(fig, source_df):
    fig = apply_premium_chart_style(fig)
    st.plotly_chart(fig, use_container_width=True)
    
    title = fig.layout.title.text if fig.layout.title and fig.layout.title.text else "Chart"
    with st.expander("✨ View AI Interpretation"):
        st.markdown(generate_ai_insight(source_df, title))

# --- FORECAST HELPER ---
def generate_forecast(df_source, date_col, val_col, periods=30, agg='sum'):
    if df_source.empty:
        return pd.DataFrame(), pd.DataFrame()
    daily = df_source.groupby(date_col)[val_col].agg(agg).reset_index()
    daily['DayOfWeek'] = daily[date_col].dt.dayofweek
    dow_avg = daily.tail(28).groupby('DayOfWeek')[val_col].mean().to_dict()
    last_date = daily[date_col].max()
    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=periods)
    forecast = [dow_avg.get(d.dayofweek, daily[val_col].mean()) for d in future_dates]
    return daily, pd.DataFrame({date_col: future_dates, 'Forecast': forecast})

# --- CUSTOM HEADER ---
st.markdown("""
<div class="title-banner">
    <h1>Enterprise Analytics Hub</h1>
    <p>Advanced Business Intelligence & Demand Forecasting Architecture</p>
    <div class="creator-badge">Created by Jefferson Paul M. Petronio</div>
</div>
""", unsafe_allow_html=True)

# --- TABS NAVIGATION ---
tab_inv, tab_fin, tab_loc, tab_pred = st.tabs(["Inventory Analytics", "Financial Performance", "Regional Distribution", "Demand Projections"])

# --- TAB 1: INVENTORY ---
with tab_inv:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Current Inventory", f"{filtered_df['Inventory Level'].sum():,}")
    c2.metric("Total Units Ordered", f"{filtered_df['Units Ordered'].sum():,}")
    c3.metric("Avg Inventory per Category", f"{filtered_df['Inventory Level'].mean():.0f}")
    c4.metric("Low Stock Alerts", f"{len(filtered_df[filtered_df['Inventory Level'] < 100]):,}")
    st.divider()

    r1c1, r1c2 = st.columns(2)
    with r1c1:
        inv_sum = filtered_df.groupby('Category', as_index=False)['Inventory Level'].mean()
        fig1 = px.bar(inv_sum, x='Category', y='Inventory Level', title="Average Inventory by Category", color='Category', template=plt_template)
        render_clickable_chart(fig1, filtered_df, 'Category', 'Category', 'i1')
    with r1c2:
        fig2 = px.box(filtered_df, x="Category", y="Inventory Level", title="Inventory Spread & Outliers", color="Category", template=plt_template)
        render_clickable_chart(fig2, filtered_df, 'Category', 'Category', 'i2')

    r2c1, r2c2 = st.columns(2)
    with r2c1:
        scatter_agg = filtered_df.groupby(['Category', 'Units Ordered'], as_index=False)['Inventory Level'].mean()
        fig3 = px.scatter(scatter_agg, x="Units Ordered", y="Inventory Level", color="Category", title="Reorder Behavior (Avg Inv per Order Volume)", opacity=0.8, size_max=10, template=plt_template)
        render_clickable_chart(fig3, scatter_agg, 'Units Ordered', 'Units Ordered', 'i3')
    with r2c2:
        inv_trend = filtered_df.groupby('Date', as_index=False)['Inventory Level'].mean()
        fig4 = px.line(inv_trend, x='Date', y='Inventory Level', title="Historical Inventory Average Trend", template=plt_template)
        render_clickable_chart(fig4, filtered_df, 'Date', 'Date', 'i4')

    r3c1, r3c2 = st.columns(2)
    with r3c1:
        daily_inv_dist = filtered_df.groupby(['Date', 'Category'], as_index=False)['Inventory Level'].sum()
        fig5 = px.histogram(daily_inv_dist, x="Inventory Level", color="Category", title="Daily Total Inventory Distribution", nbins=40, barmode="overlay", opacity=0.75, template=plt_template)
        render_static_chart(fig5, daily_inv_dist)
    with r3c2:
        inv_piv = filtered_df.pivot_table(values='Inventory Level', index='Region', columns='Category', aggfunc='mean')
        fig6 = px.imshow(inv_piv, text_auto=True, title="Average Inventory Matrix (Region vs Category)", aspect="auto", color_continuous_scale="Oranges", template=plt_template)
        render_clickable_chart(fig6, filtered_df, 'Category', 'Category', 'i6')

# --- TAB 2: FINANCIAL ---
with tab_fin:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Revenue", f"${filtered_df['Revenue'].sum():,.2f}")
    m2.metric("Average Price", f"${filtered_df['Price'].mean():,.2f}")
    m3.metric("Total Units Sold", f"{filtered_df['Units Sold'].sum():,}")
    m4.metric("Avg Discount Applied", f"{filtered_df['Discount'].mean():.1f}%")
    st.divider()

    daily_rev = filtered_df.groupby('Date', as_index=False)['Revenue'].sum()
    daily_rev['7-Day MA'] = daily_rev['Revenue'].rolling(window=7).mean()
    fig_f1 = go.Figure()
    fig_f1.add_trace(go.Scatter(x=daily_rev['Date'], y=daily_rev['Revenue'], mode='lines', name='Daily Rev', line=dict(color='#1F77B4')))
    fig_f1.add_trace(go.Scatter(x=daily_rev['Date'], y=daily_rev['7-Day MA'], mode='lines', name='7-Day MA', line=dict(color='orange', width=3)))
    fig_f1.update_layout(title="Daily Revenue Trend & Moving Average", template=plt_template, hovermode="x unified")
    render_clickable_chart(fig_f1, filtered_df, 'Date', 'Date', 'f1')

    r1c1, r1c2 = st.columns(2)
    with r1c1:
        rev_cat = filtered_df.groupby('Category', as_index=False)['Revenue'].sum()
        fig_f2 = px.pie(rev_cat, names='Category', values='Revenue', hole=0.4, title="Revenue Share by Category", template=plt_template)
        render_clickable_chart(fig_f2, filtered_df, 'Category', 'Category', 'f2')
    with r1c2:
        disc_val = filtered_df.groupby('Category', as_index=False)['Discount Value'].sum()
        fig_f3 = px.bar(disc_val, x='Category', y='Discount Value', title="Total Value of Discounts Given (Lost Revenue)", color='Category', template=plt_template)
        render_clickable_chart(fig_f3, disc_val, 'Category', 'Category', 'f3')

    r2c1, r2c2 = st.columns(2)
    with r2c1:
        price_agg = filtered_df.groupby(['Category', 'Price'], as_index=False)['Units Sold'].mean()
        fig_f4 = px.scatter(price_agg, x="Price", y="Units Sold", color="Category", title="Price Elasticity (Avg Sold per Price Point)", opacity=0.8, template=plt_template)
        render_clickable_chart(fig_f4, price_agg, 'Price', 'Price', 'f4')
    with r2c2:
        aov_df = filtered_df.groupby('Category', as_index=False)['Revenue'].mean()
        fig_f5 = px.bar(aov_df, x='Category', y='Revenue', title="Average Transaction Value (AOV)", color='Category', template=plt_template)
        render_clickable_chart(fig_f5, aov_df, 'Category', 'Category', 'f5')

    r3c1, r3c2 = st.columns(2)
    with r3c1:
        fig_f6 = px.box(filtered_df, x="Region", y="Revenue", title="Revenue Spread per Region", color="Region", template=plt_template)
        render_clickable_chart(fig_f6, filtered_df, 'Region', 'Region', 'f6')
    with r3c2:
        daily_rev['CumRev'] = daily_rev['Revenue'].cumsum()
        fig_f7 = px.area(daily_rev, x='Date', y='CumRev', title="Cumulative Revenue Growth", color_discrete_sequence=['#9467BD'], template=plt_template)
        render_clickable_chart(fig_f7, daily_rev, 'Date', 'Date', 'f7')

# --- TAB 3: LOCATION ---
with tab_loc:
    reg_sales = filtered_df.groupby('Region')['Units Sold'].sum()
    c1, c2, c3 = st.columns(3)
    c1.metric("Top Performing Region", reg_sales.idxmax())
    c2.metric("Lowest Performing Region", reg_sales.idxmin())
    c3.metric("Avg Units Sold per Region", f"{reg_sales.mean():,.0f}")
    st.divider()

    r1c1, r1c2 = st.columns(2)
    with r1c1:
        fig_l1 = px.bar(reg_sales.reset_index(), x='Region', y='Units Sold', color='Region', title="Total Units Sold by Region", template=plt_template)
        render_clickable_chart(fig_l1, filtered_df, 'Region', 'Region', 'l1')
    with r1c2:
        fig_l2 = px.treemap(filtered_df, path=['Region', 'Category'], values='Units Sold', title="Regional Category Hierarchy", color='Units Sold', color_continuous_scale='Blues', template=plt_template)
        render_clickable_chart(fig_l2, filtered_df, 'Region', 'Region', 'l2')

    r2c1, r2c2 = st.columns(2)
    with r2c1:
        piv_loc = filtered_df.pivot_table(values='Revenue', index='Region', columns='Category', aggfunc='sum')
        fig_l3 = px.imshow(piv_loc, text_auto=True, title="Revenue Heatmap (Region vs Category)", aspect="auto", template=plt_template)
        render_clickable_chart(fig_l3, filtered_df, 'Category', 'Category', 'l3')
    with r2c2:
        reg_trend = filtered_df.groupby(['Date', 'Region'], as_index=False)['Units Sold'].sum()
        fig_l4 = px.line(reg_trend, x='Date', y='Units Sold', color='Region', title="Daily Regional Demand Trends", template=plt_template)
        render_clickable_chart(fig_l4, filtered_df, 'Date', 'Date', 'l4')

    r3c1, r3c2 = st.columns(2)
    with r3c1:
        disc_reg = filtered_df.groupby(['Region', 'Discount'], as_index=False)['Units Sold'].mean()
        fig_l5 = px.scatter(disc_reg, x="Discount", y="Units Sold", color="Region", title="Impact of Discount on Avg Regional Sales", opacity=0.8, template=plt_template)
        render_clickable_chart(fig_l5, disc_reg, 'Discount', 'Discount', 'l5')
    with r3c2:
        reg_inv = filtered_df.groupby('Region', as_index=False)['Inventory Level'].sum()
        fig_l6 = px.pie(reg_inv, names='Region', values='Inventory Level', hole=0.5, title="Regional Inventory Distribution", template=plt_template)
        render_clickable_chart(fig_l6, filtered_df, 'Region', 'Region', 'l6')

# --- TAB 4: DOMAIN PREDICTIONS ---
with tab_pred:
    st.markdown("### 30-Day Forward Projections by Business Domain")
    sub_fin, sub_loc, sub_mat = st.tabs(["Finance Forecast", "Location Forecast", "Materials Forecast"])
    
    with sub_fin:
        hist_rev, fut_rev = generate_forecast(filtered_df, 'Date', 'Revenue', agg='sum')
        l30, n30 = hist_rev['Revenue'].tail(30).sum(), fut_rev['Forecast'].sum()
        c1, c2, c3 = st.columns(3)
        c1.metric("Past 30-Day Revenue", f"${l30:,.2f}")
        c2.metric("Projected 30-Day Revenue", f"${n30:,.2f}", f"{((n30-l30)/l30*100):.1f}%")
        c3.metric("Avg Daily Projection", f"${fut_rev['Forecast'].mean():,.2f}")
        st.divider()

        fig_pf1 = go.Figure()
        fig_pf1.add_trace(go.Scatter(x=hist_rev['Date'].tail(90), y=hist_rev['Revenue'].tail(90), name='Historical'))
        fig_pf1.add_trace(go.Scatter(x=fut_rev['Date'], y=fut_rev['Forecast'], name='Projected', line=dict(dash='dash')))
        fig_pf1.update_layout(title="Overall Revenue Projection", template=plt_template)
        render_clickable_chart(fig_pf1, fut_rev, 'Date', 'Date', 'pf1')
        
        r1, r2 = st.columns(2)
        with r1:
            cat_f = []
            for cat in filtered_df['Category'].unique():
                _, f = generate_forecast(filtered_df[filtered_df['Category'] == cat], 'Date', 'Revenue')
                f['Category'] = cat
                cat_f.append(f)
            cat_f_df = pd.concat(cat_f) if cat_f else pd.DataFrame()
            fig_pf2 = px.bar(cat_f_df, x='Date', y='Forecast', color='Category', title="Daily Revenue Composition", template=plt_template)
            render_clickable_chart(fig_pf2, cat_f_df, 'Date', 'Date', 'pf2')
        with r2:
            comp = pd.DataFrame({'Period': ['Last 30', 'Next 30'], 'Revenue': [l30, n30]})
            fig_pf3 = px.bar(comp, x='Period', y='Revenue', color='Period', title="Revenue Shift Volume", text_auto='.2s', template=plt_template)
            render_clickable_chart(fig_pf3, comp, 'Period', 'Period', 'pf3')

        r3, r4 = st.columns(2)
        with r3:
            fut_rev['CumProj'] = fut_rev['Forecast'].cumsum()
            fig_pf4 = px.area(fut_rev, x='Date', y='CumProj', title="Cumulative Projected Revenue", template=plt_template)
            render_clickable_chart(fig_pf4, fut_rev, 'Date', 'Date', 'pf4')
        with r4:
            fig_pf5 = px.histogram(fut_rev, x='Forecast', title="Expected Daily Revenue Spread", nbins=15, template=plt_template)
            render_static_chart(fig_pf5, fut_rev)
            
        fig_pf6 = px.box(cat_f_df, x="Category", y="Forecast", title="Projected Daily Variance by Category", color="Category", template=plt_template)
        render_clickable_chart(fig_pf6, cat_f_df, 'Category', 'Category', 'pf6')

    with sub_loc:
        reg_f = []
        for reg in filtered_df['Region'].unique():
            _, f = generate_forecast(filtered_df[filtered_df['Region'] == reg], 'Date', 'Units Sold')
            f['Region'] = reg
            reg_f.append(f)
        all_rf = pd.concat(reg_f) if reg_f else pd.DataFrame()
        
        fig_pl1 = px.area(all_rf, x='Date', y='Forecast', color='Region', title="Regional Demand Volume", template=plt_template)
        render_clickable_chart(fig_pl1, all_rf, 'Date', 'Date', 'pl1')

        r1, r2 = st.columns(2)
        with r1:
            r_tot = all_rf.groupby('Region')['Forecast'].sum().reset_index()
            fig_pl2 = px.pie(r_tot, names='Region', values='Forecast', hole=0.4, title="Projected Market Share", template=plt_template)
            render_clickable_chart(fig_pl2, all_rf, 'Region', 'Region', 'pl2')
        with r2:
            all_rf['DoW'] = all_rf['Date'].dt.day_name()
            avg_dow = all_rf.groupby(['Region', 'DoW'])['Forecast'].mean().reset_index()
            fig_pl3 = px.bar(avg_dow, x='DoW', y='Forecast', color='Region', barmode='group', title="Expected Weekly Spikes", template=plt_template)
            render_clickable_chart(fig_pl3, all_rf, 'DoW', 'Day', 'pl3')
            
        r3, r4 = st.columns(2)
        with r3:
            fig_pl4 = px.line(all_rf, x='Date', y='Forecast', color='Region', title="Individual Region Trajectories", template=plt_template)
            render_clickable_chart(fig_pl4, all_rf, 'Date', 'Date', 'pl4')
        with r4:
            rf_piv = all_rf.pivot_table(values='Forecast', index='Region', columns='Date')
            fig_pl5 = px.imshow(rf_piv, title="Demand Heatmap (Next 30 Days)", aspect="auto", template=plt_template)
            render_clickable_chart(fig_pl5, all_rf, 'Date', 'Date', 'pl5')

    with sub_mat:
        hi, fi = generate_forecast(filtered_df, 'Date', 'Inventory Level', agg='mean')
        dep = [hi['Inventory Level'].iloc[-1] - (i * fi['Forecast'].mean()*0.05) for i in range(len(fi))] if not fi.empty else []
        
        fig_pm1 = go.Figure()
        fig_pm1.add_trace(go.Scatter(x=hi['Date'].tail(60), y=hi['Inventory Level'].tail(60), name='Historical Avg'))
        fig_pm1.add_trace(go.Scatter(x=fi['Date'], y=dep, name='Proj Depletion', line=dict(dash='dot', color='red')))
        fig_pm1.update_layout(title="Overall Inventory Depletion Curve", template=plt_template)
        render_clickable_chart(fig_pm1, fi, 'Date', 'Date', 'pm1')

        sup, risk = [], []
        for cat in filtered_df['Category'].unique():
            c_df = filtered_df[filtered_df['Category'] == cat]
            ci = c_df['Inventory Level'].iloc[-1]
            _, fs = generate_forecast(c_df, 'Date', 'Units Sold')
            if not fs.empty:
                dd = fs['Forecast'].mean()
                sup.append({'Category': cat, 'Days': min(ci/dd if dd>0 else 999, 100)})
                risk.append({'Category': cat, 'Stock': c_df['Inventory Level'].mean(), 'Demand': fs['Forecast'].sum(), 'Status': 'At Risk' if fs['Forecast'].sum() > c_df['Inventory Level'].mean() else 'Safe'})
            
        r1, r2 = st.columns(2)
        rdf = pd.DataFrame(risk) if risk else pd.DataFrame()
        sdf = pd.DataFrame(sup) if sup else pd.DataFrame()

        with r1:
            fig_pm2 = px.bar(sdf.sort_values('Days') if not sdf.empty else sdf, x='Days', y='Category', orientation='h', title="Est. Days of Supply", color='Days', color_continuous_scale='Reds_r', template=plt_template)
            render_clickable_chart(fig_pm2, sdf, 'Days', 'Days of Supply', 'pm2')
        with r2:
            fig_pm3 = px.scatter(rdf, x='Demand', y='Stock', color='Category', size='Demand', title="Shortage Risk (Demand vs Stock)", template=plt_template)
            if not rdf.empty:
                max_v = max(rdf['Demand'].max(), rdf['Stock'].max())
                fig_pm3.add_shape(type="line", x0=0, y0=0, x1=max_v, y1=max_v, line=dict(color="red", dash="dash"))
            render_clickable_chart(fig_pm3, rdf, 'Demand', 'Demand', 'pm3')

        r3, r4 = st.columns(2)
        with r3:
            if not rdf.empty:
                stat_c = rdf['Status'].value_counts().reset_index()
                fig_pm4 = px.pie(stat_c, names='Status', values='count', hole=0.5, title="Safe vs At-Risk Categories", color='Status', color_discrete_map={'Safe':'green', 'At Risk':'red'}, template=plt_template)
                render_clickable_chart(fig_pm4, rdf, 'Status', 'Status', 'pm4')
        with r4:
            if not rdf.empty:
                fig_pm5 = px.treemap(rdf, path=['Status', 'Category'], values='Demand', title="Reorder Priority Hierarchy", color='Demand', color_continuous_scale='Reds', template=plt_template)
                render_clickable_chart(fig_pm5, rdf, 'Status', 'Status', 'pm5')

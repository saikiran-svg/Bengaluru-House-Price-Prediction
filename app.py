import streamlit as st
import pandas as pd
import joblib
import mysql.connector
import plotly.express as px
import plotly.graph_objects as go

# =========================================================
# PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="Bengaluru Real Estate AI Valuation",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Glassmorphism & Modern Dashboard Theme)
st.markdown("""
<style>
    /* Dark Theme Accent Header */
    .hero-banner {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #3B82F6 100%);
        padding: 2.5rem 2rem;
        border-radius: 16px;
        color: #FFFFFF;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
    }
    .hero-banner h1 {
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.025em;
        margin: 0;
        color: #FFFFFF !important;
    }
    .hero-banner p {
        color: #94A3B8;
        font-size: 1.05rem;
        margin-top: 0.5rem;
        margin-bottom: 0;
    }
    
    /* Input Container Box */
    .input-card {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }

    /* Status Badges */
    .status-pill {
        display: inline-block;
        padding: 0.6rem 1.2rem;
        border-radius: 50px;
        font-weight: 700;
        font-size: 0.95rem;
        text-align: center;
    }
    .pill-green { background-color: #064E3B; color: #34D399; border: 1px solid #059669; }
    .pill-yellow { background-color: #78350F; color: #FBBF24; border: 1px solid #D97706; }
    .pill-red { background-color: #7F1D1D; color: #FCA5A5; border: 1px solid #DC2626; }
</style>
""", unsafe_allow_html=True)


# =========================================================
# DATA & MODEL LOADERS
# =========================================================
@st.cache_resource
def load_model():
    try:
        return joblib.load("bengaluru_house_price_model.pkl")
    except Exception as e:
        return None

@st.cache_data
def load_dataset():
    try:
        df = pd.read_csv("Bengaluru_House_Data.csv")
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
        df["total_sqft_numeric"] = pd.to_numeric(
            df["total_sqft"].astype(str).str.extract(r"(\d+\.?\d*)")[0], 
            errors="coerce"
        )
        df["bhk_numeric"] = pd.to_numeric(
            df["size"].astype(str).str.extract(r"(\d+)")[0], 
            errors="coerce"
        )
        return df
    except Exception as e:
        return pd.DataFrame()

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="bengaluru_house_db"
    )

model = load_model()
df = load_dataset()


# =========================================================
# HEADER BANNER
# =========================================================
st.markdown("""
<div class="hero-banner">
    <h1>🏢 Bengaluru Real Estate Valuation Intelligence</h1>
    <p>Predict property valuation using machine learning models and analyze live market performance indicators.</p>
</div>
""", unsafe_allow_html=True)


# =========================================================
# TOP METRICS BANNER
# =========================================================
if not df.empty:
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Listings", f"{len(df):,}")
    with m2:
        st.metric("Avg Listing Price", f"₹ {df['price'].mean():.2f} L")
    with m3:
        st.metric("Avg Property Size", f"{df['total_sqft_numeric'].mean():.0f} sqft")
    with m4:
        st.metric("Active Locations", f"{df['location'].nunique():,}")

st.divider()

# =========================================================
# NAVIGATION TABS
# =========================================================
tab_estimator, tab_analytics, tab_history = st.tabs([
    "🔮 Price Estimator", 
    "📈 Market Analytics", 
    "📜 Search Logs"
])

# ---------------------------------------------------------
# TAB 1: PREDICTION ENGINE
# ---------------------------------------------------------
with tab_estimator:
    col_input, col_output = st.columns([1, 1], gap="large")
    
    with col_input:
        st.markdown("### 📝 Enter Property Details")
        
        with st.form("val_form"):
            if not df.empty and "location" in df.columns:
                loc_list = sorted(df["location"].dropna().unique().tolist())
                location = st.selectbox("📍 Location", options=loc_list)
            else:
                location = st.text_input("📍 Location", placeholder="e.g. Whitefield")

            total_sqft = st.number_input(
                "📐 Built-up Area (Sq. Ft.)",
                min_value=100.0,
                max_value=10000.0,
                value=1200.0,
                step=50.0
            )

            c1, c2 = st.columns(2)
            with c1:
                bhk = st.number_input("🛏️ BHK", min_value=1, max_value=10, value=2)
            with c2:
                bath = st.number_input("🚿 Bathrooms", min_value=1, max_value=10, value=2)

            asking_price = st.number_input(
                "💰 Asking Price (₹ in Lakhs)",
                min_value=1.0,
                value=65.0,
                step=1.0
            )

            submit_btn = st.form_submit_button("🔥 Calculate Market Value", use_container_width=True)

    with col_output:
        st.markdown("### 📊 Valuation Verdict")
        
        if submit_btn:
            if not location or location.strip() == "":
                st.warning("Please enter or select a valid location.")
            elif model is None:
                st.error("Model file `bengaluru_house_price_model.pkl` could not be loaded.")
            else:
                input_df = pd.DataFrame({
                    "location": [location],
                    "total_sqft": [total_sqft],
                    "bhk": [bhk],
                    "bath": [bath]
                })

                try:
                    predicted_val = float(model.predict(input_df)[0])
                except Exception as ex:
                    st.error(f"Prediction failed: {ex}")
                    st.stop()

                diff = ((asking_price - predicted_val) / predicted_val) * 100 if predicted_val > 0 else 0

                if diff <= -10:
                    badge = '<div class="status-pill pill-green">🟢 Undervalued Opportunity</div>'
                    rating_str = "Undervalued"
                elif diff <= 10:
                    badge = '<div class="status-pill pill-yellow">🟡 Fair Market Price</div>'
                    rating_str = "Fair Value"
                else:
                    badge = '<div class="status-pill pill-red">🔴 Overpriced Listing</div>'
                    rating_str = "Overpriced"

                # Metric comparisons
                res1, res2 = st.columns(2)
                with res1:
                    st.metric("Estimated Market Value", f"₹ {predicted_val:.2f} Lakhs")
                    st.metric("Asking Price", f"₹ {asking_price:.2f} Lakhs")
                with res2:
                    st.metric("Price Variance", f"{diff:+.2f}%")
                    st.markdown("**Assessment:**")
                    st.markdown(badge, unsafe_allow_html=True)

                # Database Logging
                try:
                    conn = get_connection()
                    cursor = conn.cursor()
                    insert_query = """
                        INSERT INTO search_history
                        (location, total_sqft, bhk, bath, asking_price, predicted_price, investment_rating)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_query, (
                        location, float(total_sqft), int(bhk), int(bath),
                        float(asking_price), float(predicted_val), rating_str
                    ))
                    conn.commit()

                    export_cursor = conn.cursor(dictionary=True)
                    export_cursor.execute("SELECT * FROM search_history ORDER BY searched_at DESC")
                    records = export_cursor.fetchall()
                    export_cursor.close()
                    cursor.close()
                    conn.close()

                    pd.DataFrame(records).to_csv("search_history.csv", index=False)
                    st.toast("Saved prediction record successfully!", icon="✅")
                except mysql.connector.Error as db_err:
                    st.error(f"MySQL Error: {db_err}")

        else:
            st.info("👈 Fill out the details on the left and click **Calculate Market Value** to render the AI analysis.")


# ---------------------------------------------------------
# TAB 2: INTERACTIVE DASHBOARD (PLOTLY)
# ---------------------------------------------------------
with tab_analytics:
    if not df.empty:
        g1, g2 = st.columns(2)

        with g1:
            st.markdown("##### 📍 Top 10 High-Value Locations")
            top_locs = (
                df.dropna(subset=["location", "price"])
                .groupby("location")["price"]
                .mean()
                .nlargest(10)
                .reset_index()
            )
            fig_loc = px.bar(
                top_locs, 
                x="price", 
                y="location", 
                orientation="h",
                labels={"price": "Avg Price (Lakhs)", "location": "Location"},
                color="price",
                color_continuous_scale="Viridis"
            )
            fig_loc.update_layout(yaxis={'categoryorder': 'total ascending'}, margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig_loc, use_container_width=True)

        with g2:
            st.markdown("##### 🛏️ Price Distribution by BHK")
            bhk_df = df.dropna(subset=["bhk_numeric", "price"])
            bhk_df = bhk_df[bhk_df["bhk_numeric"] <= 6]
            fig_bhk = px.box(
                bhk_df, 
                x="bhk_numeric", 
                y="price",
                labels={"bhk_numeric": "BHK Count", "price": "Price (Lakhs)"},
                color="bhk_numeric"
            )
            fig_bhk.update_layout(showlegend=False, margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig_bhk, use_container_width=True)

        st.markdown("##### 📐 Area (Sqft) vs Price Correlation")
        sqft_filtered = df[(df["total_sqft_numeric"] < 5000) & (df["price"] < 500)].dropna(subset=["total_sqft_numeric", "price"])
        fig_scatter = px.scatter(
            sqft_filtered, 
            x="total_sqft_numeric", 
            y="price", 
            color="bhk_numeric",
            hover_data=["location"],
            labels={"total_sqft_numeric": "Total Square Feet", "price": "Price (Lakhs)", "bhk_numeric": "BHK"},
            opacity=0.7
        )
        fig_scatter.update_layout(margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.warning("Dataset not available for generating dashboard charts.")


# ---------------------------------------------------------
# TAB 3: SEARCH HISTORY & DATABASE RECORDS
# ---------------------------------------------------------
with tab_history:
    st.markdown("### 📜 Prediction Log")
    try:
        conn = get_connection()
        hist_df = pd.read_sql("SELECT * FROM search_history ORDER BY searched_at DESC LIMIT 100", conn)
        conn.close()
        
        if not hist_df.empty:
            st.dataframe(
                hist_df,
                column_config={
                    "id": "ID",
                    "location": "Location",
                    "total_sqft": "Area (Sqft)",
                    "bhk": "BHK",
                    "bath": "Bathrooms",
                    "asking_price": st.column_config.NumberColumn("Asking Price", format="₹ %.2f L"),
                    "predicted_price": st.column_config.NumberColumn("Predicted Value", format="₹ %.2f L"),
                    "investment_rating": "Rating",
                    "searched_at": "Timestamp"
                },
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No query logs stored yet.")
    except Exception as e:
        st.warning("Database unavailable. Showing local CSV export if available.")
        try:
            csv_df = pd.read_csv("search_history.csv")
            st.dataframe(csv_df, use_container_width=True)
        except Exception:
            st.error("No historical log records found.")

import os
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import mysql.connector
from pathlib import Path
import plotly.express as px


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Smart Real Estate Analytics",
    page_icon="🏠",
    layout="wide"
)


# =========================================================
# PROJECT PATHS
# =========================================================

BASE_DIR = Path(__file__).parent
PROJECT_ROOT = BASE_DIR.parent

MODEL_PATH = BASE_DIR / "model" / "bengaluru_house_price_model.pkl"
DATA_PATH = BASE_DIR / "data" / "Bengaluru_House_Data.csv"
CSS_PATH = PROJECT_ROOT / "frontend" / "style.css"


# =========================================================
# LOAD CSS
# =========================================================

if CSS_PATH.exists():

    css = CSS_PATH.read_text(encoding="utf-8")

    st.markdown(
        "<style>" + css + "</style>",
        unsafe_allow_html=True
    )

else:

    st.error("❌ frontend/style.css was not found.")
    st.stop()


# =========================================================
# CHECK MODEL
# =========================================================

if not MODEL_PATH.exists():

    st.error(
        "❌ bengaluru_house_price_model.pkl was not found."
    )

    st.stop()


# =========================================================
# CHECK DATASET
# =========================================================

if not DATA_PATH.exists():

    st.error(
        "❌ Bengaluru_House_Data.csv was not found."
    )

    st.stop()


# =========================================================
# LOAD MODEL
# =========================================================

@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)


try:

    model = load_model()

except Exception as error:

    st.error(
        "❌ Error loading the machine learning model."
    )

    st.exception(error)
    st.stop()


# =========================================================
# LOAD DATASET
# =========================================================

@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)


try:

    df = load_data()

except Exception as error:

    st.error(
        "❌ Error loading Bengaluru_House_Data.csv."
    )

    st.exception(error)
    st.stop()


# =========================================================
# CLEAN DATA
# =========================================================

if "location" not in df.columns:

    st.error(
        "❌ Location column not found in dataset."
    )

    st.stop()


df["location"] = (
    df["location"]
    .astype(str)
    .str.strip()
)


# =========================================================
# PRICE
# =========================================================

if "price" in df.columns:

    df["price"] = pd.to_numeric(
        df["price"],
        errors="coerce"
    )


# =========================================================
# AREA CONVERSION
# =========================================================

def convert_sqft(value):

    try:

        value = str(value).strip()

        if "-" in value:

            parts = value.split("-")

            first = float(parts[0].strip())
            second = float(parts[1].strip())

            return (first + second) / 2

        return float(value)

    except Exception:

        return np.nan


if "total_sqft" in df.columns:

    df["area_numeric"] = (
        df["total_sqft"]
        .apply(convert_sqft)
    )

else:

    df["area_numeric"] = np.nan


# =========================================================
# BHK
# =========================================================

if "size" in df.columns:

    df["bhk"] = pd.to_numeric(
        df["size"]
        .astype(str)
        .str.extract(
            r"(\d+)",
            expand=False
        ),
        errors="coerce"
    )

else:

    df["bhk"] = np.nan


# =========================================================
# LOCATIONS
# =========================================================

locations = sorted(
    df["location"]
    .dropna()
    .unique()
    .tolist()
)


if len(locations) == 0:

    st.error(
        "❌ No locations found in dataset."
    )

    st.stop()


# =========================================================
# MYSQL CONNECTION
# =========================================================

def get_connection():

    return mysql.connector.connect(
        host=os.environ.get("MYSQL_HOST", "localhost"),
        port=int(os.environ.get("MYSQL_PORT", "3306")),
        user=os.environ.get("MYSQL_USER", "root"),
        password=os.environ.get("MYSQL_PASSWORD", ""),
        database=os.environ.get("MYSQL_DATABASE", "bengaluru_house_db")
    )


# =========================================================
# SAVE PREDICTION TO MYSQL
# =========================================================

def save_prediction(
    location,
    total_sqft,
    bhk,
    bath,
    asking_price,
    predicted_price,
    rating
):

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        query = """
        INSERT INTO search_history
        (
            location,
            total_sqft,
            bhk,
            bath,
            asking_price,
            predicted_price,
            investment_rating
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        """

        values = (
            location,
            float(total_sqft),
            int(bhk),
            int(bath),
            float(asking_price),
            float(predicted_price),
            rating
        )

        cursor.execute(query, values)
        connection.commit()

        return True, ""

    except Exception as error:

        if connection:
            connection.rollback()

        return False, str(error)

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# GET HISTORY
# =========================================================

def get_history():

    connection = None

    try:

        connection = get_connection()

        query = """
        SELECT
            id,
            location,
            total_sqft,
            bhk,
            bath,
            asking_price,
            predicted_price,
            investment_rating,
            searched_at
        FROM search_history
        ORDER BY searched_at DESC
        """

        history = pd.read_sql(
            query,
            connection
        )

        return history

    finally:

        if connection:
            connection.close()


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title(
    "🏠 Smart Real Estate Analytics"
)

st.sidebar.write(
    "AI-Powered Investment & Price Prediction Engine"
)

st.sidebar.divider()


page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Price Estimator",
        "📊 Market Analysis",
        "📜 Prediction History"
    ]
)


st.sidebar.divider()

st.sidebar.write(
    "🤖 Model"
)

st.sidebar.write(
    "Random Forest Regression"
)


# =========================================================
# PRICE ESTIMATOR
# =========================================================

if page == "🏠 Price Estimator":

    st.title(
        "🏠 Smart Real Estate Analytics"
    )

    st.write(
        "AI-Powered Investment & Price Prediction Engine"
    )

    st.divider()


    # -----------------------------------------------------
    # METRICS
    # -----------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "🏠 Total Listings",
            f"{len(df):,}"
        )

    with col2:

        if "price" in df.columns:

            avg_price = (
                df["price"]
                .dropna()
                .mean()
            )

        else:

            avg_price = 0

        st.metric(
            "💰 Average Price",
            f"₹ {avg_price:.2f} L"
        )

    with col3:

        st.metric(
            "📍 Locations",
            f"{len(locations):,}"
        )

    with col4:

        st.metric(
            "🤖 Model",
            "Random Forest Regression"
        )


    st.divider()


    # -----------------------------------------------------
    # INPUTS
    # -----------------------------------------------------

    st.subheader(
        "🔮 Property Price Estimator"
    )


    col1, col2 = st.columns(2)


    with col1:

        location = st.selectbox(
            "📍 Location",
            locations
        )

        total_sqft = st.number_input(
            "📐 Built-up Area (Sq. Ft.)",
            min_value=100.0,
            max_value=10000.0,
            value=1200.0,
            step=50.0
        )


    with col2:

        bhk = st.number_input(
            "🛏️ BHK",
            min_value=1,
            max_value=10,
            value=2,
            step=1
        )

        bath = st.number_input(
            "🚿 Bathrooms",
            min_value=1,
            max_value=10,
            value=2,
            step=1
        )


    asking_price = st.number_input(
        "💰 Asking Price (₹ Lakhs)",
        min_value=1.0,
        max_value=1000.0,
        value=65.0,
        step=1.0
    )


    st.write("")


    calculate = st.button(
        "🔥 Calculate Market Value",
        type="primary",
        use_container_width=True
    )


    # =====================================================
    # PREDICTION
    # =====================================================

    if calculate:

        try:

            input_data = pd.DataFrame({

                "location": [location],

                "total_sqft": [total_sqft],

                "bhk": [bhk],

                "bath": [bath]

            })


            predicted_price = float(
                model.predict(input_data)[0]
            )


            if not np.isfinite(predicted_price):

                raise ValueError(
                    "Invalid model prediction."
                )


            # ---------------------------------------------
            # VARIANCE
            # ---------------------------------------------

            variance = (
                (
                    asking_price
                    - predicted_price
                )
                / predicted_price
            ) * 100


            # ---------------------------------------------
            # RATING
            # ---------------------------------------------

            if variance <= -10:

                rating = "Undervalued"

                message = (
                    "The property is priced below "
                    "the estimated market value."
                )

            elif variance >= 10:

                rating = "Overpriced"

                message = (
                    "The asking price is higher "
                    "than the estimated market value."
                )

            else:

                rating = "Fair Market Price"

                message = (
                    "The asking price is close to "
                    "the estimated market value."
                )


            st.divider()

            st.subheader(
                "📊 Valuation Result"
            )


            r1, r2, r3 = st.columns(3)


            with r1:

                st.metric(
                    "🤖 Estimated Market Value",
                    f"₹ {predicted_price:.2f} L"
                )


            with r2:

                st.metric(
                    "💰 Asking Price",
                    f"₹ {asking_price:.2f} L"
                )


            with r3:

                st.metric(
                    "📈 Price Difference",
                    f"{variance:+.2f}%"
                )


            if rating == "Undervalued":

                st.success(
                    f"🟢 {rating} — {message}"
                )

            elif rating == "Overpriced":

                st.error(
                    f"🔴 {rating} — {message}"
                )

            else:

                st.warning(
                    f"🟡 {rating} — {message}"
                )


            # ---------------------------------------------
            # SAVE TO MYSQL
            # ---------------------------------------------

            saved, error_message = save_prediction(

                location,
                total_sqft,
                bhk,
                bath,
                asking_price,
                predicted_price,
                rating

            )


            if saved:

                st.success(
                    "✅ Prediction saved to MySQL search history."
                )

            else:

                st.error(
                    "Prediction calculated, "
                    "but MySQL storage failed."
                )

                st.code(error_message)


        except Exception as error:

            st.error(
                "❌ Market value calculation failed."
            )

            st.exception(error)


# =========================================================
# MARKET ANALYSIS
# =========================================================

elif page == "📊 Market Analysis":

    st.title(
        "📊 Smart Real Estate Market Analysis"
    )

    st.write(
        "Explore property prices, BHK trends "
        "and area-price relationships."
    )

    st.divider()


    # -----------------------------------------------------
    # FILTER
    # -----------------------------------------------------

    selected_location = st.selectbox(
        "📍 Location Filter",
        ["All Locations"] + locations
    )


    if selected_location == "All Locations":

        analysis_df = df.copy()

    else:

        analysis_df = df[
            df["location"] == selected_location
        ].copy()


    # -----------------------------------------------------
    # METRICS
    # -----------------------------------------------------

    c1, c2, c3, c4 = st.columns(4)


    with c1:

        st.metric(
            "🏠 Properties",
            f"{len(analysis_df):,}"
        )


    with c2:

        average = (
            analysis_df["price"]
            .dropna()
            .mean()
        )

        st.metric(
            "💰 Average Price",
            f"₹ {average:.2f} L"
        )


    with c3:

        average_area = (
            analysis_df["area_numeric"]
            .dropna()
            .mean()
        )

        st.metric(
            "📐 Average Area",
            f"{average_area:.0f} sqft"
        )


    with c4:

        highest = (
            analysis_df["price"]
            .dropna()
            .max()
        )

        st.metric(
            "💎 Highest Price",
            f"₹ {highest:.2f} L"
        )


    st.divider()


    # =====================================================
    # LOCATION CHART
    # =====================================================

    st.subheader(
        "📍 Top 10 Locations by Average Price"
    )


    location_chart = (

        df
        .dropna(
            subset=["location", "price"]
        )
        .groupby("location")["price"]
        .mean()
        .sort_values(
            ascending=False
        )
        .head(10)
        .reset_index()

    )


    if not location_chart.empty:

        fig1 = px.bar(

            location_chart,

            x="price",

            y="location",

            orientation="h",

            title="Average Price by Location",

            labels={
                "price": "Average Price (₹ Lakhs)",
                "location": "Location"
            }

        )

        fig1.update_layout(
            yaxis={
                "categoryorder":
                "total ascending"
            }
        )

        st.plotly_chart(
            fig1,
            use_container_width=True
        )

    else:

        st.info(
            "No location data available."
        )


    # =====================================================
    # BHK CHART
    # =====================================================

    st.subheader(
        "🛏️ Average Price by BHK"
    )


    bhk_chart = (

        analysis_df
        .dropna(
            subset=["bhk", "price"]
        )
        .groupby("bhk")["price"]
        .mean()
        .reset_index()
        .sort_values("bhk")

    )


    if not bhk_chart.empty:

        fig2 = px.bar(

            bhk_chart,

            x="bhk",

            y="price",

            title="Average Price by BHK",

            labels={
                "bhk": "BHK",
                "price": "Average Price (₹ Lakhs)"
            }

        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

    else:

        st.info(
            "No BHK data available."
        )


    # =====================================================
    # AREA VS PRICE
    # =====================================================

    st.subheader(
        "📐 Area vs Price"
    )


    scatter_df = (

        analysis_df[
            [
                "area_numeric",
                "price",
                "bhk"
            ]
        ]
        .dropna()
        .head(3000)

    )


    if not scatter_df.empty:

        fig3 = px.scatter(

            scatter_df,

            x="area_numeric",

            y="price",

            color="bhk",

            title="Built-up Area vs Price",

            labels={
                "area_numeric":
                    "Built-up Area (Sq. Ft.)",

                "price":
                    "Price (₹ Lakhs)",

                "bhk":
                    "BHK"
            }

        )

        st.plotly_chart(
            fig3,
            use_container_width=True
        )

    else:

        st.info(
            "No area-price data available."
        )


# =========================================================
# PREDICTION HISTORY
# =========================================================

elif page == "📜 Prediction History":

    st.title(
        "📜 Prediction History"
    )

    st.write(
        "Predictions saved in MySQL."
    )

    st.divider()


    try:

        history = get_history()


        st.metric(
            "🔢 Total Predictions",
            f"{len(history):,}"
        )


        st.write("")


        if history.empty:

            st.info(
                "No prediction history available."
            )

        else:

            st.dataframe(
                history,
                use_container_width=True,
                hide_index=True
            )


            st.download_button(

                "⬇️ Download History",

                history.to_csv(
                    index=False
                ),

                "prediction_history.csv",

                "text/csv"

            )


    except Exception as error:

        st.error(
            "❌ Could not connect to MySQL."
        )

        st.code(
            str(error)
        )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">
        Smart Real Estate Analytics
        <br>
        AI-Powered Investment & Price Prediction Engine •
        Streamlit • Machine Learning • MySQL
    </div>
    """,
    unsafe_allow_html=True
)
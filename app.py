import streamlit as st
import pandas as pd
import joblib
import mysql.connector


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Bengaluru House Price Prediction",
    page_icon="🏠",
    layout="wide"
)


# =========================================================
# MYSQL CONNECTION
# =========================================================

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="bengaluru_house_db"
    )


# =========================================================
# LOAD MODEL
# =========================================================

model = joblib.load(
    "bengaluru_house_price_model.pkl"
)


# =========================================================
# LOAD DATASET
# =========================================================

df = pd.read_csv(
    "Bengaluru_House_Data.csv"
)


# =========================================================
# TITLE
# =========================================================

st.title("🏠 Bengaluru House Price Prediction")

st.write(
    "Enter property details to estimate the market price "
    "and evaluate the investment value."
)


# =========================================================
# PROPERTY DETAILS
# =========================================================

st.header("🏡 Property Details")

location = st.text_input(
    "📍 Location"
)


col1, col2 = st.columns(2)


with col1:

    total_sqft = st.number_input(
        "📐 Total Square Feet",
        min_value=100.0,
        value=1000.0,
        step=50.0
    )

    bhk = st.number_input(
        "🛏️ BHK",
        min_value=1,
        max_value=10,
        value=2,
        step=1
    )


with col2:

    bath = st.number_input(
        "🚿 Bathrooms",
        min_value=1,
        max_value=10,
        value=2,
        step=1
    )

    asking_price = st.number_input(
        "💰 Asking Price (Lakhs)",
        min_value=0.0,
        value=50.0,
        step=1.0
    )


# =========================================================
# PREDICTION
# =========================================================

if st.button("🔮 Predict Price"):

    if location.strip() == "":

        st.warning(
            "⚠️ Please enter a location."
        )

    else:

        # -------------------------------------------------
        # CREATE INPUT DATA
        # -------------------------------------------------

        input_data = pd.DataFrame({
            "location": [location],
            "total_sqft": [total_sqft],
            "bhk": [bhk],
            "bath": [bath]
        })


        # -------------------------------------------------
        # MODEL PREDICTION
        # -------------------------------------------------

        try:

            prediction = float(
                model.predict(input_data)[0]
            )

        except Exception as e:

            st.error(
                f"❌ Prediction error: {e}"
            )

            st.stop()


        # -------------------------------------------------
        # INVESTMENT RATING
        # -------------------------------------------------

        if prediction > 0:

            difference = (
                (asking_price - prediction)
                / prediction
            ) * 100

        else:

            difference = 0


        if difference <= -10:

            rating = "🟢 Undervalued"

        elif difference <= 10:

            rating = "🟡 Fair Value"

        else:

            rating = "🔴 Overpriced"


        # =================================================
        # DISPLAY RESULT
        # =================================================

        st.divider()

        st.subheader(
            "📊 Prediction Result"
        )


        result1, result2 = st.columns(2)


        with result1:

            st.success(
                f"🏠 Estimated Market Price: "
                f"₹{prediction:.2f} Lakhs"
            )


        with result2:

            st.info(
                f"💡 Investment Rating: {rating}"
            )


        st.write(
            f"**Asking Price:** "
            f"₹{asking_price:.2f} Lakhs"
        )


        st.write(
            f"**Difference:** "
            f"{difference:.2f}%"
        )


        # =================================================
        # SAVE TO MYSQL
        # =================================================

        try:

            conn = get_connection()

            cursor = conn.cursor()


            insert_query = """
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
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """


            values = (
                location,
                float(total_sqft),
                int(bhk),
                int(bath),
                float(asking_price),
                float(prediction),
                rating
            )


            cursor.execute(
                insert_query,
                values
            )


            conn.commit()


            # -------------------------------------------------
            # EXPORT MYSQL DATA TO CSV
            # -------------------------------------------------

            export_cursor = conn.cursor(
                dictionary=True
            )


            export_cursor.execute(
                """
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
            )


            records = export_cursor.fetchall()


            export_cursor.close()

            cursor.close()

            conn.close()


            # -------------------------------------------------
            # CREATE / UPDATE CSV FILE
            # -------------------------------------------------

            history_df = pd.DataFrame(
                records
            )


            history_df.to_csv(
                "search_history.csv",
                index=False
            )


            st.success(
                "✅ Prediction saved successfully!"
            )


        except mysql.connector.Error as e:

            st.error(
                f"❌ MySQL error: {e}"
            )


# =========================================================
# DASHBOARD
# =========================================================

st.divider()

st.header(
    "📊 Bengaluru Housing Market Dashboard"
)

st.write(
    "Explore the Bengaluru housing market "
    "using interactive visualizations."
)


# =========================================================
# PREPARE DASHBOARD DATA
# =========================================================

dashboard_df = df.copy()


# ---------------------------------------------------------
# PRICE
# ---------------------------------------------------------

dashboard_df["price"] = pd.to_numeric(
    dashboard_df["price"],
    errors="coerce"
)


# ---------------------------------------------------------
# TOTAL SQFT
# ---------------------------------------------------------

dashboard_df["total_sqft_numeric"] = (
    dashboard_df["total_sqft"]
    .astype(str)
    .str.extract(
        r"(\d+\.?\d*)"
    )[0]
)


dashboard_df["total_sqft_numeric"] = pd.to_numeric(
    dashboard_df["total_sqft_numeric"],
    errors="coerce"
)


# ---------------------------------------------------------
# BHK
# ---------------------------------------------------------

dashboard_df["bhk_numeric"] = (
    dashboard_df["size"]
    .astype(str)
    .str.extract(
        r"(\d+)"
    )[0]
)


dashboard_df["bhk_numeric"] = pd.to_numeric(
    dashboard_df["bhk_numeric"],
    errors="coerce"
)


# =========================================================
# MARKET SUMMARY
# =========================================================

st.subheader(
    "📌 Market Summary"
)


summary1, summary2, summary3 = st.columns(3)


with summary1:

    st.metric(
        "🏠 Total Properties",
        f"{len(dashboard_df):,}"
    )


with summary2:

    average_price = (
        dashboard_df["price"].mean()
    )


    st.metric(
        "💰 Average Price",
        f"₹{average_price:.2f} Lakhs"
    )


with summary3:

    average_area = (
        dashboard_df[
            "total_sqft_numeric"
        ].mean()
    )


    st.metric(
        "📐 Average Area",
        f"{average_area:.0f} Sqft"
    )


# =========================================================
# PRICE DISTRIBUTION
# =========================================================

st.subheader(
    "💰 Property Price Distribution"
)


price_values = (
    dashboard_df["price"]
    .dropna()
)


if len(price_values) > 0:

    price_bins = pd.cut(
        price_values,
        bins=20
    )


    price_distribution = (
        price_bins
        .value_counts()
        .sort_index()
    )


    price_chart = pd.DataFrame({

        "Price Range":
            price_distribution.index.astype(str),

        "Number of Houses":
            price_distribution.values

    })


    st.bar_chart(
        price_chart.set_index(
            "Price Range"
        )
    )


# =========================================================
# AVERAGE PRICE BY BHK
# =========================================================

st.subheader(
    "🛏️ Average Price by BHK"
)


bhk_price = (
    dashboard_df
    .dropna(
        subset=[
            "bhk_numeric",
            "price"
        ]
    )
    .groupby(
        "bhk_numeric"
    )["price"]
    .mean()
    .sort_index()
)


st.bar_chart(
    bhk_price
)


# =========================================================
# AVERAGE PRICE BY LOCATION
# =========================================================

st.subheader(
    "📍 Average Price by Location"
)


location_price = (
    dashboard_df
    .dropna(
        subset=[
            "location",
            "price"
        ]
    )
    .groupby(
        "location"
    )["price"]
    .mean()
    .sort_values(
        ascending=False
    )
    .head(15)
    .sort_values()
)


st.bar_chart(
    location_price
)


# =========================================================
# TOTAL SQFT VS PRICE
# =========================================================

st.subheader(
    "📐 Total Square Feet vs Price"
)


sqft_price = (
    dashboard_df[
        [
            "total_sqft_numeric",
            "price"
        ]
    ]
    .dropna()
)


if len(sqft_price) > 0:

    sqft_price = sqft_price.rename(
        columns={
            "total_sqft_numeric":
                "Total Sqft",

            "price":
                "Price"
        }
    )


    st.scatter_chart(
        sqft_price,
        x="Total Sqft",
        y="Price"
    )
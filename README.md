Bengaluru House Price Prediction
📌 Project Overview

Bengaluru House Price Prediction is an end-to-end Machine Learning project designed to predict residential property prices in Bengaluru based on important property features such as location, total square feet, BHK, and number of bathrooms.

The project covers the complete data science workflow, starting from data preprocessing and exploratory data analysis to machine learning model development, model comparison, feature importance analysis, and deployment through an interactive Streamlit web application.

🎯 Project Objectives
Clean and preprocess the Bengaluru housing dataset.
Handle missing values and inconsistent data.
Identify and remove extreme outliers.
Perform Exploratory Data Analysis (EDA).
Engineer useful features such as BHK and price per square foot.
Build machine learning models for house price prediction.
Compare model performance using MAE, RMSE, and R².
Identify the major factors influencing house prices.
Deploy the prediction model using Streamlit.
Provide a simple and user-friendly interface for property price prediction.
📊 Dataset

The project uses the Bengaluru House Data dataset containing residential property information from Bengaluru.

Important Features
Feature	Description
location	Location of the property
total_sqft	Total area of the property
bhk	Number of bedrooms
bath	Number of bathrooms
price	Property price in lakhs

After data cleaning and preprocessing, the final dataset contains:

11,362 rows × 7 columns

🧹 Data Preprocessing

The following preprocessing steps were performed:

Removed unnecessary columns.
Handled missing values.
Cleaned location names.
Converted property size into numerical BHK values.
Converted total_sqft into a numerical format.
Created the price_per_sqft feature.
Grouped rare locations into an Other category.
Detected and removed outliers using the IQR method.
Outlier Removal

44 outliers were removed during the preprocessing stage.

📈 Exploratory Data Analysis

EDA was performed to understand the relationships between property characteristics and prices.

Key analyses included:

Price distribution.
BHK distribution.
Location-wise property prices.
Total square feet vs. price.
Price per square foot.
Relationship between BHK and property price.
Identification of major price-driving factors.
🤖 Machine Learning Models

Two regression models were developed and compared:

1. Linear Regression

Used as a baseline regression model to establish an initial prediction performance.

2. Random Forest Regression

A Random Forest Regressor was developed using multiple decision trees to capture nonlinear relationships between property features and prices.

The Random Forest model used:

200 decision trees
random_state = 42
Parallel processing using n_jobs=-1
📊 Model Evaluation

The models were evaluated using:

MAE — Mean Absolute Error

Measures the average absolute difference between actual and predicted prices.

RMSE — Root Mean Squared Error

Measures prediction error while giving greater weight to larger errors.

R² Score

Measures how well the model explains the variation in property prices.

🔍 Feature Importance & Value Drivers

Feature importance analysis was performed to identify the variables that have the greatest influence on house price predictions.

Important factors identified include:

Total square feet
BHK
Number of bathrooms
Location
Location-specific property characteristics

This analysis helps understand why property prices vary across Bengaluru.

🌐 Streamlit Web Application

The trained machine learning model is integrated into an interactive Streamlit web application.

The application allows users to enter property details such as:

📍 Location
🛏️ BHK
📐 Total square feet
🚿 Number of bathrooms

The system then provides an estimated property price.

Application Features
Simple user interface
Property price prediction
Location selection
Interactive inputs
Prediction results
Property insights
Investment-oriented analysis
🏗️ Project Workflow
Raw Bengaluru Housing Data
          ↓
Data Cleaning
          ↓
Data Preprocessing
          ↓
Feature Engineering
          ↓
Exploratory Data Analysis
          ↓
Train/Test Split
          ↓
Machine Learning Models
          ↓
Model Comparison
          ↓
Feature Importance
          ↓
Best Model Selection
          ↓
Streamlit Deployment
          ↓
House Price Prediction
🛠️ Technologies Used
Python
Pandas
NumPy
Matplotlib
Scikit-learn
Joblib
Streamlit
Git
GitHub
Git LFS
📁 Project Structure
Bengaluru_House_Project/
│
├── app.py
├── Bengaluru_House_Data.csv
├── search_history.csv
├── bengaluru_house_price_model.pkl
├── README.md
├── .gitignore
├── .gitattributes
└── .vscode/
🚀 How to Run the Project
1. Clone the repository
git clone https://github.com/saikiran-svg/Bengaluru-House-Price-Prediction.git
2. Navigate to the project folder
cd Bengaluru-House-Price-Prediction
3. Install required libraries
pip install pandas numpy matplotlib scikit-learn streamlit joblib
4. Run the Streamlit application
streamlit run app.py

The application will open in your browser.

📦 Model Storage

The trained model file is approximately 132 MB, so it is stored using Git Large File Storage (Git LFS) instead of normal Git tracking.

🎯 Expected Deliveries
Cleaned and processed Bengaluru housing dataset.
Exploratory Data Analysis and visualizations.
Machine learning prediction models.
Model performance comparison.
Identification of major property price drivers.
Trained and saved prediction model.
Interactive Streamlit web application.
GitHub repository containing the complete project.
Final project documentation and presentation.
🔮 Future Scope

The project can be further improved by:

Adding more advanced machine learning models.
Incorporating real-time property listings.
Adding geographical/map-based analysis.
Including additional property features.
Improving model accuracy through hyperparameter tuning.
Deploying the application on a cloud platform.
Adding personalized investment recommendations.
👨‍💻 Project

Bengaluru House Price Prediction

Machine Learning + Data Analytics + Streamlit
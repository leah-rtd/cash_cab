import streamlit as st

st.title("About the Project")

# Project overview
st.markdown("""
## 🚕 What is "Need a Wagon?"

This application predicts taxi fares for New York City trips using advanced machine learning techniques.
Built with deep learning models and deployed through a sophisticated MLOps pipeline, it provides
accurate fare estimates based on trip parameters.

## 🎯 Key Features

- **Fare Prediction**: Deep learning models for accurate taxi fare estimation
- **Interactive Interface**: User-friendly input forms and visualizations
- **Real-time Results**: Instant fare predictions with model confidence

## 🛠️ Technical Stack

### Frontend & Visualization
- **Interface**: Streamlit
- **Data Visualization**: Plotly, Folium

### Data Processing & Machine Learning
- **Data Processing**: Pandas, NumPy, Scikit-learn
- **Deep Learning**: TensorFlow models for fare prediction
- **Data Sources**: New York City Taxi & Limousine Commission dataset

### Backend Architecture
- **MLOps Pipeline**: MLflow for experiment tracking and model management
- **Workflow Orchestration**: Prefect for automated data pipelines
- **Model Training**: Google Cloud Virtual Machines
- **Data Warehouse**: Google BigQuery for scalable data storage
- **Containerization**: Docker images hosted in Google Artifact Registry
- **Model Deployment**: Google Cloud Run for serverless model serving


## 👩‍💻 About the Developer

This app was created by **Leah Rothschild** as part of the **Le Wagon Data Science Bootcamp**.

This project demonstrates end-to-end machine learning deployment, from data ingestion
and model training to production-ready inference services for taxi fare prediction.

## 📫 Connect

- **LinkedIn**: [Leah Rothschild](www.linkedin.com/in/leah-rothschild)
- **GitHub**: [leah-rtd](https://github.com/leah-rtd)

---
*Built with ❤️ and a sophisticated MLOps pipeline during Le Wagon*
""")

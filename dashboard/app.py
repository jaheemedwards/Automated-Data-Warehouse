import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

st.set_page_config(page_title="Automated Data Warehouse", layout="wide")

load_dotenv(dotenv_path="credentials.env")  

engine = create_engine(os.getenv("DATABASE_URL"))

st.title("🌦️ Automated Data Warehouse Dashboard")

df = pd.read_sql("SELECT * FROM fact_weather JOIN dim_city USING(city_id)", engine)
st.dataframe(df)

# Libraries
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.subplots as sp

# Layout
st.set_page_config(page_title="Stock Analysis", page_icon=":bar_chart:", layout="wide")
st.title("Stock Analysis based on returns 💸")

# Global Variables
DATE_COLUMN = "DATE"
DATA_PATH = "./../data/stocks_data.xlsx"


@st.cache
def load_data():
    data = pd.read_excel(DATA_PATH, sheet_name="Returns", header=[5, 6]).T.iloc[2:, :]
    data = data.rename(columns=data.iloc[0])
    data = data.iloc[2:]
    upercase = lambda x: str(x).upper()
    data.rename(upercase, axis="columns", inplace=True)
    data.reset_index(inplace=True)
    data.rename(columns={"level_0": "DATE1", "level_1": "DATE"}, inplace=True)
    data.drop(columns="DATE1", inplace=True)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN]).dt.date
    return data


# Load data into the dataframe
data = load_data()

st.sidebar.markdown("## Select Data Time and Stock")

stocklist = [
    "BP PLC",
    "FMC CORP",
    "WEYERHAEUSER CO",
]

df_columns_list = [
    "BP/ LN Equity",
    "FMC US Equity",
    "WY US Equity",
]

search_dictio = {}
for i, k in enumerate(df_columns_list):
    search_dictio[stocklist[i]] = k

# -- Choose stocks from stockslists
stocks_selected = st.sidebar.multiselect("Stock list", stocklist)

stocks = []
stocks.append("DATE")
for i in stocks_selected:
    stocks.append(search_dictio.get(i).upper())

# -- Choose the start and end dates
min_date = data[DATE_COLUMN].min()
max_date = data[DATE_COLUMN].max()
start_date = st.sidebar.date_input(
    "Start date:", min_value=min_date, max_value=max_date, value=min_date
)
end_date = st.sidebar.date_input(
    "End date:", min_value=min_date, max_value=max_date, value=max_date
)
st.write("Selected range:", start_date, "to", end_date)

# -- Show data
# ----- Conditions
condition1 = start_date <= data[DATE_COLUMN]
condition2 = data[DATE_COLUMN] <= end_date
mask = condition1 & condition2
filtered_df = data.loc[mask, :]
stocks_df = filtered_df[stocks]

# # ----- Reporting
m1, m2, m3, m4, m5 = st.columns((1, 1, 1, 1, 1))

total_returns = stocks_df.drop(columns=DATE_COLUMN).sum(axis=1)

m1.write("")
m2.metric(label="Number of selected stocks:", value=str(len(stocks) - 1))
m3.metric(label="Total Returns for Portfolio", value=str(round(sum(total_returns), 1)))
m1.write("")

# ---- Plot
st.dataframe(filtered_df[stocks])
st.line_chart(
    data=filtered_df, x="DATE", y=stocks, width=0, height=0, use_container_width=True
)

# -- Aknowledgments
c1, c2 = st.columns(2)
with c1:
    st.info(
        "**Data Scientists Linkedin: [@JAGS](https://www.linkedin.com/in/jagarciasanchez) [@Sarra](https://www.linkedin.com/in/sarrabenyahia/)**",
        icon="💡",
    )
with c2:
    st.info(
        "**GitHub: [@JAGS](https://github.com/Pse1234) [@Sarra](https://github.com/sarrabenyahia)**",
        icon="💻",
    )

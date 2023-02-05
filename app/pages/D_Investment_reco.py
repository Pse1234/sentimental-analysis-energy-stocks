import streamlit as st
import pandas as pd
from PIL import Image

# Layout
twt_logo = Image.open('app/images/twitter-logo.png')
st.set_page_config(
    page_title="Sentimental analysis", page_icon=twt_logo, layout="wide"
)

st.title("Investment Recommendation for the selected period")
st.header("Long or Short stocks")

@st.cache(suppress_st_warning=True)
def load_predicted_data():
    results = pd.read_csv("./data/data_model/results.csv",)
    strategy = pd.read_csv("./data/data_model/todo.csv",)
    returns = pd.read_csv("./data/stocks_data.csv",)
    returns = returns.rename(columns=returns.iloc[0])
    returns = returns.iloc[2:]
    upercase = lambda x: str(x).upper()
    returns.rename(upercase, axis="columns", inplace=True)
    returns.rename(
        columns={"UNNAMED: 2_LEVEL_0": "DATE1", "UNNAMED: 2_LEVEL_1": "DATE"}, inplace=True
    )
    returns.drop(columns="DATE1", inplace=True)
    except_column = "DATE"
    returns.fillna(0, inplace=True)
    col_list = returns.columns.tolist()
    selected_columns = [col for col in col_list if col != except_column]
    returns[selected_columns] = returns[selected_columns].astype(float)
    result = returns[selected_columns].apply(lambda x: x / 100 + 1, axis=1)
    returns = pd.concat([returns[except_column], result], axis=1)
    returns["DATE"] = pd.to_datetime(returns["DATE"])
    returns["year"] = returns["DATE"].dt.year
    returns["month"] = returns["DATE"].dt.month
    returns["yearmonth"] = (
        returns["year"].astype(str)
        + "-"
        + returns["month"].astype(str).str.zfill(2)
    )

    return results, strategy, returns, selected_columns

results, strategy, returns, selected_columns = load_predicted_data()

strategy = strategy.rename(columns={'Unnamed: 0': 'month_invest'})
strategy['month_invest'] = pd.to_datetime(strategy['month_invest']).dt.date

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


# Filter the stocks
options = st.multiselect(
    "**Select your desired stocks:**",
    options=stocklist,
    default=None,
    key="macro_options",
)

min_date = strategy["month_invest"].min()
max_date = strategy["month_invest"].max()

# filter start date
start_date = st.date_input(
    "**Select a start date:**",
    min_value=min_date,
    max_value=max_date,
    value=min_date,
    key="start_date",
)
# filter end date
end_date = st.date_input(
    "**Select an end date:**",
    min_value=min_date,
    max_value=max_date,
    value=max_date,
    key="end_date",
)

condition1 = start_date <= strategy["month_invest"]
condition2 = strategy["month_invest"] <= end_date
mask = condition1 & condition2
filtered_investment = strategy.loc[mask, :]

printing_results = pd.DataFrame()
for col in stocklist:
    printing_results.loc[col, 'total_investment'] = filtered_investment[filtered_investment[col] > 0][col].sum()
    printing_results.loc[col, 'total_return'] = filtered_investment[col+'_cumulative_sum'].sum()
    printing_results.loc[col, 'market_results'] = returns[search_dictio.get(col).upper()].prod() - 1
printing_results['strategy_results'] = printing_results['total_return'] / printing_results['total_investment']

printing_results.reset_index(inplace=True)
printing_results = printing_results.rename(columns={'index': 'companies'})
printing_results.fillna(0, inplace=True)
selected_stocks = printing_results['companies'].isin(options)
printing_results = printing_results.loc[selected_stocks]

st.dataframe(printing_results)

if len(options)>0:
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            label=f"Investment recommendation:",
            value=str(round(results_selected["total_investment"].sum(), 2)),
        )

    with c2:
        st.metric(
            label=f"Return on investment:",
            value=str(round(results_selected["total_return"].sum()*100, 2)
            ) + "%"
        )

    with c3:
        st.metric(
            label=f"Benefice of our strategy:",
            value=str(
                round(results_selected["strategy_results"].mean()*100, 2)
            ) + "%"
        )

    with c4:
        st.metric(
            label=f"Benefice of market:",
            value=str(
                round(results_selected["market_results"].mean()*100, 2)
            ) + "%"
        )

    st.dataframe(results_selected)

else:
    st.warning("Please select at least one stock to see the metrics.")

st.write("You are maybe wondering when and how much do you have to invest. Then look at the next dataframe:")
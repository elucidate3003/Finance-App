import streamlit as st
import pandas as pd
import tabula
import plotly.express as px
import json
import os

st.set_page_config(page_title='Finance App', page_icon=':bar_chart:',layout="wide")
category_file = "categories.json"

if "categories" not in st.session_state:
    st.session_state.categories = {
        "Uncategorised": [],
    }
    
if os.path.exists(category_file):
        with open(category_file,"r") as f:
            st.session_state.categories=json.load(f)
            
def save_categories():
    with open(category_file,"w") as f:
        json.dump(st.session_state.categories,f)
def categorise_transaction(df):
    df["CATEGORY"] = "Uncategorised"
    
    for category, keywords in st.session_state.categories.items():
        if category == "Uncategorised" or not keywords:
            continue
        
        lower_keywords=[keyword for keyword in keywords]
        
        for idx,row in df.iterrows():
            details=row["MODE"]
            if details in lower_keywords:
                df.at[idx,"CATEGORY"]= category
    return df

def load_transactions(file):
    try:
        df = pd.read_csv(file)
        df.dropna(how="any",inplace=True) 
        df.columns = [col.strip() for col in df.columns]
        df["DEPOSITS"]=df["DEPOSITS"].str.replace(",","").astype(float)
        df["WITHDRAWALS"]=df["WITHDRAWALS"].str.replace(",","").astype(float)
        df["BALANCE"]=df["BALANCE"].str.replace(",","").astype(float)
        df['DATE'] = pd.to_datetime(df['DATE'], format="%d-%m-%Y")
        df=df.sort_values(by=['DATE'])
        
        return categorise_transaction(df)
        
    except Exception as e:
        print(f"Error loading transactions: {str(e)} in line {e.__traceback__.tb_lineno}")
        return None
def add_keyword_to_category(category, keyword):
    keyword = keyword.strip()
    if keyword and keyword not in st.session_state.categories[category]:
        st.session_state.categories[category].append(keyword)
        save_categories()
        return True
    
    return False
def main():
    # Load data from CSV file
    st.title('Financial Data Analysis')
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv","pdf"])
    
    if uploaded_file is not None:
        df = load_transactions(uploaded_file)
        
        if df is not None:
            # Store the dataframe in session state
            st.session_state.df = df
            tab1, tab2, tab3 = st.tabs(["Spent Money 💸", "Earned Money 🤑", "Balance 💰"])
            with tab1:
                new_category_name=st.text_input("Enter the name of the category:")
                add_button = st.button("Add Category")
                if add_button and new_category_name:
                    if new_category_name not in st.session_state.categories:
                        st.session_state.categories[new_category_name]=[]
                        save_categories()
                        st.success(f"{new_category_name} category successfully added")
                        st.rerun()
                    elif new_category_name in st.session_state.categories.keys():
                        st.warning("Category already exists!")
                st.subheader("Your Expenses")
                edited_df = st.data_editor(
                    st.session_state.df[["DATE","MODE","WITHDRAWALS","CATEGORY"]],
                    column_config={
                        "DATE": st.column_config.DateColumn("DATE", format="DD/MM/YYYY"),
                        "WITHDRAWALS": st.column_config.NumberColumn("WITHDRAWALS", format="%.2f INR"),
                        "CATEGORY": st.column_config.SelectboxColumn(
                            "CATEGORY",
                            options=list(st.session_state.categories.keys())
                        )
                    },
                    hide_index=True,
                    use_container_width=True,
                    key="category_editor"
                )
                
                save_button = st.button("Apply Changes", type="primary")
                if save_button:
                    for idx, row in edited_df.iterrows():
                        new_category = row["CATEGORY"]
                        if new_category == st.session_state.df.at[idx, "CATEGORY"]:
                            continue
                        
                        details = row["MODE"]
                        st.session_state.df.at[idx, "CATEGORY"] = new_category
                        add_keyword_to_category(new_category, details)
                        
                st.subheader('Expense Summary')
                category_totals = st.session_state.df.groupby("CATEGORY")["WITHDRAWALS"].sum().reset_index()
                category_totals = category_totals.sort_values("WITHDRAWALS", ascending=False)
                
                st.dataframe(
                    category_totals, 
                    column_config={
                     "WITHDRAWALS": st.column_config.NumberColumn("WITHDRAWALS", format="%.2f INR")   
                    },
                    use_container_width=True,
                    hide_index=True
                )
                
                fig = px.pie(
                    category_totals,
                    values="WITHDRAWALS",
                    names="CATEGORY",
                    title="Expenses by Category"
                )
                st.plotly_chart(fig, use_container_width=True)
                
            with tab2:
                st.subheader("Payments Summary")
                total_payments = df["DEPOSITS"].sum()
                st.metric("Total Payments", f"{total_payments:,.2f} INR")
                st.write = df["DEPOSITS"]
            with tab3:
                st.subheader("Balance Summary")
                balance_summary = df.groupby(pd.Grouper(key="DATE", freq="3600min"))["BALANCE"].last().reset_index()
                balance_summary.rename(columns={"BALANCE":"MONTHLY BALANCE"}, inplace=True)
                st.dataframe(balance_summary,use_container_width=True)
                st.plotly_chart(px.line(
                    balance_summary,
                    x="DATE",
                    y="MONTHLY BALANCE"),
                    use_container_width=True,)        
main()
                
        
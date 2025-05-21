import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
import sys
import subprocess

# Set Java home path for JPype
os.environ['JAVA_HOME'] = '/Library/Internet Plug-Ins/JavaAppletPlugin.plugin/Contents/Home'

# Set Java options for better performance with large PDFs
os.environ['_JAVA_OPTIONS'] = '-Xmx1024m -XX:ReservedCodeCacheSize=256m'

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
            details=row["PARTICULARS"]
            if details in lower_keywords:
                df.at[idx,"CATEGORY"]= category
    return df

def check_java_installed():
    """Check if Java is installed on the system and set JAVA_HOME if needed."""
    try:
        # Try to get Java version
        java_version = subprocess.check_output(['java', '-version'], stderr=subprocess.STDOUT)
        
        # If we're on macOS, try to get the Java home path
        if sys.platform == 'darwin':
            try:
                java_home = subprocess.check_output(['/usr/libexec/java_home'], text=True).strip()
                if java_home and os.path.exists(java_home):
                    os.environ['JAVA_HOME'] = java_home
                    return True
            except:
                # If /usr/libexec/java_home fails, we'll use the hardcoded path
                pass
                
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def load_transactions(file):
    try:
        file_type = file.name.split('.')[-1].lower()
        
        if file_type == 'csv':
            # Handle CSV files
            df = pd.read_csv(file)
        elif file_type == 'pdf':
            # Check if Java is installed
            if not check_java_installed():
                st.error("Java is required to read PDF files. Please install Java from https://www.java.com/download/ and restart the application.")
                return None
            
            # Try to use tabula with subprocess approach if JPype fails
            try:
                # First try to import tabula normally
                try:
                    import tabula
                    import warnings
                    # Suppress font warnings
                    warnings.filterwarnings('ignore', message='.*font.*')
                    use_subprocess = False
                except ImportError:
                    st.warning("Using fallback method for PDF processing. For better performance, install JPype1: pip install JPype1")
                    import tabula
                    use_subprocess = True
                
                # Check if PDF is password-protected
                password = None
                try:
                    # First try without password
                    if use_subprocess:
                        tables = tabula.read_pdf(file, pages="1", multiple_tables=True, stream=True, 
                                               output_format="dataframe", lattice=True, silent=True)
                    else:
                        tables = tabula.read_pdf(file, pages="1", multiple_tables=True, stream=True, 
                                               lattice=True, silent=True)
                except Exception as e:
                    if "password is incorrect" in str(e) or "Cannot decrypt PDF" in str(e):
                        # PDF is password-protected, ask for password
                        password = st.text_input("This PDF is password-protected. Please enter the password:", type="password")
                        if not password:
                            st.error("Password is required to read this PDF file.")
                            return None
                
                # Read PDF file with password if provided
                try:
                    if use_subprocess:
                        tables = tabula.read_pdf(file, pages="all", multiple_tables=True, stream=True, 
                                               output_format="dataframe", password=password,
                                               lattice=True, silent=True, guess=False)
                    else:
                        tables = tabula.read_pdf(file, pages="all", multiple_tables=True, stream=True, 
                                               password=password, lattice=True, silent=True, guess=False)
                    
                    if not tables:
                        st.error("No tables found in the PDF file.")
                        return None
                        
                    # Use the first table found
                    df = tables[0]
                    for table in tables[1:]:
                        df = pd.concat([df, table], ignore_index=True)
                except Exception as e:
                    if password and ("password is incorrect" in str(e) or "Cannot decrypt PDF" in str(e)):
                        st.error("The password you entered is incorrect.")
                    else:
                        st.error(f"Error reading PDF: {str(e)}")
                    return None
            except Exception as e:
                st.error(f"Error reading PDF: {str(e)}")
                st.error("Make sure Java is installed correctly and the JAVA_HOME environment variable is set.")
                return None
        else:
            st.error(f"Unsupported file type: {file_type}. Please upload a CSV or PDF file.")
            return None
            
        # Process the dataframe
        try:
            # Clean column names
            df.columns = [col.strip() for col in df.columns]
            
            # Check if required columns exist
            required_columns = ["DATE", "PARTICULARS", "DEPOSITS", "WITHDRAWALS", "BALANCE"]
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                st.error(f"The following required columns are missing from the file: {', '.join(missing_columns)}")
                st.write("Available columns:", ", ".join(df.columns))
                return None
            
            # Process numeric columns - first convert to string if needed
            # Handle DEPOSITS column
            try:
                if df["DEPOSITS"].dtype != 'object':
                    df["DEPOSITS"] = df["DEPOSITS"].astype(str)
                df["DEPOSITS"] = df["DEPOSITS"].str.replace(",", "").astype(float)
            except Exception as e:
                st.warning(f"Issue processing DEPOSITS column: {str(e)}")
                # Try direct conversion if string operations fail
                try:
                    df["DEPOSITS"] = pd.to_numeric(df["DEPOSITS"], errors='coerce')
                except:
                    pass
                
            # Handle WITHDRAWALS column
            try:
                if df["WITHDRAWALS"].dtype != 'object':
                    df["WITHDRAWALS"] = df["WITHDRAWALS"].astype(str)
                df["WITHDRAWALS"] = df["WITHDRAWALS"].str.replace(",", "").astype(float)
            except Exception as e:
                st.warning(f"Issue processing WITHDRAWALS column: {str(e)}")
                # Try direct conversion if string operations fail
                try:
                    df["WITHDRAWALS"] = pd.to_numeric(df["WITHDRAWALS"], errors='coerce')
                except:
                    pass
                
            # Handle BALANCE column
            try:
                if df["BALANCE"].dtype != 'object':
                    df["BALANCE"] = df["BALANCE"].astype(str)
                df["BALANCE"] = df["BALANCE"].str.replace(",", "").astype(float)
            except Exception as e:
                st.warning(f"Issue processing BALANCE column: {str(e)}")
                # Try direct conversion if string operations fail
                try:
                    df["BALANCE"] = pd.to_numeric(df["BALANCE"], errors='coerce')
                except:
                    pass
            
            # Process date column with multiple format support
            try:
                # First try with the expected format
                df['DATE'] = pd.to_datetime(df['DATE'], format="%d-%b-%Y")
            except Exception as e:
                st.warning(f"Could not parse dates with format %d-%b-%Y, trying alternative formats: {str(e)}")
                try:
                    # Try with automatic format detection
                    df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce')
                    
                    # Check if we have any valid dates
                    if df['DATE'].isna().all():
                        st.error("Could not parse any dates in the DATE column.")
                        return None
                except Exception as e2:
                    st.error(f"Failed to parse dates: {str(e2)}")
                    return None
            
            # Sort by date
            df = df.sort_values(by=['DATE'])
        except Exception as e:
            st.error(f"Error processing data: {str(e)}")
            st.write("Please make sure your file has the correct format with columns: DATE, PARTICULARS, DEPOSITS, WITHDRAWALS, BALANCE")
            return None
        
        return categorise_transaction(df)
        
    except Exception as e:
        error_msg = f"Error loading transactions: {str(e)}"
        if hasattr(e, '__traceback__'):
            error_msg += f" in line {e.__traceback__.tb_lineno}"
        st.error(error_msg)
        print(error_msg)
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
                    st.session_state.df[["DATE","PARTICULARS","WITHDRAWALS","CATEGORY"]],
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
                        
                        details = row["PARTICULARS"]
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
                st.write("Deposits Details:")
                st.dataframe(df[["DATE", "PARTICULARS", "DEPOSITS"]], 
                             column_config={
                                 "DATE": st.column_config.DateColumn("DATE", format="DD/MM/YYYY"),
                                 "DEPOSITS": st.column_config.NumberColumn("DEPOSITS", format="%.2f INR")
                             },
                             use_container_width=True,
                             hide_index=True)
            with tab3:
                st.subheader("Balance Summary")
                # Drop rows with NaT in DATE column before grouping
                df_clean = df.dropna(subset=['DATE'])
                
                if len(df_clean) > 0:
                    # Group by date with a daily frequency
                    balance_summary = df_clean.groupby(pd.Grouper(key="DATE", freq="D"))["BALANCE"].last().reset_index()
                    balance_summary.rename(columns={"BALANCE":"DAILY BALANCE"}, inplace=True)
                    
                    # Display the balance summary
                    st.dataframe(balance_summary, use_container_width=True)
                else:
                    st.error("No valid dates found for balance summary. Please check your data.")
                if len(df_clean) > 0:
                    st.plotly_chart(px.line(
                        balance_summary,
                        x="DATE",
                        y="DAILY BALANCE",
                        title="Balance Over Time"),
                        use_container_width=True)        
main()
                
        
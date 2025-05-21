# Finance App

A comprehensive financial data analysis application built with Streamlit that helps you track, categorize, and visualize your expenses and income.

## Features

- **CSV and PDF Import**: Upload your bank statements in CSV or PDF format
- **Automatic Categorization**: Transactions are automatically categorized based on keywords
- **Custom Categories**: Create and manage your own expense categories
- **Interactive Data Editing**: Edit transaction details and categories directly in the app
- **Visual Analytics**: View your financial data through interactive charts and graphs
- **Expense Tracking**: Analyze your spending patterns by category
- **Income Monitoring**: Track your income sources and total earnings
- **Balance Visualization**: See how your account balance changes over time

## Screenshots

*[Add screenshots of your application here]*

## Installation

### Prerequisites

- Python 3.9 or higher
- Java Runtime Environment (JRE) - Required for PDF processing

### Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd FinanceApp
   ```

2. Install dependencies:
   ```
   pip install uv
   uv pip install -r requirements.txt
   ```
   or
   Install from a pyproject.toml file:

  ```
  uv pip install -r pyproject.toml
  ```

3. Make sure Java is installed for PDF processing:
   - For macOS: Install from [java.com](https://www.java.com/download/)
   - For Windows: Install from [java.com](https://www.java.com/download/)
   - For Linux: `sudo apt install default-jre` (Ubuntu/Debian) or equivalent

## Usage

1. Start the application:
   ```
   streamlit run main.py
   ```

2. Upload your bank statement:
   - Click on the file uploader
   - Select a CSV or PDF file containing your bank transactions
   - If using a PDF with password protection, you'll be prompted to enter the password

3. Analyze your finances:
   - Navigate between tabs to view expenses, income, and balance history
   - Create new categories and categorize transactions
   - View summary charts and statistics

## Data Format

The application expects your bank statement to have the following columns:
- **DATE**: Transaction date
- **PARTICULARS**: Transaction details/description
- **DEPOSITS**: Amount deposited (income)
- **WITHDRAWALS**: Amount withdrawn (expenses)
- **BALANCE**: Account balance after the transaction

## Project Structure

```
FinanceApp/
├── main.py           # Main application file
├── categories.json   # Saved categories and keywords
├── pyproject.toml    # Project dependencies
├── README.md         # This documentation
└── .gitignore        # Git ignore file
```

## Technical Details

### Dependencies

- **streamlit**: Web application framework
- **pandas**: Data manipulation and analysis
- **plotly**: Interactive data visualization
- **tabula-py**: PDF table extraction
- **jpype1**: Java bridge for Python (used by tabula-py)

### Key Features Implementation

- **Category Management**: Categories are stored in a JSON file and loaded into session state
- **Transaction Categorization**: Transactions are categorized based on keywords in the PARTICULARS field
- **PDF Processing**: Uses tabula-py with JPype to extract tables from PDF files
- **Data Visualization**: Uses Plotly for interactive charts and Streamlit's built-in visualization components

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Specify your license here]

## Acknowledgements

- [Streamlit](https://streamlit.io/) for the amazing web app framework
- [Tabula](https://tabula.technology/) for PDF table extraction capabilities
- [Plotly](https://plotly.com/python/) for data visualization tools

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from datetime import date, datetime

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Expense Tracker | Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CONSTANTS
# =========================================================

FILE_NAME = Path("expenses.csv")

COLUMNS = [
    "id",
    "date",
    "category",
    "description",
    "amount"
]

CATEGORIES = [
    "Food",
    "Travel",
    "Shopping",
    "Bills",
    "Education",
    "Healthcare",
    "Entertainment",
    "Other"
]

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>
    /* Main application */
    .main {
        background-color: #f7f9fc;
    }

    /* Hide default Streamlit menu and footer */
    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    /* Dashboard cards */
    .metric-card {
        background-color: white;
        padding: 22px;
        border-radius: 15px;
        border: 1px solid #e8edf3;
        box-shadow: 0 3px 12px rgba(0,0,0,0.04);
    }

    .metric-title {
        color: #667085;
        font-size: 14px;
        font-weight: 600;
    }

    .metric-value {
        color: #172033;
        font-size: 28px;
        font-weight: 700;
        margin-top: 8px;
    }

    /* App title */
    .app-title {
        color: #172033;
        font-size: 34px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .app-subtitle {
        color: #667085;
        font-size: 16px;
        margin-bottom: 25px;
    }

    /* Section headings */
    .section-title {
        color: #172033;
        font-size: 22px;
        font-weight: 700;
        margin-top: 15px;
        margin-bottom: 15px;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #172033;
    }

    section[data-testid="stSidebar"] * {
        color: white;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
    }

    /* Responsive spacing */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# FILE MANAGEMENT
# =========================================================

def initialize_file():
    """Create the CSV file if it does not exist."""

    if not FILE_NAME.exists():
        df = pd.DataFrame(columns=COLUMNS)
        df.to_csv(FILE_NAME, index=False)


def load_expenses():
    """Load expenses from CSV."""

    initialize_file()

    try:
        df = pd.read_csv(FILE_NAME)

        if df.empty:
            return pd.DataFrame(columns=COLUMNS)

        for column in COLUMNS:
            if column not in df.columns:
                df[column] = None

        df = df[COLUMNS]

        df["id"] = pd.to_numeric(
            df["id"], errors="coerce"
        ).astype("Int64")

        df["amount"] = pd.to_numeric(
            df["amount"], errors="coerce"
        ).fillna(0.0)

        df["date"] = pd.to_datetime(
            df["date"], errors="coerce"
        )

        return df

    except Exception as error:
        st.error(f"Unable to load expenses: {error}")
        return pd.DataFrame(columns=COLUMNS)


def save_expenses(df):
    """Save expenses to CSV."""

    try:
        output_df = df.copy()

        if not output_df.empty:
            output_df["date"] = pd.to_datetime(
                output_df["date"], errors="coerce"
            ).dt.strftime("%Y-%m-%d")

            output_df["amount"] = pd.to_numeric(
                output_df["amount"], errors="coerce"
            ).round(2)

        output_df.to_csv(FILE_NAME, index=False)

        return True

    except Exception as error:
        st.error(f"Unable to save expenses: {error}")
        return False


# =========================================================
# VALIDATION
# =========================================================

def get_next_id(df):
    """Generate the next available expense ID."""

    if df.empty:
        return 1

    valid_ids = pd.to_numeric(
        df["id"], errors="coerce"
    ).dropna()

    if valid_ids.empty:
        return 1

    return int(valid_ids.max()) + 1


def validate_expense(expense_date, category, description, amount):
    """Validate user-entered expense details."""

    if not category:
        return False, "Please select a category."

    if not description.strip():
        return False, "Please enter an expense description."

    if amount <= 0:
        return False, "Amount must be greater than zero."

    if amount > 10_000_000:
        return False, "Please enter a reasonable amount."

    if expense_date > date.today():
        return False, "Future dates are not allowed."

    return True, ""


# =========================================================
# DASHBOARD METRICS
# =========================================================

def display_metric(title, value, icon):
    """Display a professional metric card."""

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">
                {icon} &nbsp; {title}
            </div>
            <div class="metric-value">
                {value}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def show_dashboard(df):
    """Display the main dashboard."""

    st.markdown(
        '<div class="app-title">💰 Expense Tracker</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="app-subtitle">'
        'Track your expenses, understand your spending, '
        'and manage your finances efficiently.'
        '</div>',
        unsafe_allow_html=True
    )

    total_expenses = df["amount"].sum()
    transaction_count = len(df)

    average_expense = (
        total_expenses / transaction_count
        if transaction_count > 0
        else 0
    )

    unique_categories = (
        df["category"].nunique()
        if not df.empty
        else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        display_metric(
            "Total Spending",
            f"₹{total_expenses:,.2f}",
            "💸"
        )

    with col2:
        display_metric(
            "Transactions",
            f"{transaction_count}",
            "🧾"
        )

    with col3:
        display_metric(
            "Average Expense",
            f"₹{average_expense:,.2f}",
            "📊"
        )

    with col4:
        display_metric(
            "Categories Used",
            f"{unique_categories}",
            "📁"
        )

    st.markdown(
        '<div class="section-title">📈 Spending Analytics</div>',
        unsafe_allow_html=True
    )

    if df.empty:
        st.info(
            "No expense records available. "
            "Add your first expense to view analytics."
        )
        return

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        category_data = (
            df.groupby("category", as_index=False)["amount"]
            .sum()
            .sort_values("amount", ascending=False)
        )

        fig_category = px.bar(
            category_data,
            x="category",
            y="amount",
            title="Spending by Category",
            labels={
                "category": "Category",
                "amount": "Amount (₹)"
            },
            text_auto=".2f"
        )

        fig_category.update_layout(
            template="plotly_white",
            showlegend=False,
            xaxis_title="Category",
            yaxis_title="Amount (₹)"
        )

        st.plotly_chart(
            fig_category,
            use_container_width=True
        )

    with chart_col2:
        monthly_data = df.copy()

        monthly_data["month"] = (
            monthly_data["date"]
            .dt.to_period("M")
            .astype(str)
        )

        monthly_data = (
            monthly_data.groupby("month", as_index=False)["amount"]
            .sum()
            .sort_values("month")
        )

        fig_monthly = px.line(
            monthly_data,
            x="month",
            y="amount",
            title="Monthly Spending Trend",
            markers=True,
            labels={
                "month": "Month",
                "amount": "Amount (₹)"
            }
        )

        fig_monthly.update_layout(
            template="plotly_white",
            xaxis_title="Month",
            yaxis_title="Amount (₹)"
        )

        st.plotly_chart(
            fig_monthly,
            use_container_width=True
        )


# =========================================================
# ADD EXPENSE
# =========================================================

def add_expense_page():
    """Display the add expense form."""

    st.markdown(
        '<div class="section-title">➕ Add New Expense</div>',
        unsafe_allow_html=True
    )

    st.write(
        "Enter your expense details using the form below."
    )

    with st.form("add_expense_form", clear_on_submit=True):

        col1, col2 = st.columns(2)

        with col1:
            expense_date = st.date_input(
                "Expense Date",
                value=date.today(),
                max_value=date.today()
            )

            category = st.selectbox(
                "Category",
                options=CATEGORIES
            )

        with col2:
            amount = st.number_input(
                "Amount (₹)",
                min_value=0.0,
                max_value=10_000_000.0,
                value=0.0,
                step=10.0,
                format="%.2f"
            )

            description = st.text_input(
                "Description",
                placeholder="e.g. Lunch, Bus ticket, Books"
            )

        submitted = st.form_submit_button(
            "💾 Save Expense",
            use_container_width=True
        )

        if submitted:

            is_valid, message = validate_expense(
                expense_date,
                category,
                description,
                amount
            )

            if not is_valid:
                st.error(message)

            else:
                df = load_expenses()

                new_expense = pd.DataFrame(
                    [{
                        "id": get_next_id(df),
                        "date": expense_date.strftime("%Y-%m-%d"),
                        "category": category,
                        "description": description.strip(),
                        "amount": round(amount, 2)
                    }]
                )

                updated_df = pd.concat(
                    [df, new_expense],
                    ignore_index=True
                )

                if save_expenses(updated_df):
                    st.success(
                        "✅ Expense added successfully!"
                    )
                    st.rerun()


# =========================================================
# EXPENSE HISTORY
# =========================================================

def expense_history_page():
    """Display searchable and filterable expenses."""

    st.markdown(
        '<div class="section-title">📋 Expense History</div>',
        unsafe_allow_html=True
    )

    df = load_expenses()

    if df.empty:
        st.info(
            "No expenses found. Add an expense to view history."
        )
        return

    filter_col1, filter_col2 = st.columns(2)

    with filter_col1:
        selected_category = st.selectbox(
            "Filter by Category",
            ["All Categories"] + CATEGORIES
        )

    with filter_col2:
        search_text = st.text_input(
            "Search Description",
            placeholder="Search expenses..."
        )

    filtered_df = df.copy()

    if selected_category != "All Categories":
        filtered_df = filtered_df[
            filtered_df["category"] == selected_category
        ]

    if search_text.strip():
        filtered_df = filtered_df[
            filtered_df["description"]
            .astype(str)
            .str.contains(
                search_text.strip(),
                case=False,
                na=False
            )
        ]

    display_df = filtered_df.copy()

    display_df["date"] = (
        display_df["date"]
        .dt.strftime("%Y-%m-%d")
    )

    display_df["amount"] = (
        display_df["amount"].map(
            lambda x: f"₹{x:,.2f}"
        )
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "id": st.column_config.NumberColumn("ID"),
            "date": st.column_config.TextColumn("Date"),
            "category": st.column_config.TextColumn("Category"),
            "description": st.column_config.TextColumn(
                "Description"
            ),
            "amount": st.column_config.TextColumn("Amount")
        }
    )

    st.caption(
        f"Showing {len(filtered_df)} expense(s)"
    )

    csv_data = filtered_df.copy()

    csv_data["date"] = (
        csv_data["date"]
        .dt.strftime("%Y-%m-%d")
    )

    csv_download = csv_data.to_csv(index=False).encode(
        "utf-8"
    )

    st.download_button(
        label="⬇️ Download Filtered CSV",
        data=csv_download,
        file_name="filtered_expenses.csv",
        mime="text/csv",
        use_container_width=False
    )


# =========================================================
# DELETE EXPENSE
# =========================================================

def delete_expense_page():
    """Delete an expense using its ID."""

    st.markdown(
        '<div class="section-title">🗑️ Delete Expense</div>',
        unsafe_allow_html=True
    )

    df = load_expenses()

    if df.empty:
        st.info("No expenses available to delete.")
        return

    expense_ids = (
        df["id"]
        .dropna()
        .astype(int)
        .tolist()
    )

    selected_id = st.selectbox(
        "Select Expense ID",
        options=expense_ids
    )

    selected_expense = df[
        df["id"] == selected_id
    ]

    if not selected_expense.empty:
        expense = selected_expense.iloc[0]

        st.warning(
            f"Selected expense: "
            f"{expense['category']} | "
            f"{expense['description']} | "
            f"₹{expense['amount']:,.2f}"
        )

    confirm_delete = st.checkbox(
        "I confirm that I want to delete this expense."
    )

    if st.button(
        "🗑️ Delete Selected Expense",
        disabled=not confirm_delete,
        use_container_width=True
    ):

        updated_df = df[
            df["id"] != selected_id
        ].copy()

        if save_expenses(updated_df):
            st.success("✅ Expense deleted successfully!")
            st.rerun()


# =========================================================
# SIDEBAR NAVIGATION
# =========================================================

def main():

    initialize_file()

    df = load_expenses()

    st.sidebar.markdown(
        "## 💰 Expense Tracker"
    )

    st.sidebar.caption(
        "Personal Expense Management"
    )

    st.sidebar.divider()

    page = st.sidebar.radio(
        "Navigation",
        [
            "📊 Dashboard",
            "➕ Add Expense",
            "📋 Expense History",
            "🗑️ Delete Expense"
        ]
    )

    st.sidebar.divider()

    st.sidebar.info(
        "💡 Keep track of your daily spending "
        "and understand your financial habits."
    )

    if page == "📊 Dashboard":
        show_dashboard(df)

    elif page == "➕ Add Expense":
        add_expense_page()

    elif page == "📋 Expense History":
        expense_history_page()

    elif page == "🗑️ Delete Expense":
        delete_expense_page()

    st.sidebar.divider()

    st.sidebar.caption(
        "Built with Python & Streamlit"
    )


# =========================================================
# APPLICATION ENTRY POINT
# =========================================================

if __name__ == "__main__":
    main()
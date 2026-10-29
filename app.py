"""
Electricity Consumption Analysis Dashboard
===========================================
A beginner-friendly Streamlit dashboard to analyze electricity usage over time,
visualize consumption patterns, and estimate electricity bills.

Technologies: Python, Pandas, Matplotlib, Streamlit
"""

import os
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# ---------------------------------------------------------
# Streamlit Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Electricity Consumption Analysis",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# Custom Styling for Metric Cards & Clean Presentation
# ---------------------------------------------------------
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-label {
        font-size: 0.85rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #0F172A;
        margin-top: 4px;
    }
    .metric-subtitle {
        font-size: 0.8rem;
        color: #94A3B8;
        margin-top: 2px;
    }
    .footer-note {
        font-size: 0.85rem;
        color: #6B7280;
        text-align: center;
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid #E5E7EB;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Helper Functions: Data Loading and Validation
# ---------------------------------------------------------
def load_default_dataset() -> pd.DataFrame:
    """Load the built-in sample electricity consumption dataset."""
    default_path = os.path.join(os.path.dirname(__file__), "electricity.csv")
    if not os.path.exists(default_path):
        # Fallback to local working directory if running from different root
        default_path = "electricity.csv"
    return pd.read_csv(default_path)


def validate_and_clean_data(df: pd.DataFrame):
    """
    Validate dataset structure, parse dates, convert consumption,
    and filter out invalid/negative values.

    Returns:
        cleaned_df (pd.DataFrame): Validated and sorted DataFrame.
        warnings (list of str): List of warning messages to display.
    """
    warnings = []

    # Check required columns (case-insensitive mapping)
    col_map = {col.strip().lower(): col for col in df.columns}
    if "date" not in col_map or "consumption_kwh" not in col_map:
        raise ValueError(
            "The uploaded file must contain 'Date' and 'Consumption_kWh' columns. "
            f"Found columns: {list(df.columns)}"
        )

    # Standardize column names
    standard_df = pd.DataFrame()
    standard_df["Date"] = df[col_map["date"]]
    standard_df["Consumption_kWh"] = df[col_map["consumption_kwh"]]

    initial_count = len(standard_df)

    # Check for empty dataset
    if initial_count == 0:
        raise ValueError("The uploaded dataset contains 0 rows.")

    # 1. Parse Date column
    standard_df["Date"] = pd.to_datetime(standard_df["Date"], errors="coerce")
    invalid_dates = standard_df["Date"].isna().sum()
    if invalid_dates > 0:
        warnings.append(f"Found {invalid_dates} row(s) with missing or invalid date formats; removed.")

    # 2. Parse Consumption column
    standard_df["Consumption_kWh"] = pd.to_numeric(
        standard_df["Consumption_kWh"], errors="coerce"
    )
    invalid_consumption = standard_df["Consumption_kWh"].isna().sum()
    if invalid_consumption > 0:
        warnings.append(
            f"Found {invalid_consumption} row(s) with non-numeric or missing consumption values; removed."
        )

    # Filter out NaNs
    clean_df = standard_df.dropna(subset=["Date", "Consumption_kWh"]).copy()

    # 3. Handle Negative Consumption values
    negative_rows = clean_df["Consumption_kWh"] < 0
    neg_count = negative_rows.sum()
    if neg_count > 0:
        warnings.append(
            f"Found {neg_count} row(s) with negative electricity consumption (< 0 kWh); removed."
        )
        clean_df = clean_df[~negative_rows].copy()

    if clean_df.empty:
        raise ValueError("No valid rows remaining after data validation and cleaning.")

    # Sort sequentially by date
    clean_df = clean_df.sort_values(by="Date").reset_index(drop=True)

    return clean_df, warnings


# ---------------------------------------------------------
# Helper Functions: Statistics Calculations
# ---------------------------------------------------------
def calculate_statistics(df: pd.DataFrame, tariff: float) -> dict:
    """
    Calculate summary statistics and estimated billing metrics.

    Parameters:
        df: Filtered DataFrame with 'Date' and 'Consumption_kWh'.
        tariff: Rate per kWh in INR (₹).

    Returns:
        dict containing total, average, highest day, lowest day, and costs.
    """
    total_consumption = float(df["Consumption_kWh"].sum())
    avg_consumption = float(df["Consumption_kWh"].mean())

    # Find highest consumption day
    max_idx = df["Consumption_kWh"].idxmax()
    max_row = df.loc[max_idx]
    highest_day = {
        "date": max_row["Date"].strftime("%d %b %Y"),
        "kwh": float(max_row["Consumption_kWh"]),
    }

    # Find lowest consumption day
    min_idx = df["Consumption_kWh"].idxmin()
    min_row = df.loc[min_idx]
    lowest_day = {
        "date": min_row["Date"].strftime("%d %b %Y"),
        "kwh": float(min_row["Consumption_kWh"]),
    }

    # Estimated costs
    # Formula: Estimated Bill = Total consumption * Electricity tariff
    total_bill = total_consumption * tariff
    avg_daily_cost = avg_consumption * tariff

    return {
        "total_kwh": total_consumption,
        "avg_daily_kwh": avg_consumption,
        "highest_day": highest_day,
        "lowest_day": lowest_day,
        "total_bill": total_bill,
        "avg_daily_cost": avg_daily_cost,
        "num_days": len(df),
    }


# ---------------------------------------------------------
# Helper Functions: Matplotlib Data Visualizations
# ---------------------------------------------------------
def plot_daily_line_chart(df: pd.DataFrame):
    """Line Chart: Daily electricity consumption over time with mean line."""
    fig, ax = plt.subplots(figsize=(10, 4.5))

    dates = df["Date"]
    consumption = df["Consumption_kWh"]
    mean_val = consumption.mean()

    ax.plot(
        dates,
        consumption,
        marker="o",
        markersize=4,
        linewidth=2,
        color="#2563EB",
        label="Daily Consumption",
    )
    ax.axhline(
        mean_val,
        color="#DC2626",
        linestyle="--",
        linewidth=1.5,
        label=f"Average ({mean_val:.2f} kWh)",
    )

    ax.set_title("1. Daily Electricity Consumption Over Time", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Date", fontsize=10)
    ax.set_ylabel("Consumption (kWh)", fontsize=10)
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(loc="upper right", frameon=True)
    fig.autofmt_xdate(rotation=30)
    plt.tight_layout()
    return fig


def plot_daily_bar_chart(df: pd.DataFrame):
    """Bar Chart: Compare electricity consumption across days."""
    fig, ax = plt.subplots(figsize=(10, 4.5))

    date_labels = df["Date"].dt.strftime("%d %b")
    consumption = df["Consumption_kWh"]

    bars = ax.bar(date_labels, consumption, color="#3B82F6", edgecolor="#1D4ED8", alpha=0.85)

    # Add value labels on top of bars if dataset is compact
    if len(df) <= 35:
        for bar in bars:
            height = bar.get_height()
            ax.annotate(
                f"{height:.1f}",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=7.5,
                rotation=90 if len(df) > 20 else 0,
            )

    ax.set_title("2. Daily Electricity Consumption Comparison", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Date", fontsize=10)
    ax.set_ylabel("Consumption (kWh)", fontsize=10)
    ax.grid(axis="y", linestyle=":", alpha=0.6)
    plt.xticks(rotation=60, ha="right", fontsize=8)
    plt.tight_layout()
    return fig


def plot_weekly_pie_chart(df: pd.DataFrame):
    """Pie Chart: Show each week's share of total consumption."""
    df_copy = df.copy()

    # Create Weekly Buckets using Period (Monday to Sunday)
    # Using ISO calendar week for robust grouping
    df_copy["Week_Label"] = df_copy["Date"].dt.to_period("W-SUN").apply(
        lambda p: f"{p.start_time.strftime('%b %d')} - {p.end_time.strftime('%b %d')}"
    )

    weekly_totals = df_copy.groupby("Week_Label", sort=False)["Consumption_kWh"].sum()

    fig, ax = plt.subplots(figsize=(6.5, 5))
    colors = ["#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899", "#14B8A6"]

    wedges, texts, autotexts = ax.pie(
        weekly_totals,
        labels=weekly_totals.index,
        autopct="%1.1f%%",
        startangle=140,
        colors=colors[: len(weekly_totals)],
        textprops={"fontsize": 9},
        wedgeprops={"edgecolor": "white", "linewidth": 1.5},
    )

    for autotext in autotexts:
        autotext.set_fontsize(8.5)
        autotext.set_weight("bold")

    ax.set_title("3. Weekly Share of Total Consumption", fontsize=13, fontweight="bold", pad=12)
    plt.tight_layout()
    return fig


def plot_consumption_histogram(df: pd.DataFrame):
    """Histogram: Show the distribution of daily electricity consumption."""
    fig, ax = plt.subplots(figsize=(6.5, 5))

    consumption = df["Consumption_kWh"]
    mean_val = consumption.mean()
    median_val = consumption.median()

    counts, bins, patches = ax.hist(
        consumption,
        bins=10,
        color="#6366F1",
        edgecolor="#312E81",
        alpha=0.8,
    )

    ax.axvline(
        mean_val,
        color="#DC2626",
        linestyle="--",
        linewidth=1.8,
        label=f"Mean: {mean_val:.1f} kWh",
    )
    ax.axvline(
        median_val,
        color="#059669",
        linestyle="-.",
        linewidth=1.8,
        label=f"Median: {median_val:.1f} kWh",
    )

    ax.set_title("4. Distribution of Daily Electricity Usage", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Daily Consumption (kWh)", fontsize=10)
    ax.set_ylabel("Number of Days (Frequency)", fontsize=10)
    ax.grid(axis="y", linestyle=":", alpha=0.6)
    ax.legend(loc="upper right", frameon=True)
    plt.tight_layout()
    return fig


def plot_weekday_average_chart(df: pd.DataFrame):
    """Bar Chart: Compare average consumption across weekdays."""
    df_copy = df.copy()
    weekday_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    df_copy["Day_Name"] = df_copy["Date"].dt.day_name()
    weekday_avg = (
        df_copy.groupby("Day_Name")["Consumption_kWh"]
        .mean()
        .reindex(weekday_order)
        .dropna()
    )

    fig, ax = plt.subplots(figsize=(10, 4.5))

    # Color weekends differently to highlight leisure/home usage
    colors = [
        "#F59E0B" if day in ["Saturday", "Sunday"] else "#0284C7"
        for day in weekday_avg.index
    ]

    bars = ax.bar(
        weekday_avg.index,
        weekday_avg.values,
        color=colors,
        edgecolor="#0F172A",
        alpha=0.85,
        width=0.6,
    )

    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            f"{height:.2f} kWh",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
        )

    ax.set_title("5. Average Consumption Across Weekdays", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Day of the Week", fontsize=10)
    ax.set_ylabel("Average Consumption (kWh)", fontsize=10)
    ax.grid(axis="y", linestyle=":", alpha=0.6)
    plt.tight_layout()
    return fig


# ---------------------------------------------------------
# Main Application Flow
# ---------------------------------------------------------
def main():
    # Header Section
    st.markdown('<div class="main-title">⚡ Electricity Consumption Analysis</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">An interactive analytics dashboard to monitor electricity usage trends, '
        "break down weekly consumption patterns, and estimate energy bills.</div>",
        unsafe_allow_html=True,
    )

    # ---------------------------------------------------------
    # Sidebar: Data Source, Tariff, and Date Filtering
    # ---------------------------------------------------------
    st.sidebar.header("⚙️ Configuration & Filters")

    # Data Source Selection
    data_source = st.sidebar.radio(
        "Choose Data Source:",
        options=["Use Sample Dataset", "Upload Custom CSV"],
        index=0,
        help="Use the built-in 42-day sample dataset or upload your own CSV file.",
    )

    raw_df = None
    is_sample_dataset = True

    if data_source == "Upload Custom CSV":
        uploaded_file = st.sidebar.file_uploader(
            "Upload your electricity CSV file",
            type=["csv"],
            help="File must contain 'Date' and 'Consumption_kWh' columns.",
        )
        if uploaded_file is not None:
            try:
                raw_df = pd.read_csv(uploaded_file)
                is_sample_dataset = False
            except Exception as e:
                st.sidebar.error(f"Error reading uploaded CSV: {e}")
                st.stop()
        else:
            st.info("👆 Please upload a CSV file via the sidebar, or select 'Use Sample Dataset' to explore.")
            st.stop()
    else:
        try:
            raw_df = load_default_dataset()
            is_sample_dataset = True
        except Exception as e:
            st.error(f"Failed to load sample dataset: {e}")
            st.stop()

    # Validate and Clean Dataset
    try:
        clean_df, warnings = validate_and_clean_data(raw_df)
    except Exception as e:
        st.error(f"⚠️ Dataset Validation Error: {e}")
        st.stop()

    # Display data warnings if any exist
    if warnings:
        for w in warnings:
            st.sidebar.warning(f"⚠️ {w}")

    # Electricity Tariff Input
    st.sidebar.subheader("💡 Tariff Setting")
    tariff = st.sidebar.number_input(
        "Electricity Tariff (₹ per kWh):",
        min_value=0.0,
        value=7.50,
        step=0.25,
        format="%.2f",
        help="Rate charged per unit (kWh). Used to calculate estimated cost.",
    )

    # Date Range Filter
    st.sidebar.subheader("📅 Date Range Filter")
    min_date = clean_df["Date"].min().date()
    max_date = clean_df["Date"].max().date()

    selected_date_range = st.sidebar.date_input(
        "Select Date Range:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    # Handle single date vs date range selection in Streamlit
    if isinstance(selected_date_range, (tuple, list)):
        if len(selected_date_range) == 2:
            start_date, end_date = selected_date_range
        elif len(selected_date_range) == 1:
            start_date = end_date = selected_date_range[0]
        else:
            start_date, end_date = min_date, max_date
    else:
        start_date = end_date = selected_date_range

    # Filter DataFrame according to the selected range
    filtered_df = clean_df[
        (clean_df["Date"].dt.date >= start_date) & (clean_df["Date"].dt.date <= end_date)
    ].copy()

    if filtered_df.empty:
        st.warning("No records found for the selected date range. Please widen your filter.")
        st.stop()

    # Informational notice about Sample Data & Billing calculation
    if is_sample_dataset:
        st.info(
            "📌 **Sample Dataset Active:** You are viewing realistic sample data for demonstration "
            "(not actual meter readings). You can upload your own CSV using the sidebar.",
            icon="ℹ️",
        )

    # ---------------------------------------------------------
    # Statistical Analysis: Metric Cards
    # ---------------------------------------------------------
    stats = calculate_statistics(filtered_df, tariff)

    st.markdown("### 📊 Key Electricity Usage & Cost Statistics")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Total Electricity Consumed</div>
                <div class="metric-value">{stats['total_kwh']:.2f} <span style="font-size:1rem;color:#64748B;">kWh</span></div>
                <div class="metric-subtitle">Across {stats['num_days']} recorded day(s)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Average Daily Consumption</div>
                <div class="metric-value">{stats['avg_daily_kwh']:.2f} <span style="font-size:1rem;color:#64748B;">kWh/day</span></div>
                <div class="metric-subtitle">Mean energy per day</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Estimated Total Bill</div>
                <div class="metric-value">₹ {stats['total_bill']:,.2f}</div>
                <div class="metric-subtitle">Based on ₹{tariff:.2f} / kWh</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")  # Spacing

    col4, col5, col6 = st.columns(3)
    with col4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Highest Consumption Day</div>
                <div class="metric-value">{stats['highest_day']['kwh']:.2f} <span style="font-size:1rem;color:#64748B;">kWh</span></div>
                <div class="metric-subtitle">On {stats['highest_day']['date']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col5:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Lowest Consumption Day</div>
                <div class="metric-value">{stats['lowest_day']['kwh']:.2f} <span style="font-size:1rem;color:#64748B;">kWh</span></div>
                <div class="metric-subtitle">On {stats['lowest_day']['date']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col6:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Average Daily Cost</div>
                <div class="metric-value">₹ {stats['avg_daily_cost']:,.2f}</div>
                <div class="metric-subtitle">Expected daily expenditure</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.caption(
        "⚠️ **Billing Note:** The estimated bill is calculated as `Total Consumption × Electricity Tariff`. "
        "It excludes fixed meter rent/demand charges, local municipal taxes, cess, and government subsidies unless included in the tariff."
    )

    st.markdown("---")

    # ---------------------------------------------------------
    # Visualizations Section
    # ---------------------------------------------------------
    st.markdown("### 📈 Visual Analysis")

    # Chart 1: Daily Line Chart (Full width)
    fig_line = plot_daily_line_chart(filtered_df)
    st.pyplot(fig_line, use_container_width=True)
    plt.close(fig_line)

    # Chart 2: Daily Bar Chart (Full width)
    fig_bar = plot_daily_bar_chart(filtered_df)
    st.pyplot(fig_bar, use_container_width=True)
    plt.close(fig_bar)

    # Row with Pie Chart & Histogram
    c_left, c_right = st.columns(2)
    with c_left:
        fig_pie = plot_weekly_pie_chart(filtered_df)
        st.pyplot(fig_pie, use_container_width=True)
        plt.close(fig_pie)

    with c_right:
        fig_hist = plot_consumption_histogram(filtered_df)
        st.pyplot(fig_hist, use_container_width=True)
        plt.close(fig_hist)

    # Chart 5: Weekday Average (Full width)
    fig_weekday = plot_weekday_average_chart(filtered_df)
    st.pyplot(fig_weekday, use_container_width=True)
    plt.close(fig_weekday)

    st.markdown("---")

    # ---------------------------------------------------------
    # Tabular Data Section
    # ---------------------------------------------------------
    st.markdown("### 📋 Filtered Dataset Records")

    display_df = filtered_df.copy()
    display_df["Date"] = display_df["Date"].dt.strftime("%Y-%m-%d")
    display_df["Estimated_Cost_INR"] = (display_df["Consumption_kWh"] * tariff).round(2)
    display_df.rename(
        columns={
            "Date": "Date",
            "Consumption_kWh": "Consumption (kWh)",
            "Estimated_Cost_INR": f"Estimated Cost (₹ @ {tariff:.2f}/kWh)",
        },
        inplace=True,
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )

    # Download Filtered Data as CSV
    csv_data = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv_data,
        file_name="filtered_electricity_consumption.csv",
        mime="text/csv",
    )

    # Footer
    st.markdown(
        """
        <div class="footer-note">
            Electricity Consumption Analysis Project &bull; Built with Python, Streamlit, Pandas & Matplotlib
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()

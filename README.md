<div align="center">

# ⚡ Electricity Consumption Analysis Dashboard

**A modern, beginner-friendly analytics dashboard to monitor electricity usage trends, analyze weekly patterns, and estimate energy bills.**

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Pandas](https://img.shields.io/badge/Pandas-2.0%2B-150458?logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Matplotlib](https://img.shields.io/badge/Matplotlib-3.7%2B-11557c)](https://matplotlib.org/)
[![Status](https://img.shields.io/badge/Status-Complete-success)]()
[![Project Type](https://img.shields.io/badge/Academic-Mini--Project-orange)]()

[Key Features](#-key-features) • [Project Structure](#-project-structure) • [Installation & Run](#-quick-start-guide) • [Visualizations](#-data-visualizations) • [Viva & Presentation Guide](#-college-mini-project-viva-guide)

</div>

---

## 📌 Project Overview

The **Electricity Consumption Analysis Dashboard** is an intuitive, interactive data analytics tool developed in Python. Designed for household energy tracking and college mini-project demonstrations, it bridges the gap between raw meter logs and actionable insights.

Users can analyze daily power consumption patterns, identify peak usage periods, visualize weekly distributions, and estimate their electricity bill using custom tariff rates in Indian Rupees (**₹ per kWh**).

> **Note on Sample Data:** The included `electricity.csv` provides 42 days of illustrative household usage data. It does not represent live electricity meter readings. Users can upload their own CSV anytime via the sidebar.

---

## ✨ Key Features

### 1. 📂 Dataset Management & Validation
* **Zero Configuration Startup:** Pre-loaded with realistic sample data so the application works out-of-the-box.
* **Custom CSV Upload:** Users can upload their own electricity consumption files.
* **Robust Validation Pipeline:** Automatically detects and filters:
  * Missing or malformed dates (`YYYY-MM-DD`).
  * Missing, null, or non-numeric consumption values.
  * Negative energy consumption readings (`< 0 kWh`).
  * Displays user-friendly warning badges in the sidebar when anomalies are resolved.

### 2. 📊 Real-Time Statistical Summary
Dynamic KPI metric cards at the top of the dashboard recalculate instantly with every filter change:
* **Total Electricity Consumed (kWh)** across the selected time period.
* **Average Daily Consumption (kWh/day)** to gauge normal household demand.
* **Highest Consumption Day:** Exact date and peak consumption in kWh.
* **Lowest Consumption Day:** Minimum consumption benchmark and date.
* **Estimated Total Bill (₹):** Computed using the formula:
  $$\text{Estimated Bill} = \text{Total Consumption (kWh)} \times \text{Tariff (₹/kWh)}$$
* **Average Daily Cost (₹):** Estimated financial expenditure per day.

> ℹ️ *Disclaimer:* The estimated bill strictly reflects energy consumption charges. Fixed meter fees, taxes, fuel adjustment surcharges, and government subsidies are excluded unless incorporated into the unit tariff.

### 3. 📉 Interactive Filtering
* **Date Range Selector:** Dynamically inspect specific weeks, months, or custom date spans.
* **Custom Electricity Tariff (₹/kWh):** Adjustable number input to reflect local discom / utility rates.
* **Tabular Data Viewer & CSV Export:** Download filtered records with computed daily costs in one click.

---

## 📈 Data Visualizations

All visual charts are generated using **Matplotlib** with clean typography, clear axis labels, and high readability:

| # | Chart Type | Description & Purpose |
|---|---|---|
| **1** | **Line Chart** | **Daily Consumption Over Time:** Tracks temporal trends and highlights fluctuations with a red dashed mean reference line. |
| **2** | **Bar Chart** | **Daily Comparison:** Displays exact day-to-day power usage with vertical data annotations for quick comparison. |
| **3** | **Pie Chart** | **Weekly Share of Total:** Categorizes consumption into ISO weekly buckets to show which week contributed most to the overall bill. |
| **4** | **Histogram** | **Distribution Analysis:** Illustrates consumption frequency, showing the central tendency with mean and median markers. |
| **5** | **Weekday Bar Chart** | **Day-of-Week Comparison:** Highlights differences between weekday routines and weekend peaks with differentiated color schemes. |

---

## 📁 Project Structure

```text
electricity-analysis/
│
├── app.py              # Main Streamlit dashboard application source code
├── electricity.csv     # Sample 42-day illustrative consumption dataset
├── requirements.txt    # Python dependencies (Streamlit, Pandas, Matplotlib)
└── README.md           # Modern project documentation and user manual
```

---

## 📋 Dataset Format

The application expects a CSV file containing two primary columns:

| Column Header | Data Type | Example | Description |
|---|---|---|---|
| `Date` | Date String (`YYYY-MM-DD`) | `2024-03-15` | Date of the meter reading |
| `Consumption_kWh` | Numeric (Float/Int) | `17.2` | Active electricity usage in kilowatt-hours |

### Sample Data Snippet (`electricity.csv`):
```csv
Date,Consumption_kWh
2024-03-01,14.5
2024-03-02,18.2
2024-03-03,19.8
2024-03-04,13.4
...
```

---

## 🚀 Quick Start Guide

### Prerequisites
Make sure you have **Python 3.9** or higher installed on your system.

### Step 1: Open Terminal / Command Prompt
Navigate to the project folder:
```bash
cd electricity-analysis
```

### Step 2: Install Dependencies
Install all required libraries using `pip`:
```bash
pip install -r requirements.txt
```

### Step 3: Launch the Application
Run the Streamlit application:
```bash
streamlit run app.py
```

The application will start immediately and automatically open in your default browser at:
`http://localhost:8501`

---

## 📐 Formulas & Calculation Methodology

1. **Total Consumption:**
   $$\text{Total (kWh)} = \sum_{i=1}^{N} \text{Consumption}_i$$

2. **Average Daily Consumption:**
   $$\text{Daily Average (kWh)} = \frac{\text{Total (kWh)}}{N}$$

3. **Estimated Electricity Bill:**
   $$\text{Bill (₹)} = \text{Total (kWh)} \times \text{Tariff Rate (₹/kWh)}$$

4. **Average Daily Cost:**
   $$\text{Daily Cost (₹)} = \text{Daily Average (kWh)} \times \text{Tariff Rate (₹/kWh)}$$

---

## 🎓 College Mini-Project Viva Guide

If you are presenting this project for an academic evaluation, lab exam, or viva, keep these talking points in mind:

### Q1: Why did you choose Streamlit instead of Flask or Django?
> **Answer:** Streamlit is purpose-built for data science and analytics. It provides native reactive data binding without requiring complex HTML/CSS or JavaScript frontend code, allowing rapid development of dashboards with live widget updates.

### Q2: How does the application prevent crashes if an uploaded CSV contains bad data?
> **Answer:** Through the modular `validate_and_clean_data()` function:
> 1. It verifies required column names regardless of letter casing.
> 2. Coerces dates using `pd.to_datetime(..., errors='coerce')` and flags unparseable formats.
> 3. Coerces numbers using `pd.to_numeric(..., errors='coerce')` and filters out nulls/strings.
> 4. Validates that energy usage cannot be negative ($\ge 0$ kWh).
> 5. Logs informative warnings to the UI while keeping the app stable.

### Q3: What insights can a consumer gain from the weekday chart?
> **Answer:** The weekday analysis groups energy usage by day of the week. This reveals whether consumption surges during weekends (due to air conditioning, entertainment appliances, laundry) or remains constant, enabling targeted energy-saving habits.

---

## 🛡️ License & Academic Integrity

This project is open-source and created for educational purposes. Feel free to adapt and expand it for academic projects, workshops, and learning!

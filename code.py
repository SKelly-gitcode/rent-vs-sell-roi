import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("🏠 Rent vs Sell Investment Analysis")

# Sidebar Inputs
st.sidebar.header("Investment Parameters")
home_value = st.sidebar.number_input("Home Value", value=1_250_000, step=1000)
mortgage_balance = st.sidebar.number_input("Mortgage Balance", value=739_000, step=1000)
mortgage_rate = st.sidebar.number_input("Mortgage Interest Rate", value=0.0499, step=0.001, format="%.4f")
monthly_payment = st.sidebar.number_input("Monthly Mortgage Payment", value=4100, step=100)
annual_taxes = st.sidebar.number_input("Annual Taxes", value=5000, step=100)
annual_insurance = st.sidebar.number_input("Annual Insurance", value=2000, step=100)
annual_other_fees = st.sidebar.number_input("Annual Other Fees", value=1000, step=100)
monthly_rent_income = st.sidebar.number_input("Monthly Rent Income", value=3750, step=50)
rent_increase_rate = st.sidebar.number_input("Annual Rent Increase Rate", value=0.02, step=0.001, format="%.3f")
maintenance_rate = st.sidebar.number_input("Annual Maintenance Rate", value=0.01, step=0.001, format="%.3f")
expense_inflation_rate = st.sidebar.number_input("Annual Expense Inflation Rate", value=0.02, step=0.001, format="%.3f")
investor_debt = st.sidebar.number_input("Investor Debt", value=100_000, step=1000)
realtor_fee_rate = st.sidebar.number_input("Realtor Fee Rate", value=0.05, step=0.005, format="%.3f")
mortgage_penalty = st.sidebar.number_input("Mortgage Penalty", value=9000, step=500)
market_return = st.sidebar.number_input("Annual Market Return", value=0.07, step=0.005, format="%.3f")
home_appreciation_rate = st.sidebar.number_input("Annual Home Appreciation Rate", value=0.03, step=0.001, format="%.3f")
projection_years = st.sidebar.slider("Projection Period (Years)", 1, 30, 10)

# Mortgage Interest Calculation
def mortgage_interest(balance, rate):
    return balance * rate

# Scenario Calculations
rent_df = []
sell_df = []
remaining_balance_rent = mortgage_balance
remaining_balance_sell = mortgage_balance
current_home_value = home_value
current_rent_income = monthly_rent_income * 12

for year in range(1, projection_years + 1):
    # Rent scenario
    interest_payment = mortgage_interest(remaining_balance_rent, mortgage_rate)
    principal_payment = (monthly_payment * 12) - interest_payment
    remaining_balance_rent -= principal_payment
    annual_maintenance = current_home_value * maintenance_rate
    annual_expenses = (interest_payment + annual_taxes + annual_insurance + annual_other_fees + annual_maintenance) * ((1 + expense_inflation_rate) ** (year - 1))
    annual_rental_income = current_rent_income * ((1 + rent_increase_rate) ** (year - 1))
    net_cash_flow = annual_rental_income - annual_expenses
    current_home_value *= (1 + home_appreciation_rate)

    rent_df.append({
        "Year": year,
        "Home Value": current_home_value,
        "Remaining Mortgage": remaining_balance_rent,
        "Annual Cash Flow": net_cash_flow,
        "Accumulated Equity": current_home_value - remaining_balance_rent - investor_debt
    })

    # Sell scenario (corrected)
    annual_expenses_sell = (monthly_payment * 12 + annual_taxes + annual_insurance + annual_other_fees + annual_maintenance) * ((1 + expense_inflation_rate) ** (year - 1))
    annual_savings = annual_expenses_sell - annual_rental_income

    sell_df.append({
        "Year": year,
        "Annual Savings": annual_savings
    })

sale_proceeds = home_value * (1 - realtor_fee_rate) - mortgage_balance - investor_debt - mortgage_penalty
investment_balance = sale_proceeds

investment_balances = []
for year in sell_df:
    investment_balance = investment_balance * (1 + market_return) + year["Annual Savings"]
    investment_balances.append(investment_balance)

# Results DataFrame
rent_df = pd.DataFrame(rent_df)
sell_df = pd.DataFrame(sell_df)
sell_df["Investment Balance"] = investment_balances

# Display Tables
st.subheader("Year-over-Year Details")
col1, col2 = st.columns(2)
with col1:
    st.write("### Rent Scenario")
    st.dataframe(rent_df.set_index("Year").style.format("${:,.2f}"))
with col2:
    st.write("### Sell & Invest Scenario")
    st.dataframe(sell_df.set_index("Year").style.format("${:,.2f}"))

# Graph
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(rent_df["Year"], rent_df["Accumulated Equity"], label="Rent Scenario Equity")
ax.plot(sell_df["Year"], sell_df["Investment Balance"], label="Sell & Invest Scenario")
ax.set_xlabel("Year")
ax.set_ylabel("Value ($)")
ax.set_title("Investment Scenarios Over Time")
ax.legend()
ax.grid(True)

st.pyplot(fig)

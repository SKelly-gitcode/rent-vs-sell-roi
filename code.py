import streamlit as st
import numpy as np
import pandas as pd

st.set_page_config(layout="centered")
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
maintenance_rate = st.sidebar.number_input("Annual Maintenance Rate", value=0.01, step=0.001, format="%.3f")
investor_debt = st.sidebar.number_input("Investor Debt", value=100_000, step=1000)
realtor_fee_rate = st.sidebar.number_input("Realtor Fee Rate", value=0.05, step=0.005, format="%.3f")
mortgage_penalty = st.sidebar.number_input("Mortgage Penalty", value=9000, step=500)
market_return = st.sidebar.number_input("Annual Market Return", value=0.07, step=0.005, format="%.3f")
home_appreciation_rate = st.sidebar.number_input("Annual Home Appreciation Rate", value=0.03, step=0.001, format="%.3f")
projection_years = st.sidebar.slider("Projection Period (Years)", 1, 30, 10)

# Mortgage Interest Calculation
def mortgage_interest(balance, rate):
    return balance * rate

# Scenario 1: Keep and Rent
remaining_balance = mortgage_balance
home_val_scenario = home_value
cash_flow_rent = []

for year in range(1, projection_years + 1):
    interest_payment = mortgage_interest(remaining_balance, mortgage_rate)
    principal_payment = (monthly_payment * 12) - interest_payment
    remaining_balance -= principal_payment
    annual_maintenance = home_val_scenario * maintenance_rate

    annual_expenses = interest_payment + annual_taxes + annual_insurance + annual_other_fees + annual_maintenance
    annual_rental_income = monthly_rent_income * 12

    net_cash_flow = annual_rental_income - annual_expenses
    cash_flow_rent.append(net_cash_flow)

    home_val_scenario *= (1 + home_appreciation_rate)

final_equity_rent = home_val_scenario - remaining_balance - investor_debt

# Scenario 2: Sell and Invest
sale_proceeds = home_value * (1 - realtor_fee_rate) - mortgage_balance - investor_debt - mortgage_penalty
annual_savings = []
remaining_balance_sell = mortgage_balance

for year in range(1, projection_years + 1):
    interest_payment = mortgage_interest(remaining_balance_sell, mortgage_rate)
    principal_payment = (monthly_payment * 12) - interest_payment
    remaining_balance_sell -= principal_payment

    annual_maintenance = home_val_scenario * maintenance_rate
    annual_expenses = interest_payment + annual_taxes + annual_insurance + annual_other_fees + annual_maintenance
    annual_rental_income = monthly_rent_income * 12

    net_cash_flow = annual_expenses - annual_rental_income
    annual_savings.append(net_cash_flow)

investment_balance = sale_proceeds

for saving in annual_savings:
    investment_balance = investment_balance * (1 + market_return) + saving

# Results
results_df = pd.DataFrame({
    "Scenario": ["Keep & Rent", "Sell & Invest"],
    "Final Equity / Investment": [final_equity_rent, investment_balance],
    "Total Net Gain": [final_equity_rent + sum(cash_flow_rent), investment_balance]
})

st.subheader("Comparison of Scenarios")
st.dataframe(results_df.set_index("Scenario").style.format("${:,.2f}"))

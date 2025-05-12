import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(layout="centered")
st.title("🏠 Rent vs Sell ROI Forecaster")

st.sidebar.header("Scenario Parameters")
years = st.sidebar.slider("Years to Project", 1, 30, 15)
discount_rate = st.sidebar.slider("Inflation/Discount Rate (%)", 0.0, 10.0, 2.0) / 100

# Rent Scenario Inputs
st.sidebar.subheader("Renting the Property")
initial_home_value = st.sidebar.number_input("Current Home Value ($)", value=1000000.0, step=10000.0)
monthly_rent = st.sidebar.number_input("Monthly Rent ($)", value=3000.0, step=100.0)
rent_increase = st.sidebar.slider("Annual Rent Increase (%)", 0.0, 10.0, 2.0) / 100
home_growth = st.sidebar.slider("Annual Home Value Growth (%)", 0.0, 10.0, 4.0) / 100

property_tax = st.sidebar.number_input("Annual Property Tax ($)", value=6000.0)
maintenance = st.sidebar.number_input("Annual Maintenance ($)", value=5000.0)
insurance = st.sidebar.number_input("Annual Insurance ($)", value=2000.0)
management_fees = st.sidebar.number_input("Annual Management Fees ($)", value=3000.0)

# Sell Scenario Inputs
st.sidebar.subheader("Selling and Investing")
net_proceeds = st.sidebar.number_input("Net Proceeds from Sale ($)", value=900000.0, step=10000.0)
rate_of_return = st.sidebar.slider("Annual Investment Return (%)", 0.0, 12.0, 6.0) / 100

# Projection Calculations
years_range = np.arange(1, years + 1)
rent_income = np.array([(monthly_rent * 12) * ((1 + rent_increase) ** (i - 1)) for i in years_range])
fixed_costs = property_tax + maintenance + insurance + management_fees
net_rent = np.array([rent_income[i - 1] - fixed_costs for i in years_range])
cum_rent = np.cumsum(net_rent)
house_value = np.array([initial_home_value * ((1 + home_growth) ** i) for i in years_range])
rent_scenario_value = cum_rent + house_value

investment_value = np.array([net_proceeds * ((1 + rate_of_return) ** i) for i in years_range])
discount_factors = np.array([(1 + discount_rate) ** i for i in years_range])
adjusted_rent_value = rent_scenario_value / discount_factors
adjusted_investment_value = investment_value / discount_factors

df = pd.DataFrame({
    "Year": years_range,
    "Rent + Equity": adjusted_rent_value,
    "Invested Proceeds": adjusted_investment_value
})

# Plot
st.subheader("Projected ROI Over Time")
fig, ax = plt.subplots()
ax.plot(df["Year"], df["Rent + Equity"], label="Rent + Home Equity")
ax.plot(df["Year"], df["Invested Proceeds"], label="Invested Sale Proceeds")
ax.set_xlabel("Year")
ax.set_ylabel("Value ($)")
ax.set_title("Rent vs Sell ROI Comparison")
ax.legend()
st.pyplot(fig)

# Crossover Point
crossover = np.where(adjusted_investment_value > adjusted_rent_value)[0]
if len(crossover) > 0:
    st.success(f"💡 Investment surpasses rent strategy in year {crossover[0] + 1}.")
else:
    st.info("💡 Rent strategy remains superior over the selected timeframe.")

with st.expander("📊 Show Yearly Data Table"):
    st.dataframe(df.style.format("{:.0f}"))

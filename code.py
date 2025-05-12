import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(layout="centered")
st.title("🏠 Rent vs Sell ROI Forecaster")

st.sidebar.header("Scenario Parameters")
years = st.sidebar.slider("Years to Project", 1, 30, 15)
discount_rate = st.sidebar.slider("Inflation/Discount Rate (%)", 0.0, 10.0, 2.0) / 100
opportunity_cost_rate = st.sidebar.slider("Opportunity Cost of Negative Cashflow (%)", 0.0, 10.0, 6.0) / 100
income_tax_rate = st.sidebar.slider("Tax on Rental Income (%)", 0.0, 50.0, 30.0) / 100

# Rent Scenario Inputs
st.sidebar.subheader("Renting the Property")
initial_home_value = st.sidebar.number_input("Current Home Value ($)", value=1000000.0, step=10000.0)
mortgage_balance = st.sidebar.number_input("Current Mortgage Balance ($)", value=700000.0, step=10000.0)
mortgage_rate = st.sidebar.slider("Mortgage Interest Rate (%)", 0.0, 10.0, 3.0) / 100
monthly_mortgage_payment = st.sidebar.number_input("Monthly Mortgage Payment ($)", value=4100.0, step=50.0)
mortgage_term_years = st.sidebar.slider("Remaining Mortgage Term (Years)", 1, 30, 22)

monthly_rent = st.sidebar.number_input("Monthly Rent ($)", value=3000.0, step=100.0)
rent_increase = st.sidebar.slider("Annual Rent Increase (%)", 0.0, 10.0, 2.0) / 100
home_growth = st.sidebar.slider("Annual Home Value Growth (%)", 0.0, 10.0, 4.0) / 100

property_tax = st.sidebar.number_input("Annual Property Tax ($)", value=6000.0)
maintenance = st.sidebar.number_input("Annual Maintenance ($)", value=5000.0)
insurance = st.sidebar.number_input("Annual Insurance ($)", value=2000.0)
management_fees = st.sidebar.number_input("Annual Management Fees ($)", value=3000.0)

# Sell Scenario Inputs
st.sidebar.subheader("Selling and Investing")
sale_price = st.sidebar.number_input("Expected Sale Price ($)", value=1000000.0, step=10000.0)
mortgage_remaining = st.sidebar.number_input("Mortgage Remaining at Sale ($)", value=700000.0, step=10000.0)
capital_gains_tax = st.sidebar.slider("Capital Gains Tax (%)", 0.0, 50.0, 0.0) / 100
realtor_fees = st.sidebar.slider("Realtor Fees (%)", 0.0, 10.0, 5.0) / 100

rate_of_return = st.sidebar.slider("Annual Investment Return (%)", 0.0, 12.0, 6.0) / 100

# Calculate net proceeds from sale
capital_gains = max(sale_price - initial_home_value, 0) * capital_gains_tax
net_proceeds = sale_price - realtor_fees * sale_price - mortgage_remaining - capital_gains

# Full amortization schedule over loan term
full_amortization_balance = []
full_interest_paid = []
balance = mortgage_balance

for year in range(mortgage_term_years):
    interest_paid = 0
    for _ in range(12):
        interest = balance * (mortgage_rate / 12)
        principal = monthly_mortgage_payment - interest
        balance -= principal
        interest_paid += interest
    full_amortization_balance.append(balance)
    full_interest_paid.append(interest_paid)

# Limit to projection window
years_range = np.arange(1, years + 1)
remaining_balance = full_amortization_balance[:years]
interest_paid_yearly = full_interest_paid[:years]

# Projection Calculations
rent_income = np.array([(monthly_rent * 12) * ((1 + rent_increase) ** (i - 1)) for i in years_range])
tax_paid = rent_income * income_tax_rate
house_value = np.array([initial_home_value * ((1 + home_growth) ** i) for i in years_range])
equity = house_value - np.array(remaining_balance)

fixed_costs = np.array([
    property_tax + maintenance + insurance + management_fees + interest_paid_yearly[i]
    for i in range(years)
]) + tax_paid

net_rent = rent_income - fixed_costs
opportunity_loss = np.array([min(0, net_rent[i]) * ((1 + opportunity_cost_rate) ** (i + 1)) for i in range(years)])
cum_rent = np.cumsum(net_rent)
adjusted_equity = equity - np.cumsum(opportunity_loss)
rent_scenario_value = cum_rent + adjusted_equity

investment_value = np.zeros(years)
investment_value[0] = net_proceeds
for i in range(1, years):
    additional_cash = max(0, net_rent[i - 1])
    investment_value[i] = (investment_value[i - 1] + additional_cash) * (1 + rate_of_return)

discount_factors = np.array([(1 + discount_rate) ** i for i in years_range])
adjusted_rent_value = rent_scenario_value / discount_factors
adjusted_investment_value = investment_value / discount_factors

# Create dataframe
df = pd.DataFrame({
    "Year": years_range,
    "Rent + Equity": adjusted_rent_value,
    "Invested Proceeds": adjusted_investment_value
})

# Plot
df.set_index("Year", inplace=True)
st.subheader("Projected ROI Over Time")
fig, ax = plt.subplots()
df.plot(ax=ax)
ax.set_xlabel("Year")
ax.set_ylabel("Value ($)")
ax.set_title("Rent vs Sell ROI Comparison")
st.pyplot(fig)

# Crossover Point
crossover = np.where(adjusted_investment_value > adjusted_rent_value)[0]
if len(crossover) > 0:
    st.success(f"💡 Investment surpasses rent strategy in year {crossover[0] + 1}.")
else:
    st.info("💡 Rent strategy remains superior over the selected timeframe.")

with st.expander("📊 Show Yearly Data Table"):
    st.dataframe(df.style.format("{:.0f}"))

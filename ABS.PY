import numpy as np
import numpy_financial as npf  # Install via: pip install numpy_financial
import matplotlib.pyplot as plt

# Set random seed for reproducibility
np.random.seed(42)

# ---------------------------
# 1. SET UP LOAN PORTFOLIO
# ---------------------------
num_loans = 100
term = 36  # months

# Randomly generate loan parameters
loan_amounts = np.random.uniform(10_000, 50_000, num_loans)
interest_rates = np.random.uniform(0.05, 0.15, num_loans)  # annual rates

# Monthly payment calculation using the annuity formula
def monthly_payment(principal, annual_rate, months):
    r = annual_rate / 12
    return principal * r / (1 - (1 + r) ** (-months))

# Compute scheduled monthly payments for each loan
payments = np.array([monthly_payment(loan_amounts[i], interest_rates[i], term)
                     for i in range(num_loans)])

# ---------------------------
# 2. SIMULATE LOAN CASH FLOWS
# ---------------------------
# For simplicity, simulate standard amortization without prepayment/default.
# Each loan’s cash flow is computed month-by-month.
loan_cashflows = np.zeros((num_loans, term))
for i in range(num_loans):
    balance = loan_amounts[i]
    r = interest_rates[i] / 12
    pay = payments[i]
    for m in range(term):
        # Calculate interest and principal components
        interest_payment = balance * r
        principal_payment = pay - interest_payment
        # Adjust the final payment if needed
        if balance < principal_payment:
            principal_payment = balance
            pay = principal_payment + interest_payment
        loan_cashflows[i, m] = pay
        balance -= principal_payment

# Aggregate monthly cash flows from all loans
portfolio_cashflow = loan_cashflows.sum(axis=0)
total_cash = portfolio_cashflow.sum()         # Total cash received (principal + interest)
total_principal = loan_amounts.sum()            # Total initial principal

# ---------------------------
# 3. STRUCTURE TRANCHES
# ---------------------------
# Define tranche percentages by principal
senior_pct, mezzanine_pct, equity_pct = 0.70, 0.20, 0.10

# The initial investment for each tranche is its share of total principal.
senior_investment = total_principal * senior_pct
mezzanine_investment = total_principal * mezzanine_pct
equity_investment = total_principal * equity_pct

# Allocate total cash collected (which exceeds total principal because of interest)
senior_total_cash = total_cash * senior_pct
mezzanine_total_cash = total_cash * mezzanine_pct
equity_total_cash = total_cash * equity_pct

# For simplicity, assume cash flows are distributed evenly over the term.
senior_cf = np.full(term, senior_total_cash / term)
mezzanine_cf = np.full(term, mezzanine_total_cash / term)
equity_cf = np.full(term, equity_total_cash / term)

# ---------------------------
# 4. CALCULATE IRRs
# ---------------------------
def calculate_irr(cf_series, initial_investment):
    # The cash flow series starts with a negative outflow (the initial investment)
    irr_value = npf.irr([-initial_investment] + list(cf_series))
    return 0 if np.isnan(irr_value) else irr_value

irr_senior = calculate_irr(senior_cf, senior_investment)
irr_mezzanine = calculate_irr(mezzanine_cf, mezzanine_investment)
irr_equity = calculate_irr(equity_cf, equity_investment)

print(f"Total Principal: ${total_principal:,.2f}")
print(f"Total Cash Collected: ${total_cash:,.2f}\n")
print(f"Senior Investment: ${senior_investment:,.2f} | Senior Total Cash: ${senior_total_cash:,.2f} | IRR: {irr_senior:.2%}")
print(f"Mezzanine Investment: ${mezzanine_investment:,.2f} | Mezzanine Total Cash: ${mezzanine_total_cash:,.2f} | IRR: {irr_mezzanine:.2%}")
print(f"Equity Investment: ${equity_investment:,.2f} | Equity Total Cash: ${equity_total_cash:,.2f} | IRR: {irr_equity:.2%}")

# ---------------------------
# 5. PLOT PORTFOLIO CASH FLOW
# ---------------------------
plt.figure(figsize=(8, 4))
plt.plot(portfolio_cashflow, marker='o', linestyle='-', color='blue', label='Portfolio Cash Flow')
plt.xlabel("Month")
plt.ylabel("Cash Flow ($)")
plt.title("Monthly Portfolio Cash Flow")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

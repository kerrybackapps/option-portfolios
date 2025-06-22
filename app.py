import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Configure Streamlit page
st.set_page_config(
    page_title="Option Portfolios",
    layout="wide"
)

class Option(list):
    def add(self, security, quantity, strike=None):
        self.append(dict(security=security, quantity=quantity, strike=strike))

    def strikes(self):
        return [
            d["strike"] for d in self if d["security"] not in ["Underlying", "Cash"]
        ]

    def grid(self):
        strikes = self.strikes()
        maxstrike = 100 if len(strikes) == 0 else 1.5 * np.max(strikes)
        return np.linspace(0, maxstrike, 200)

    def value(self):
        grid = self.grid()
        value = np.zeros(len(grid))
        for x in self:
            if x["security"] == "Cash":
                value += x["quantity"]
            elif x["security"] == "Underlying":
                value += x["quantity"] * grid
            elif x["security"] == "Call":
                value += x["quantity"] * np.maximum(grid - x["strike"], 0)
            else:
                value += x["quantity"] * np.maximum(x["strike"] - grid, 0)
        return value

    def plot(self):
        df = pd.DataFrame(self.grid(), columns=["Underlying"])
        df["Portfolio"] = self.value()
        fig = px.line(df, x="Underlying", y="Portfolio")
        fig.layout.xaxis["title"] = "Underlying Price"
        fig.layout.yaxis["title"] = "Portfolio Value"
        fig.update_layout(
            xaxis_tickprefix="$", 
            xaxis_tickformat=",.0f",
            yaxis_tickprefix="$", 
            yaxis_tickformat=",.0f",
            template="plotly_white",
            height=500
        )
        return fig

# Sidebar controls
with st.sidebar:
    # Cash position
    cash_position = st.selectbox("Cash position:", ["None", "Long", "Short"])
    cash_amount = None
    if cash_position != "None":
        cash_amount = st.selectbox("Cash amount:", list(range(5, 105, 5)))
    
    # Underlying position
    underlying_position = st.selectbox("Underlying position:", ["None", "Long", "Short"])
    underlying_quantity = None
    if underlying_position != "None":
        underlying_quantity = st.selectbox("Underlying quantity:", list(range(1, 4)))
    
    st.markdown("---")
    st.markdown("**Options:**")
    
    # Option positions (4 slots)
    options = []
    for i in range(4):
        st.markdown(f"**Option {i+1}:**")
        option_type = st.selectbox(f"Type {i+1}:", ["None", "Call", "Put"], key=f"type_{i}")
        
        if option_type != "None":
            strike = st.selectbox(f"Strike {i+1}:", list(range(5, 205, 5)), key=f"strike_{i}")
            quantity = st.selectbox(f"Quantity {i+1}:", [-3, -2, -1, 1, 2, 3], key=f"qty_{i}")
            options.append((option_type, strike, quantity))
        else:
            options.append(None)

# Create portfolio
portfolio = Option()

# Add cash position
if cash_position == "Long" and cash_amount:
    portfolio.add(security="Cash", quantity=cash_amount)
elif cash_position == "Short" and cash_amount:
    portfolio.add(security="Cash", quantity=-cash_amount)

# Add underlying position
if underlying_position == "Long" and underlying_quantity:
    portfolio.add(security="Underlying", quantity=underlying_quantity)
elif underlying_position == "Short" and underlying_quantity:
    portfolio.add(security="Underlying", quantity=-underlying_quantity)

# Add options
for option in options:
    if option:
        option_type, strike, quantity = option
        portfolio.add(security=option_type, strike=strike, quantity=quantity)

# Display plot
if len(portfolio) > 0:
    fig = portfolio.plot()
    st.plotly_chart(fig, use_container_width=True)
else:
    # Show empty plot with grid
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[0, 100], y=[0, 0], mode='lines', line=dict(color='lightgray')))
    fig.update_layout(
        xaxis_title="Underlying Price",
        yaxis_title="Portfolio Value",
        xaxis_tickprefix="$",
        xaxis_tickformat=",.0f",
        yaxis_tickprefix="$", 
        yaxis_tickformat=",.0f",
        template="plotly_white",
        height=500,
        xaxis=dict(range=[0, 100]),
        yaxis=dict(range=[-50, 50])
    )
    st.plotly_chart(fig, use_container_width=True)
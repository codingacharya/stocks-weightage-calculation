import streamlit as st
import pandas as pd

# --- 1. Define Initial Data (Weights) ---
# NOTE: This is a sample list of high-weight Nifty-50 stocks for demonstration. 
# For a real-time application, this data should be loaded from a live API/database.
STOCK_WEIGHTS = {
    'HDFC Bank Ltd': 13.11,
    'Reliance Ind. Ltd': 8.31,
    'ICICI Bank Ltd': 9.00,
    'Infosys Ltd': 4.78,
    'Bharti Airtel Ltd': 4.65,
    'SBI': 2.79,
    'HUL': 2.13,
    'L&T Ltd': 3.82,
    'TCS Ltd': 2.85,
    'Axis Bank Ltd': 2.70
}

def calculate_nifty_impact(weights_df):
    """
    Calculates the impact of each stock on the Nifty-50 index.
    
    Formula: Impact (%) = (Weightage / 100) * Live % Change
    """
    # Ensure columns are numeric for calculation
    weights_df['Weightage (%)'] = pd.to_numeric(weights_df['Weightage (%)'], errors='coerce')
    weights_df['Live % Change'] = pd.to_numeric(weights_df['Live % Change'], errors='coerce')
    
    # Perform the core calculation
    weights_df['Impact (%)'] = (weights_df['Weightage (%)'] / 100) * weights_df['Live % Change']
    
    # Sort results by Impact, showing highest contributors first
    weights_df = weights_df.sort_values(by='Impact (%)', ascending=False)
    
    return weights_df.dropna(subset=['Impact (%)']) # Remove rows where calculation failed

# --- 2. Streamlit Application Layout ---
def main():
    st.set_page_config(
        page_title="Nifty-50 Stock Impact Calculator",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("📈 Nifty-50 Index Impact Calculator")
    st.markdown("""
        Determine how **individual stock movements** contribute to the **overall Nifty-50 index change** using the weighted average formula: 
        $$\\text{Impact (\\%)} = \\frac{\\text{Weightage (\\%)}}{100} \\times \\text{Live \\% Change}$$
    """)

    # --- 3. Prepare the DataFrame for display and calculation ---
    # Create the initial DataFrame
    data = pd.DataFrame(list(STOCK_WEIGHTS.items()), columns=['Stock', 'Weightage (%)'])
    data['Live % Change'] = 0.0  # Initialize Live % Change to 0.0

    st.header("Input Stock Movements")
    st.info("Edit the **Live % Change** column below for each stock. Use positive values for gains and negative values for losses.")
    
    # Use st.data_editor to allow users to modify the 'Live % Change' column
    edited_data = st.data_editor(
        data,
        column_config={
            "Weightage (%)": st.column_config.NumberColumn(
                "Weightage (%)",
                help="Stock's current weight in the Nifty-50 index",
                format="%.2f%%",
                disabled=True # Weights are fixed inputs
            ),
            "Live % Change": st.column_config.NumberColumn(
                "Live % Change",
                help="The stock's real-time percentage change from the previous close (e.g., 2.5 for a 2.5% gain).",
                format="%.2f"
            )
        },
        hide_index=True,
        num_rows="dynamic", # Allow adding new rows (though weights will be missing)
        key="data_editor"
    )

    if not edited_data.empty:
        # Calculate the impact using the edited data
        result_df = calculate_nifty_impact(edited_data.copy())

        # --- 4. Display Results ---
        st.header("Results and Contribution")
        
        # Display the results table
        st.dataframe(
            result_df,
            column_config={
                "Impact (%)": st.column_config.NumberColumn(
                    "Impact (%)",
                    help="Contribution to the overall Nifty-50 movement in percentage points (Pips).",
                    format="%.4f"
                )
            },
            hide_index=True
        )

        # --- 5. Summary Metrics ---
        total_impact = result_df['Impact (%)'].sum()
        
        # Logic for Summary Display
        if total_impact > 0:
            sentiment = "Uptrend (Bullish)"
        elif total_impact < 0:
            sentiment = "Downtrend (Bearish)"
        else:
            sentiment = "Flat"

        st.markdown("---")
        st.subheader("Total Index Impact")
        
        # The corrected st.metric usage: delta_color is 'normal'
        st.metric(
            label=f"Net Impact from {len(result_df)} Stocks (in % points)",
            value=f"{total_impact:.4f}%",
            delta=f"{total_impact:.4f}", # The delta value applies color based on sign
            delta_color='normal'
        )
        st.markdown(f"**Interpretation:** The net contribution from the listed stocks is **{total_impact:.4f} percentage points**. This suggests an overall **{sentiment}** bias from this major subset of the index.")

if __name__ == "__main__":
    main()
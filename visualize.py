import pandas as pd
import plotly.express as px

def main():
    # 1. Load the data
    # Assuming the CSV is in the same directory as this script
    df = pd.read_csv("categorized_budget.csv")
    
    # 2. Clean and Prep Data
    # We will visualize the 2026 budget. 
    # Plotly's treemap/sunburst cannot accept zero or negative values for sizing.
    target_year = '2026'
    df = df[df[target_year] > 0].copy()
    
    # Fill missing categories just in case
    df['Category'] = df['Category'].fillna('Uncategorized')
    
    # Create a dummy column to serve as the root of our hierarchy
    df['Root'] = 'Total 2026 Budget'

    print(f"Loaded {len(df)} active account lines for {target_year}.")

    # 3. Generate Treemap
    # path defines the hierarchy: Root -> Category -> Account Name
    fig_treemap = px.treemap(
        df,
        path=['Root', 'Category', 'Account Name'],
        values=target_year,
        title=f"City Budget {target_year} - Treemap View",
        color='Category',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    # Improve layout and text information
    fig_treemap.update_traces(
        textinfo="label+value+percent parent",
        hovertemplate="<b>%{label}</b><br>Budget: $%{value:,.0f}<br>Parent Contribution: %{percentParent:.1%}"
    )
    
    # 4. Generate Sunburst Chart
    fig_sunburst = px.sunburst(
        df,
        path=['Root', 'Category', 'Account Name'],
        values=target_year,
        title=f"City Budget {target_year} - Sunburst View",
        color='Category',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    fig_sunburst.update_traces(
        textinfo="label+percent parent",
        hovertemplate="<b>%{label}</b><br>Budget: $%{value:,.0f}<br>Parent Contribution: %{percentParent:.1%}"
    )

    # 5. Display the charts
    # This will open two tabs in your default web browser
    print("Opening Treemap in browser...")
    fig_treemap.show()
    
    print("Opening Sunburst in browser...")
    fig_sunburst.show()

if __name__ == "__main__":
    main()

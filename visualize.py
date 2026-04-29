import pandas as pd
import plotly.express as px

SITE_URL = "https://caldwell.pages.dev"
SITE_DESCRIPTION = "City of Caldwell budget visualizations"


def inject_og_tags(html: str, title: str, url: str) -> str:
    tags = (
        f'    <meta property="og:title" content="{title}" />\n'
        f'    <meta property="og:description" content="{SITE_DESCRIPTION}" />\n'
        f'    <meta property="og:url" content="{url}" />\n'
        f'    <meta property="og:type" content="website" />\n'
    )
    return html.replace("</head>", tags + "</head>")


def main():
    df = pd.read_csv("categorized_budget.csv")

    target_year = "2026"
    df = df[df[target_year] > 0].copy()
    df["Category"] = df["Category"].fillna("Uncategorized")
    df["Root"] = "Total 2026 Budget"

    print(f"Loaded {len(df)} active account lines for {target_year}.")

    fig_treemap = px.treemap(
        df,
        path=["Root", "Category", "Account Name"],
        values=target_year,
        title=f"City Budget {target_year} - Treemap View",
        color="Category",
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    fig_treemap.update_traces(
        textinfo="label+value+percent parent",
        hovertemplate="<b>%{label}</b><br>Budget: $%{value:,.0f}<br>Parent Contribution: %{percentParent:.1%}",
    )

    fig_sunburst = px.sunburst(
        df,
        path=["Root", "Category", "Account Name"],
        values=target_year,
        title=f"City Budget {target_year} - Sunburst View",
        color="Category",
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    fig_sunburst.update_traces(
        textinfo="label+percent parent",
        hovertemplate="<b>%{label}</b><br>Budget: $%{value:,.0f}<br>Parent Contribution: %{percentParent:.1%}",
    )

    charts = [
        (
            fig_treemap,
            "treemap_budget.html",
            f"City Budget {target_year} - Treemap View",
        ),
        (
            fig_sunburst,
            "sunburst_budget.html",
            f"City Budget {target_year} - Sunburst View",
        ),
    ]

    for fig, filename, title in charts:
        html = fig.to_html(full_html=True)
        html = inject_og_tags(html, title=title, url=f"{SITE_URL}/{filename}")
        output_path = f"docs/{filename}"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Written {output_path}")

    print("Opening Treemap in browser...")
    fig_treemap.show()

    print("Opening Sunburst in browser...")
    fig_sunburst.show()


if __name__ == "__main__":
    main()

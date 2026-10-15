import plotly.express as px


def build_category_chart(df):
    if df.empty:
        return None
    cat_data = df.groupby("category")["quantity"].sum().reset_index()
    fig = px.bar(
        cat_data,
        x="category",
        y="quantity",
        color="category",
        text="quantity",
        template="plotly_dark",
        labels={"quantity": "Units in Stock", "category": "Category"},
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    fig.update_layout(
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def build_risk_chart(df):
    if df.empty:
        return None
    status_data = df.groupby("status")["quantity"].sum().reset_index()
    fig = px.pie(
        status_data,
        names="status",
        values="quantity",
        hole=0.4,
        template="plotly_dark",
        color="status",
        color_discrete_map={
            "Safe": "#10b981",
            "Expiring Soon": "#f59e0b",
            "Expired": "#ef4444",
        },
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
    )
    return fig

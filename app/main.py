import pandas as pd
import streamlit as st

from api_client import (
    get_sales_summary,
    get_sales_by_product,
    get_sales_by_category,
    get_sales_by_date,
    get_pipeline_health,
    get_pipeline_runs,
)


st.set_page_config(
    page_title="RetailPulse",
    page_icon="📊",
    layout="wide",
)


st.title("RetailPulse")
st.subheader("Sales Intelligence Dashboard")


try:
    all_product_data = get_sales_by_product()
    all_category_data = get_sales_by_category()
    all_date_data = get_sales_by_date()
    pipeline_health = get_pipeline_health()

    product_names = [
        row["product_name"]
        for row in all_product_data
    ]

    category_names = [
        row["category_name"]
        for row in all_category_data
    ]

    all_date_values = pd.to_datetime(
        [str(row["date_key"]) for row in all_date_data],
        format="%Y%m%d",
    )

    min_date = all_date_values.min().date()
    max_date = all_date_values.max().date()

    st.subheader("Filters")

    filter_col1, filter_col2, filter_col3 = st.columns(3)

    selected_products = filter_col1.multiselect(
        "Product",
        options=product_names,
        default=product_names,
    )

    selected_categories = filter_col2.multiselect(
        "Category",
        options=category_names,
        default=category_names,
    )

    selected_dates = filter_col3.date_input(
        "Date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    if len(selected_dates) == 2:
        start_date, end_date = selected_dates

        selected_products_for_api = selected_products or None
        selected_categories_for_api = selected_categories or None

        sales_summary = get_sales_summary(
            str(start_date),
            str(end_date),
            selected_products_for_api,
            selected_categories_for_api,
        )

        product_data = get_sales_by_product(
            str(start_date),
            str(end_date),
            selected_products_for_api,
            selected_categories_for_api,
        )

        category_data = get_sales_by_category(
            str(start_date),
            str(end_date),
            selected_products_for_api,
            selected_categories_for_api,
        )

        date_data = get_sales_by_date(
            str(start_date),
            str(end_date),
            selected_products_for_api,
            selected_categories_for_api,
        )
    else:
        sales_summary = get_sales_summary(
            products=selected_products or None,
            categories=selected_categories or None,
        )

        product_data = get_sales_by_product(
            products=selected_products or None,
            categories=selected_categories or None,
        )

        category_data = get_sales_by_category(
            products=selected_products or None,
            categories=selected_categories or None,
        )

        date_data = get_sales_by_date(
            products=selected_products or None,
            categories=selected_categories or None,
        )

    total_sales = sales_summary["total_sales"]
    total_orders = sales_summary["total_orders"]
    total_quantity = sales_summary["total_quantity"]

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Sales",
        f"₹{float(total_sales):,.2f}",
    )

    col2.metric(
        "Total Orders",
        f"{total_orders:,}",
    )

    col3.metric(
        "Total Quantity",
        f"{total_quantity:,}",
    )

    st.divider()

    st.subheader("Sales by Product")

    if product_data:
        product_chart = pd.DataFrame(product_data)

        product_chart["total_sales"] = product_chart[
            "total_sales"
        ].astype(float)

        product_chart = product_chart.set_index(
            "product_name"
        )

        st.bar_chart(
            product_chart["total_sales"],
            horizontal=True,
        )
    else:
        st.info("No product sales found for the selected filters.")

    st.subheader("Sales by Category")

    if category_data:
        category_chart = pd.DataFrame(category_data)

        category_chart["total_sales"] = category_chart[
            "total_sales"
        ].astype(float)

        category_chart = category_chart.set_index(
            "category_name"
        )

        st.bar_chart(
            category_chart["total_sales"],
            horizontal=True,
        )
    else:
        st.info("No category sales found for the selected filters.")

    st.subheader("Sales Trend")

    if date_data:
        sales_trend = pd.DataFrame(
            {
                "date": pd.to_datetime(
                    [str(row["date_key"]) for row in date_data],
                    format="%Y%m%d",
                ),
                "sales": [
                    float(row["total_sales"])
                    for row in date_data
                ],
            }
        )

        sales_trend["date"] = sales_trend["date"].dt.strftime(
            "%d %b"
        )

        st.line_chart(
            sales_trend,
            x="date",
            y="sales",
        )
    else:
        st.info("No sales data available for the selected filters.")

    st.divider()

    st.subheader("Pipeline Health")

    pipeline_col1, pipeline_col2, pipeline_col3, pipeline_col4 = st.columns(4)

    pipeline_col1.metric(
        "Total Runs",
        f"{pipeline_health['total_runs']:,}",
    )

    pipeline_col2.metric(
        "Successful",
        f"{pipeline_health['successful_runs']:,}",
    )

    pipeline_col3.metric(
        "Failed",
        f"{pipeline_health['failed_runs']:,}",
    )

    pipeline_col4.metric(
        "Skipped",
        f"{pipeline_health['skipped_runs']:,}",
    )

    st.subheader("Recent Pipeline Runs")

    pipeline_runs = get_pipeline_runs(limit=10)

    pipeline_runs_df = pd.DataFrame(pipeline_runs)

    if not pipeline_runs_df.empty:
        pipeline_runs_df["started_at"] = pd.to_datetime(
            pipeline_runs_df["started_at"]
        ).dt.strftime("%d %b %Y, %I:%M %p")

        pipeline_runs_df["completed_at"] = pd.to_datetime(
            pipeline_runs_df["completed_at"]
        ).dt.strftime("%d %b %Y, %I:%M %p")

        display_columns = [
            "run_id",
            "pipeline_name",
            "source_file",
            "status",
            "started_at",
            "completed_at",
            "records_received",
            "records_accepted",
            "records_rejected",
            "records_processed",
        ]

        st.dataframe(
            pipeline_runs_df[display_columns],
            width="stretch",
            hide_index=True,
        )
    else:
        st.info("No pipeline runs found.")

except Exception as exc:
    st.exception(exc)
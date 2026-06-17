import streamlit as st
import pandas as pd

from services.incident_service import (
    get_user_incidents
)

st.title("📊 HELP Dashboard")

try:

    user_id = st.session_state.get("user_id")

    if not user_id:
        st.warning(
            "Please login first."
        )
        st.stop()

    result = get_user_incidents(
        user_id
    )

    incidents = result.data

    if not incidents:

        st.info(
            "No incidents found."
        )

    else:

        df = pd.DataFrame(
            incidents
        )

        st.subheader(
            "Overview"
        )

        total_incidents = len(df)

        critical_count = len(
            df[
                df["severity"] == "CRITICAL"
            ]
        )

        high_count = len(
            df[
                df["severity"] == "HIGH"
            ]
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Total Incidents",
                total_incidents
            )

        with col2:
            st.metric(
                "Critical",
                critical_count
            )

        with col3:
            st.metric(
                "High",
                high_count
            )

        st.subheader(
            "Severity Distribution"
        )

        if "severity" in df.columns:

            severity_counts = (
                df["severity"]
                .value_counts()
            )

            st.bar_chart(
                severity_counts
            )

        st.subheader(
            "Recent Incidents"
        )

        display_columns = [
            col for col in [
                "incident_type",
                "severity",
                "category",
                "status",
                "location_name",
                "created_at"
            ]
            if col in df.columns
        ]

        st.dataframe(
            df[display_columns],
            use_container_width=True
        )

except Exception as e:

    st.error(
        f"Dashboard Error: {e}"
    )
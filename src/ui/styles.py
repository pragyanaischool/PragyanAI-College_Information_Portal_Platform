"""
src/ui/styles.py

Custom UI styling tokens, CSS injectors, and metric card styling for Streamlit.
"""

import streamlit as st


def inject_custom_css():
    """Injects responsive enterprise CSS variables and card styles."""
    st.markdown(
        """
        <style>
        /* Base Container Customization */
        .main .block-container {
            padding-top: 1.8rem;
            padding-bottom: 2.5rem;
            padding-left: 2.5rem;
            padding-right: 2.5rem;
            max-width: 1350px;
        }

        /* Metric Cards */
        .metric-card {
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 1.25rem 1.5rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.04), 0 2px 4px -1px rgba(0, 0, 0, 0.02);
            transition: all 0.2s ease-in-out;
            margin-bottom: 1rem;
        }
        .metric-card:hover {
            border-color: #3b82f6;
            box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.08);
            transform: translateY(-2px);
        }
        .metric-card-title {
            font-size: 0.82rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #64748b;
            margin-bottom: 0.25rem;
        }
        .metric-card-value {
            font-size: 1.75rem;
            font-weight: 700;
            color: #0f172a;
            margin-bottom: 0.25rem;
        }
        .metric-card-delta {
            font-size: 0.8rem;
            font-weight: 600;
        }
        .delta-positive { color: #10b981; }
        .delta-neutral { color: #64748b; }

        /* Document Citation & Media Pills */
        .media-pill {
            display: inline-flex;
            align-items: center;
            background-color: #eff6ff;
            border: 1px solid #bfdbfe;
            color: #1d4ed8;
            padding: 0.35rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.8rem;
            font-weight: 600;
            margin-right: 0.5rem;
            margin-bottom: 0.5rem;
            text-decoration: none;
        }
        .media-pill:hover {
            background-color: #dbeafe;
            color: #1e40af;
        }

        /* Lead Priority Badges */
        .badge-urgent {
            background-color: #fee2e2;
            color: #b91c1c;
            padding: 0.2rem 0.6rem;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 700;
        }
        .badge-medium {
            background-color: #fef3c7;
            color: #b45309;
            padding: 0.2rem 0.6rem;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 700;
        }
        .badge-normal {
            background-color: #f1f5f9;
            color: #475569;
            padding: 0.2rem 0.6rem;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 700;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(title: str, value: str, delta: str = "", positive: bool = True):
    """Renders a custom HTML metric card."""
    delta_class = "delta-positive" if positive else "delta-neutral"
    delta_html = f'<div class="metric-card-delta {delta_class}">{delta}</div>' if delta else ""
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-card-title">{title}</div>
            <div class="metric-card-value">{value}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

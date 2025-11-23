import streamlit as st

def apply_custom_css():
    """Apply custom CSS styling to improve UI"""
    st.markdown("""
        <style>
        /* Main container styling */
        .main {
            padding: 0rem 1rem;
        }
        
        /* Metric cards styling */
        [data-testid="stMetricValue"] {
            font-size: 1.8rem;
            font-weight: 600;
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 10px 20px;
            border-radius: 8px 8px 0 0;
        }
        
        /* Alert box styling */
        .alert-box {
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            border-left: 4px solid;
        }
        
        .alert-success {
            background-color: #d4edda;
            border-color: #28a745;
            color: #155724;
        }
        
        .alert-warning {
            background-color: #fff3cd;
            border-color: #ffc107;
            color: #856404;
        }
        
        .alert-danger {
            background-color: #f8d7da;
            border-color: #dc3545;
            color: #721c24;
        }
        
        /* Price change styling */
        .price-up {
            color: #28a745;
            font-weight: 600;
        }
        
        .price-down {
            color: #dc3545;
            font-weight: 600;
        }
        
        /* Card styling */
        .info-card {
            background-color: #f8f9fa;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 1rem 0;
        }
        
        /* Header styling */
        h1 {
            color: #1f77b4;
            font-weight: 700;
        }
        
        h2 {
            color: #2c3e50;
            font-weight: 600;
        }
        
        h3 {
            color: #34495e;
        }
        </style>
    """, unsafe_allow_html=True)

def display_price_change(value: float, label: str = "") -> str:
    """Display price change with color coding"""
    color = "price-up" if value >= 0 else "price-down"
    arrow = "▲" if value >= 0 else "▼"
    return f'<span class="{color}">{arrow} {abs(value):.2f}%</span> {label}'

def create_alert_box(message: str, alert_type: str = "info"):
    """Create styled alert box"""
    st.markdown(f'<div class="alert-box alert-{alert_type}">{message}</div>', unsafe_allow_html=True)

def display_stat_card(title: str, value: str, description: str = ""):
    """Display a styled statistics card"""
    st.markdown(f"""
        <div class="info-card">
            <h4 style="margin: 0; color: #7f8c8d;">{title}</h4>
            <h2 style="margin: 0.5rem 0; color: #2c3e50;">{value}</h2>
            <p style="margin: 0; color: #95a5a6; font-size: 0.9rem;">{description}</p>
        </div>
    """, unsafe_allow_html=True)

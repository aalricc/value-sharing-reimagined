import streamlit as st

class UIManager:
    """Manages all UI styling and CSS for the FairShare app"""
    
    def __init__(self):
        pass
    
    def apply_global_styles(self):
        """Apply global CSS styles to the app"""
        st.markdown(self._get_global_css(), unsafe_allow_html=True)
        st.set_page_config(page_title="FairShare – Creator Rewards", layout="wide")
    
    def _get_global_css(self):
        """Get all global CSS styles"""
        return """
        <style>
        /* Smooth tab transitions */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background: linear-gradient(90deg, #1a1a1a, #2d2d2d);
            border-radius: 12px;
            padding: 8px;
            margin-bottom: 20px;
        }

        .stTabs [data-baseweb="tab"] {
            background: transparent;
            border-radius: 8px;
            color: #ffffff;
            padding: 12px 24px;
            font-weight: 500;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            border: 2px solid transparent;
            position: relative;
            overflow: hidden;
        }

        .stTabs [data-baseweb="tab"]:hover {
            background: linear-gradient(135deg, rgba(255, 0, 80, 0.1), rgba(0, 242, 234, 0.1));
            border-color: rgba(255, 0, 80, 0.3);
            transform: translateY(-2px);
            box-shadow: 0 4px 20px rgba(255, 0, 80, 0.2);
        }

        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background: transparent;
            color: #00F2EA;
            border: 2px solid #00F2EA;
            box-shadow: none;
            transform: none;
        }

        /* Smooth content transitions */
        .stTabs [data-baseweb="tab-panel"] {
            animation: fadeInUp 0.5s ease-out;
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        /* Hover effects for interactive elements */
        .stButton > button {
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            border-radius: 8px;
        }

        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(255, 0, 80, 0.3);
        }

        /* Smooth expander transitions */
        .streamlit-expanderHeader {
            transition: all 0.3s ease;
            border-radius: 8px;
        }

        .streamlit-expanderHeader:hover {
            background: linear-gradient(135deg, rgba(255, 0, 80, 0.1), rgba(0, 242, 234, 0.1));
            transform: translateX(5px);
        }

        /* Custom scrollbar for better aesthetics */
        ::-webkit-scrollbar {
            width: 8px;
        }

        ::-webkit-scrollbar-track {
            background: #1a1a1a;
            border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #FF0050, #00F2EA);
            border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, #E6004C, #00D4CC);
        }
        </style>
        """

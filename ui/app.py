import streamlit as st
import requests
import pandas as pd

# Must be the first Streamlit command
st.set_page_config(
    page_title="Optylize Market Insights",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Premium Custom CSS
st.markdown("""
<style>
    /* Global styles for dark mode and vibrant accents */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #58a6ff !important;
        font-family: 'Inter', sans-serif;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #1f6feb, #3fb950);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(31, 111, 235, 0.4);
        border: none;
        color: white;
    }
    
    /* Input box */
    .stTextInput>div>div>input {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: white;
        border-radius: 8px;
    }
    
    /* Glassmorphic cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-2px);
        background: rgba(255, 255, 255, 0.05);
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #3fb950;
    }
</style>
""", unsafe_allow_html=True)

st.title("🔮 Optylize Market Insights")
st.markdown("Enter a market research query below. Our ASI-powered agentic workflow will crawl the web, process data in real-time, and generate a structured report.")

query = st.text_input("Research Query", placeholder="e.g. AI adoption trends and ASI workflows in the global logistics industry")

if st.button("Generate Insights ✨"):
    if not query:
        st.warning("Please enter a query first.")
    else:
        with st.spinner("Agents are researching... this usually takes 15-30 seconds."):
            try:
                response = requests.post(
                    "http://localhost:8000/api/v1/research/",
                    json={"query": query},
                    timeout=90
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    st.success("Research Complete!")
                    st.header(data.get("title", "Market Report"))
                    st.markdown(f"*{data.get('executive_summary', '')}*")
                    
                    # Display Quantitative Data
                    st.subheader("📊 Quantitative Metrics")
                    metrics = data.get("quantitative_data", [])
                    if metrics:
                        cols = st.columns(min(len(metrics), 3))
                        for i, m in enumerate(metrics):
                            with cols[i % len(cols)]:
                                st.markdown(f"""
                                <div class="glass-card">
                                    <h4 style="margin-top:0; color: #8b949e !important;">{m.get('metric_name', '')}</h4>
                                    <div class="metric-value">{m.get('value', '')}</div>
                                    <p style="font-size: 0.9rem; margin-top: 0.5rem;">{m.get('context', '')}</p>
                                    <a href="{m.get('source', '#')}" target="_blank" style="font-size: 0.8rem; color: #58a6ff;">Source</a>
                                </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.info("No quantitative data found.")
                        
                    # Display Qualitative Trends
                    st.subheader("📈 Qualitative Trends")
                    trends = data.get("key_trends", [])
                    for t in trends:
                        st.markdown(f"""
                        <div class="glass-card">
                            <h3 style="margin-top:0;">{t.get('trend_name', '')} <span style="font-size: 0.9rem; background: rgba(88, 166, 255, 0.2); padding: 0.2rem 0.5rem; border-radius: 12px; vertical-align: middle; color: white;">{t.get('adoption_level', '')}</span></h3>
                            <p>{t.get('description', '')}</p>
                            <strong>ASI Relevance:</strong> {t.get('asi_relevance', '')}
                        </div>
                        """, unsafe_allow_html=True)
                        
                    # Display Strategic Recommendations
                    st.subheader("🎯 Strategic Recommendations")
                    recs = data.get("strategic_recommendations", [])
                    for i, r in enumerate(recs):
                        st.markdown(f"- {r}")
                        
                else:
                    st.error(f"API Error: {response.text}")
            except Exception as e:
                st.error(f"Failed to connect to backend: {e}")

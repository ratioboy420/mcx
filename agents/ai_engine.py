import os
from groq import Groq

def run_real_multi_agent_pipeline(pair_symbol, spread_val, z_score, rsi):
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        import streamlit as st
        groq_key = st.session_state.get("groq_key", "")
        
    if not groq_key:
        raise ValueError("Groq API Key missing! Please enter it in the sidebar.")
        
    client = Groq(api_key=groq_key)
    
    # Agent 1: Researcher
    r1_prompt = f"Agent 1 (Researcher): Analyze macro sentiment for MCX spread pair {pair_symbol}."
    res1 = client.chat.completions.create(model="llama3-8b-8192", messages=[{"role": "user", "content": r1_prompt}], max_tokens=150)
    
    # Agent 2: Technical Analyst
    r2_prompt = f"Agent 2 (Technical Analyst): Evaluate Z-Score {z_score} and RSI {rsi} for spread {spread_val}."
    res2 = client.chat.completions.create(model="llama3-8b-8192", messages=[{"role": "user", "content": r2_prompt}], max_tokens=150)
    
    # Agent 3: Expert Advisor
    r3_prompt = f"Agent 3 (Expert Advisor): Give final execution verdict ('LIVE' or 'pending') based on Research & Tech reports."
    res3 = client.chat.completions.create(model="llama3-8b-8192", messages=[{"role": "user", "content": r3_prompt}], max_tokens=150)
    
    ans3_text = res3.choices[0].message.content
    verdict = "LIVE" if "live" in ans3_text.lower() else "pending"
    
    return {
        "Agent_1": res1.choices[0].message.content,
        "Agent_2": res2.choices[0].message.content,
        "Agent_3_Verdict": verdict,
        "Strategy_Note": ans3_text
    }

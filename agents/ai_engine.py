import os
from groq import Groq

class RealQuantMultiAgentDesk:
    def __init__(self):
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            import streamlit as st
            groq_api_key = st.secrets["api_credentials"]["groq_api_key"]
            
        self.client = Groq(api_key=groq_api_key)

    def agent_1_researcher(self, pair_symbol):
        """Agent 1: Real macro & news sentiment analysis."""
        prompt = f"Agent 1 (Researcher): Analyze real-time macro sentiment and news flow for MCX commodity spread pair {pair_symbol}. Keep it sharp and factual."
        res = self.client.chat.completions.create(
            model="llama3-8b-8192", 
            messages=[{"role": "user", "content": prompt}], 
            max_tokens=150
        )
        return res.choices[0].message.content

    def agent_2_technical_analyst(self, pair_symbol, current_spread, z_score, rsi):
        """Agent 2: Real mathematical spread logic, Z-Score, and RSI evaluation."""
        prompt = f"Agent 2 (Technical Analyst): Evaluate real math metrics for {pair_symbol}. Spread: {current_spread}, Z-Score: {z_score}, RSI: {rsi}."
        res = self.client.chat.completions.create(
            model="llama3-8b-8192", 
            messages=[{"role": "user", "content": prompt}], 
            max_tokens=150
        )
        return res.choices[0].message.content

    def agent_3_expert_advisor(self, research_report, technical_report):
        """Agent 3: Real synthesis and final execution decision ('LIVE' or 'pending')."""
        prompt = f"""
        Agent 3 (Expert Advisor): Make final execution decision based on inputs.
        Research Report: {research_report}
        Technical Report: {technical_report}
        Strictly output 'LIVE' or 'pending' at the beginning, followed by precise execution rationale.
        """
        res = self.client.chat.completions.create(
            model="llama3-8b-8192", 
            messages=[{"role": "user", "content": prompt}], 
            max_tokens=200
        )
        return res.choices[0].message.content

def run_real_multi_agent_pipeline(pair_symbol, spread_val, z_score, rsi):
    engine = RealQuantMultiAgentDesk()
    r1 = engine.agent_1_researcher(pair_symbol)
    r2 = engine.agent_2_technical_analyst(pair_symbol, spread_val, z_score, rsi)
    r3 = engine.agent_3_expert_advisor(r1, r2)
    
    verdict = "LIVE" if "live" in r3.lower() else "pending"
    return {
        "Agent_1": r1,
        "Agent_2": r2,
        "Agent_3_Verdict": verdict,
        "Strategy_Note": r3
    }

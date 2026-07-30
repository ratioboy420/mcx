import os
from groq import Groq

# Initialize Groq Client (Ensure GROQ_API_KEY is in your environment variables or Streamlit secrets)
# client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def get_groq_response(client, system_prompt, user_prompt, model="llama3-70b-8192"):
    """Base function to call Groq LPU for blazing fast inference."""
    try:
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model=model,
            temperature=0.2, # Low temperature for logical, analytical answers
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"AI Error: {e}"

def macro_agent(client, news_data, fed_rates, dollar_index):
    """Agent 1: Macro & Fundamental Analysis"""
    sys_prompt = "You are an elite MCX Commodities Macro Analyst. Analyze global news, Fed rates, and the Dollar Index to determine the overall sentiment (Bullish, Bearish, or Neutral) for Gold and Silver. Keep it under 3 bullet points."
    
    user_prompt = f"Data today: News: {news_data} | Fed Rates: {fed_rates} | DXY: {dollar_index}. What is the macro view?"
    return get_groq_response(client, sys_prompt, user_prompt)

def quant_agent(client, pair_name, z_score, rsi, dte, oi_delta):
    """Agent 2: Technical & Quantitative Analysis"""
    sys_prompt = "You are a highly mathematical MCX Quant Trader. You strictly follow rules: Reject extreme Z-scores (<-1.7), reject RSI < 40, prioritize DTE between 49-56, and demand positive OI Delta. Respond with 'TRADE APPROVED' or 'TRADE REJECTED' followed by a 1-sentence technical reason."
    
    user_prompt = f"Evaluating {pair_name}: Z-Score: {z_score}, RSI: {rsi}, DTE: {dte}, OI Delta: {oi_delta}%. Should we take this trade?"
    return get_groq_response(client, sys_prompt, user_prompt)

def risk_agent(client, entry_price, target, stop_loss, account_balance):
    """Agent 3: Risk Management & Position Sizing"""
    sys_prompt = "You are a strict Risk Manager. Calculate the Risk/Reward ratio. If risk is greater than reward, or if the stop loss risks more than 2% of the account balance, reject the trade. Suggest the optimal lot size."
    
    user_prompt = f"Account: ₹{account_balance}. Trade Entry: {entry_price}, Target: {target}, SL: {stop_loss}. Analyze risk."
    return get_groq_response(client, sys_prompt, user_prompt)

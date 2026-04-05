import os
import requests
from dotenv import load_dotenv

load_dotenv()

def send_telegram_summary(chat_id: str, summary_data: dict, app_url: str = "") -> bool:
    """
    Sends a formatted financial summary to a specific Telegram Chat ID.
    Requires TELEGRAM_BOT_TOKEN in the environment.
    If chat_id is empty, it falls back to TELEGRAM_CHAT_ID from the environment.
    """
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN is not set in the environment.")

    # Fallback to ENV chat_id if not provided by the UI
    final_chat_id = chat_id.strip() if chat_id else os.getenv("TELEGRAM_CHAT_ID")
    if not final_chat_id:
        raise ValueError("No Target Chat ID provided and TELEGRAM_CHAT_ID is missing from .env")

    # Format the message
    commitments = summary_data.get("commitments", [])
    snapshot = summary_data.get("financial_snapshot", {})
    
    text = "🛡️ *Armor Financial Intelligence*\n\n"
    text += f"*Risk Level*: {summary_data.get('risk_label', 'Unknown')}\n"
    text += f"_{summary_data.get('risk_reasoning', 'No reasoning provided')}_\n\n"
    
    if commitments:
        text += "📌 *Commitments Made:*\n"
        for c in commitments:
            text += f"• *{c.get('speaker', 'Unknown')}*: {c.get('commitment', '')}\n"
        text += "\n"
        
    amounts = snapshot.get("amounts", [])
    if amounts:
        text += "💰 *Amounts Detected:*\n"
        for a in amounts:
            text += f"• {a}\n"
        text += "\n"
        
    text += "This is an automated record from your recent conversation."
    
    if app_url:
        text += f"\n\n[View Full Report in Vault]({app_url})"

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": final_chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    
    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()
    return True

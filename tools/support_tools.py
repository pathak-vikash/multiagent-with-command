from datetime import datetime
from typing import Dict, Any, Literal
from langchain_core.tools import tool

@tool
def create_support_ticket(issue: str, priority: Literal["high", "medium", "low"]) -> str:
    try:
        ticket_id = f"SUP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        return f"Support ticket created for {issue} with priority {priority}. Ticket ID: {ticket_id}"
    except Exception as e:
        return f"Failed to create support ticket: {str(e)}"

@tool
def check_warranty_status(customer_id: str) -> str:
    try:
        warranty_status = "Active"
        expiry_date = "2025-12-31"
        return f"Warranty status for customer {customer_id}: {warranty_status}, expires: {expiry_date}"
    except Exception as e:
        return f"Failed to check warranty status: {str(e)}"

@tool
def escalate_ticket(ticket_id: str, reason: str) -> str:
    try:
        return f"Ticket {ticket_id} escalated due to: {reason}"
    except Exception as e:
        return f"Failed to escalate ticket: {str(e)}"

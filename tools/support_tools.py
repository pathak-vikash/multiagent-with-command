from datetime import datetime
from typing import Dict, Any, Literal
from langchain_core.tools import tool

@tool
def create_support_ticket(issue: str, priority: Literal["high", "medium", "low"]) -> str:
    """
    Create a new support ticket for customer service issues.
    
    This tool creates a support ticket with a unique identifier and assigns the specified
    priority level. It's used to track and manage customer service requests.
    
    Args:
        issue: Description of the problem or issue that needs support
        priority: Priority level of the ticket - must be "high", "medium", or "low"
        
    Returns:
        str: Confirmation message with ticket ID and details
    """
    try:
        ticket_id = f"SUP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        return f"Support ticket created for {issue} with priority {priority}. Ticket ID: {ticket_id}"
    except Exception as e:
        return f"Failed to create support ticket: {str(e)}"

@tool
def check_warranty_status(customer_id: str) -> str:
    """
    Check the warranty status for a specific customer.
    
    This tool retrieves warranty information including status and expiration date
    for the specified customer ID.
    
    Args:
        customer_id: Unique identifier for the customer
        
    Returns:
        str: Warranty status information including status and expiration date
    """
    try:
        warranty_status = "Active"
        expiry_date = "2025-12-31"
        return f"Warranty status for customer {customer_id}: {warranty_status}, expires: {expiry_date}"
    except Exception as e:
        return f"Failed to check warranty status: {str(e)}"

@tool
def escalate_ticket(ticket_id: str, reason: str) -> str:
    """
    Escalate a support ticket to a higher priority level.
    
    This tool is used when a support ticket needs to be escalated due to urgency,
    complexity, or other reasons that require immediate attention.
    
    Args:
        ticket_id: The unique identifier of the ticket to escalate
        reason: Explanation of why the ticket needs to be escalated
        
    Returns:
        str: Confirmation message indicating the ticket has been escalated
    """
    try:
        return f"Ticket {ticket_id} escalated due to: {reason}"
    except Exception as e:
        return f"Failed to escalate ticket: {str(e)}"

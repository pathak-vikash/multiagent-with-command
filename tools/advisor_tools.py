from datetime import datetime
from typing import Dict, Any, Literal
from langchain_core.tools import tool

@tool
def get_service_info(service: str) -> str:
    """
    Get detailed information about a specific service.
    
    This tool provides comprehensive information about service offerings including
    duration, frequency, and price ranges. It helps customers understand what to expect
    from each service type.
    
    Args:
        service: Name of the service to get information about (e.g., "lawn care", "house cleaning", "pest control", "landscaping")
        
    Returns:
        str: Detailed service information including duration, frequency, and pricing
    """
    try:
        service_info = {
            "lawn care": "Professional lawn maintenance including mowing, edging, and fertilization. Duration: 1-2 hours, Frequency: Weekly or bi-weekly, Price Range: $100-200 per visit",
            "house cleaning": "Comprehensive residential cleaning services. Duration: 2-4 hours, Frequency: One-time or recurring, Price Range: $150-300 per visit",
            "pest control": "Pest elimination and prevention services. Duration: 1-3 hours, Frequency: As needed or quarterly, Price Range: $200-400 per treatment",
            "landscaping": "Landscape design, installation, and maintenance. Duration: Varies by project, Frequency: One-time or ongoing, Price Range: $500-5000+ per project"
        }
        
        info = service_info.get(service.lower(), "Service information not available. Contact us for details.")
        return f"Information about {service}: {info}"
    except Exception as e:
        return f"Failed to get service info: {str(e)}"

@tool
def get_business_hours() -> str:
    """
    Get the current business operating hours.
    
    This tool provides information about when the business is open and available
    for appointments, consultations, and customer service.
    
    Returns:
        str: Business hours for each day of the week
    """
    try:
        business_hours = "Monday-Friday: 8:00 AM - 6:00 PM, Saturday: 9:00 AM - 4:00 PM, Sunday: Closed"
        return f"Business hours: {business_hours}"
    except Exception as e:
        return f"Failed to get business hours: {str(e)}"

@tool
def get_contact_info() -> str:
    """
    Get the company's contact information.
    
    This tool provides all available contact methods including phone, email,
    and physical address for customer inquiries and support.
    
    Returns:
        str: Complete contact information including phone, email, and address
    """
    try:
        contact_info = "Phone: (555) 123-4567, Email: info@example.com, Address: 123 Business St, City, State 12345"
        return f"Contact us at: {contact_info}"
    except Exception as e:
        return f"Failed to get contact info: {str(e)}"

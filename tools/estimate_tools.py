from datetime import datetime
from typing import Dict, Any, Literal
from langchain_core.tools import tool

@tool
def calculate_estimate(service: str, location: str) -> str:
    """
    Calculate a cost estimate for a specific service at a given location.
    
    This tool provides pricing estimates for various services based on service type
    and location. It generates a unique estimate ID for tracking purposes.
    
    Args:
        service: Type of service requested (e.g., "lawn care", "house cleaning", "pest control", "landscaping")
        location: Service location or address
        
    Returns:
        str: Cost estimate with service details and unique estimate ID
    """
    try:
        base_prices = {
            "lawn care": 150,
            "house cleaning": 200,
            "pest control": 300,
            "landscaping": 500
        }
        
        base_price = base_prices.get(service.lower(), 250)
        estimate_id = f"EST-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return f"Estimate for {service} at {location}: ${base_price}. Estimate ID: {estimate_id}"
    except Exception as e:
        return f"Failed to calculate estimate: {str(e)}"

@tool
def verify_address(address: str) -> str:
    """
    Verify if a given address is within the service area.
    
    This tool checks whether the provided address is serviceable by the company.
    It helps determine if services can be provided at the specified location.
    
    Args:
        address: The address to verify for service availability
        
    Returns:
        str: Verification result indicating whether the address is serviceable
    """
    try:
        is_serviceable = True
        return f"Address {address} is {'serviceable' if is_serviceable else 'not serviceable'}"
    except Exception as e:
        return f"Failed to verify address: {str(e)}"

@tool
def get_service_catalog() -> str:
    """
    Retrieve the complete catalog of available services.
    
    This tool provides a comprehensive list of all services offered by the company,
    including descriptions of each service type.
    
    Returns:
        str: List of available services with descriptions
    """
    try:
        services = [
            "Lawn Care - Regular lawn maintenance and care",
            "House Cleaning - Residential cleaning services", 
            "Pest Control - Pest elimination and prevention",
            "Landscaping - Landscape design and installation"
        ]
        
        return f"Available services: {', '.join(services)}"
    except Exception as e:
        return f"Failed to get service catalog: {str(e)}"

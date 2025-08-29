from datetime import datetime, date
from typing import Dict, Any, Literal
from langchain_core.tools import tool

def validate_future_date(date_str: str, time_str: str) -> bool:
    """
    Validate that a given date and time combination is in the future.
    
    Args:
        date_str: Date in YYYY-MM-DD format
        time_str: Time in HH:MM format
        
    Returns:
        bool: True if the datetime is in the future, False otherwise
    """
    try:
        appointment_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        return appointment_datetime > datetime.now()
    except ValueError:
        return False

@tool
def create_appointment(date: str, time: str, service: str, agenda: str = None, location: str = None, contact: str = None) -> str:
    """
    FINAL STEP: Create a new appointment with complete details.
    
    Use this tool ONLY when you have ALL required information:
    - Date (YYYY-MM-DD format)
    - Time (HH:MM format) 
    - Service type
    - User has confirmed they want to book
    
    Do NOT use this tool if:
    - Missing any required information
    - User hasn't confirmed the booking
    - You're still collecting information
    
    Args:
        date: Appointment date in YYYY-MM-DD format (e.g., "2024-12-25")
        time: Appointment time in HH:MM format (e.g., "14:30")
        service: Type of service requested (e.g., "inspection", "repair", "maintenance")
        agenda: Optional description of the appointment purpose
        location: Optional service location address
        contact: Optional contact information (email or phone)
        
    Returns:
        str: Confirmation message with appointment details and ID, or error message
    """
    try:
        appointment_id = f"APT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        if not validate_future_date(date, time):
            return "Error: Appointment date and time must be in the future."
        
        response_parts = [
            f"Appointment created successfully!",
            f"Date: {date}",
            f"Time: {time}",
            f"Service: {service}",
            f"Appointment ID: {appointment_id}"
        ]
        
        if agenda:
            response_parts.append(f"Agenda: {agenda}")
        if location:
            response_parts.append(f"Location: {location}")
        if contact:
            response_parts.append(f"Contact: {contact}")
        
        response_parts.append("\nAppointment details will be sent to your provided contact information.")
        
        return "\n".join(response_parts)
    except ValueError as e:
        return f"Error: Invalid date/time format. Please use YYYY-MM-DD HH:MM format."
    except Exception as e:
        return f"Failed to create appointment: {str(e)}"

@tool
def check_availability(date: str) -> str:
    """
    Check available appointment slots for a specific date.
    
    Use this tool ONLY when:
    - User has specified a date they want to book
    - You need to show available time slots for that date
    - User asks about availability for a specific date
    
    Do NOT use this tool if:
    - User hasn't specified a date yet
    - You're still collecting other information
    - User is asking about general availability (not a specific date)
    
    Args:
        date: Date to check availability for in YYYY-MM-DD format (e.g., "2024-12-25")
        
    Returns:
        str: List of available time slots for the specified date
    """
    try:
        available_slots = ["9:00 AM", "2:00 PM", "4:00 PM"]
        return f"Available slots on {date}: {', '.join(available_slots)}"
    except Exception as e:
        return f"Failed to check availability: {str(e)}"

@tool
def reschedule_appointment(appointment_id: str, new_date: str, new_time: str) -> str:
    """
    Reschedule an existing appointment to a new date and time.
    
    This tool allows users to change the date and time of an existing appointment.
    It validates that the new datetime is in the future.
    
    Args:
        appointment_id: The unique identifier of the appointment to reschedule
        new_date: New appointment date in YYYY-MM-DD format (e.g., "2024-12-26")
        new_time: New appointment time in HH:MM format (e.g., "15:00")
        
    Returns:
        str: Confirmation message with new appointment details, or error message
    """
    try:
        if not validate_future_date(new_date, new_time):
            return "Error: New appointment date and time must be in the future."
        
        return f"Appointment {appointment_id} rescheduled to {new_date} at {new_time}"
    except Exception as e:
        return f"Failed to reschedule appointment: {str(e)}"

@tool
def validate_appointment_sops(agenda: str = None, service: str = None, date: str = None, time: str = None, location: str = None, contact: str = None) -> str:
    """
    Validate that all required Standard Operating Procedure (SOP) information is provided for appointment creation.
    
    This tool checks that all necessary information has been collected before creating an appointment.
    It validates service types, ensures future dates, and confirms all required fields are present.
    
    Args:
        agenda: Description of the appointment purpose
        service: Type of service (must be one of: inspection, repair, maintenance, installation, replacement, consultation, other)
        date: Appointment date in YYYY-MM-DD format
        time: Appointment time in HH:MM format
        location: Service location address
        contact: Contact information (email or phone)
        
    Returns:
        str: Validation result indicating missing information or confirmation that all requirements are met
    """
    missing_items = []
    
    if not agenda or agenda.strip() == "":
        missing_items.append("Agenda - purpose of the appointment")
    
    if not service or service.strip() == "":
        missing_items.append("Service type")
    elif service.lower() not in ['inspection', 'repair', 'maintenance', 'installation', 'replacement', 'consultation', 'other']:
        missing_items.append("Valid service type (must be one of: inspection, repair, maintenance, installation, replacement, consultation, other)")
    
    if not date or not time:
        missing_items.append("Date and time")
    elif not validate_future_date(date, time):
        missing_items.append("Future date and time (current selection is in the past)")
    
    if not location or location.strip() == "":
        missing_items.append("Service location")
    
    if not contact or contact.strip() == "":
        missing_items.append("Contact information (email or phone)")
    
    if missing_items:
        return f"Missing required information: {', '.join(missing_items)}"
    else:
        return "All SOP requirements have been met. Ready to create appointment."

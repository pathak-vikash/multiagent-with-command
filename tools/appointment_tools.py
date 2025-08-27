from datetime import datetime
from typing import Dict, Any, Literal
from langchain_core.tools import tool

@tool
def create_appointment(date: str, time: str, service: str) -> str:
    """Create a new appointment with the specified details."""
    try:
        appointment_id = f"APT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        return f"Appointment created for {service} on {date} at {time}. Appointment ID: {appointment_id}"
    except Exception as e:
        return f"Failed to create appointment: {str(e)}"

@tool
def check_availability(date: str) -> str:
    """Check available appointment slots for a specific date."""
    try:
        # Mock availability data
        available_slots = ["9:00 AM", "2:00 PM", "4:00 PM"]
        return f"Available slots on {date}: {', '.join(available_slots)}"
    except Exception as e:
        return f"Failed to check availability: {str(e)}"

@tool
def reschedule_appointment(appointment_id: str, new_date: str, new_time: str) -> str:
    """Reschedule an existing appointment to a new date and time."""
    try:
        return f"Appointment {appointment_id} rescheduled to {new_date} at {new_time}"
    except Exception as e:
        return f"Failed to reschedule appointment: {str(e)}"

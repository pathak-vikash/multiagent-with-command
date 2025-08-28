from datetime import datetime, date
from typing import Dict, Any, Literal
from langchain_core.tools import tool

def validate_future_date(date_str: str, time_str: str) -> bool:
    try:
        appointment_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        return appointment_datetime > datetime.now()
    except ValueError:
        return False

@tool
def create_appointment(date: str, time: str, service: str, agenda: str = None, location: str = None, contact: str = None) -> str:
    try:
        appointment_id = f"APT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        if not validate_future_date(date, time):
            return "Error: Appointment date and time must be in the future."
        
        response_parts = [
            f"✅ Appointment created successfully!",
            f"📅 Date: {date}",
            f"🕐 Time: {time}",
            f"🔧 Service: {service}",
            f"🆔 Appointment ID: {appointment_id}"
        ]
        
        if agenda:
            response_parts.append(f"📋 Agenda: {agenda}")
        if location:
            response_parts.append(f"📍 Location: {location}")
        if contact:
            response_parts.append(f"📞 Contact: {contact}")
        
        response_parts.append("\n📧 Appointment details will be sent to your provided contact information.")
        
        return "\n".join(response_parts)
    except ValueError as e:
        return f"Error: Invalid date/time format. Please use YYYY-MM-DD HH:MM format."
    except Exception as e:
        return f"Failed to create appointment: {str(e)}"

@tool
def check_availability(date: str) -> str:
    try:
        available_slots = ["9:00 AM", "2:00 PM", "4:00 PM"]
        return f"Available slots on {date}: {', '.join(available_slots)}"
    except Exception as e:
        return f"Failed to check availability: {str(e)}"

@tool
def reschedule_appointment(appointment_id: str, new_date: str, new_time: str) -> str:
    try:
        return f"Appointment {appointment_id} rescheduled to {new_date} at {new_time}"
    except Exception as e:
        return f"Failed to reschedule appointment: {str(e)}"

@tool
def validate_appointment_sops(agenda: str = None, service: str = None, date: str = None, time: str = None, location: str = None, contact: str = None) -> str:
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
        return f"❌ Missing required information: {', '.join(missing_items)}"
    else:
        return "✅ All SOP requirements have been met. Ready to create appointment."

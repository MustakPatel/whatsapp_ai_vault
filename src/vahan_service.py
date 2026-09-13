import os
import re
from src.vault_service import get_setting, set_setting

DEFAULT_VEHICLE_REG = "MP09XX1234"

def get_default_vehicle() -> str:
    """Returns saved default vehicle registration number from database or fallback."""
    return get_setting("saved_vehicle_reg", DEFAULT_VEHICLE_REG)

def set_default_vehicle(reg_no: str) -> str:
    global DEFAULT_VEHICLE_REG
    clean_reg = re.sub(r'[^A-Za-z0-9]', '', reg_no).upper()
    if clean_reg:
        DEFAULT_VEHICLE_REG = clean_reg
        set_setting("saved_vehicle_reg", clean_reg)
    return clean_reg if clean_reg else get_default_vehicle()

def get_vehicle_details(registration_no: str = None) -> dict:
    """
    Fetches Vehicle RC, Owner Name, Model, Insurance & Pollution Expiry by Vehicle Registration Number.
    If registration_no is omitted or generic ('my vehicle'), uses saved registered vehicle.
    """
    saved_reg = get_default_vehicle()
    if not registration_no or registration_no.lower().strip() in ["my vehicle", "vehicle", "car", "bike", "my vehicle details", "my saved vehicle"]:
        registration_no = saved_reg

    clean_reg = re.sub(r'[^A-Za-z0-9]', '', registration_no).upper()
    if not clean_reg:
        clean_reg = saved_reg

    # Format simulation response for Parivahan Vehicle Info
    return {
        "status": "success",
        "registration_no": clean_reg,
        "owner_name": "MUSTAK PATEL",
        "maker_model": "HYUNDAI CRETA 1.5 PETROL / SX",
        "vehicle_class": "Motor Car (LMV)",
        "registration_date": "15-Aug-2022",
        "fitness_valid_upto": "14-Aug-2037",
        "insurance_company": "ICICI Lombard General Insurance",
        "insurance_valid_upto": "14-Aug-2027",
        "pucc_valid_upto": "10-Nov-2026",
        "tax_valid_upto": "LTT (Life Time Tax)"
    }

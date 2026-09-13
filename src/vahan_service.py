import re

def get_vehicle_details(registration_no: str) -> dict:
    """
    Fetches Vehicle RC, Owner Name, Model, Insurance & Pollution Expiry by Vehicle Registration Number.
    Simulates Parivahan/Vahan API response with structure.
    """
    clean_reg = re.sub(r'[^A-Za-z0-9]', '', registration_no).upper()
    
    if not clean_reg:
        return {"status": "error", "message": "Invalid Vehicle Registration Number."}

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

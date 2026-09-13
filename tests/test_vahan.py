import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.vahan_service import get_vehicle_details

def test_get_vehicle_details():
    res = get_vehicle_details("MP09AB1234")
    assert res["status"] == "success"
    assert res["registration_no"] == "MP09AB1234"
    assert "owner_name" in res
    assert "insurance_valid_upto" in res
    assert "pucc_valid_upto" in res

def test_set_default_vehicle():
    from src.vahan_service import set_default_vehicle, get_default_vehicle
    saved = set_default_vehicle("MP09CD5678")
    assert saved == "MP09CD5678"
    assert get_default_vehicle() == "MP09CD5678"
    
    # Test getting details without specifying registration number uses saved vehicle
    res = get_vehicle_details()
    assert res["registration_no"] == "MP09CD5678"

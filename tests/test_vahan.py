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

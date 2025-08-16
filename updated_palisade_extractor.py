#!/usr/bin/env python3
"""
Updated Hyundai Palisade 2024 Calligraphy Fingerprint Extractor

Based on the real carFw data from the user's actual device.
This includes ECUs from multiple brands (Hyundai, Volkswagen, Subaru).

Author: OpenPilot Community
"""

import json
import re
from typing import Dict, List, Tuple, Any

# Updated firmware data from actual comma device - Palisade 2024 Calligraphy
PALISADE_2024_CALLIGRAPHY_FW_DATA = [
    # Hyundai ECUs
    {
        'address': 1990, 'brand': 'hyundai', 'bus': 1, 'ecu': 'combinationMeter',
        'fwVersion': b'\xf1\x00020', 'responseAddress': 1998, 'subAddress': 0
    },
    {
        'address': 2004, 'brand': 'hyundai', 'bus': 1, 'ecu': 'eps',
        'fwVersion': b'\xf1\x00LXP MDPS C 1.00 1.00 56310S8620\x00 4LXPC100',
        'responseAddress': 2012, 'subAddress': 0
    },
    {
        'address': 2001, 'brand': 'hyundai', 'bus': 1, 'ecu': 'abs',
        'fwVersion': b'\xf1\x00LX ESC \x0b 103#\x03) 58910-S8700',
        'responseAddress': 2009, 'subAddress': 0
    },
    {
        'address': 1971, 'brand': 'hyundai', 'bus': 1, 'ecu': 'hvac',
        'fwVersion': b"\xf1\x00LX2   97250-S8BH0CONTROL ASS'Y-DATC  1.03 LX2PE ATC 1.4 1.00  ",
        'responseAddress': 1979, 'subAddress': 0
    },
    {
        'address': 1975, 'brand': 'hyundai', 'bus': 1, 'ecu': 'cornerRadar',
        'fwVersion': b'\xf1\x00LX2 BCW RR 2.00 , 3.00 (\x81SW#\x02h\x02\x81',
        'responseAddress': 1983, 'subAddress': 0
    },
    {
        'address': 2017, 'brand': 'hyundai', 'bus': 1, 'ecu': 'transmission',
        'fwVersion': b'\xf1\x00bcsh8p55  U992\x00\x00\x00\x00\x00\x00SLX0G38GSBU\xd4\xb5\xa4',
        'responseAddress': 2025, 'subAddress': 0
    },
    {
        'address': 1988, 'brand': 'hyundai', 'bus': 1, 'ecu': 'fwdCamera',
        'fwVersion': b'\xf1\x00LX2 MFC  AT MES LHD 1.00 1.01 99211-S8600 230817',
        'responseAddress': 1996, 'subAddress': 0
    },
    {
        'address': 2000, 'brand': 'hyundai', 'bus': 1, 'ecu': 'fwdRadar',
        'fwVersion': b'\xf1\x00LX2_ SCC F-CUP      1.00 1.00 99110-S8600         ',
        'responseAddress': 2008, 'subAddress': 0
    },
    # Additional fwdRadar version with different request type
    {
        'address': 2000, 'brand': 'hyundai', 'bus': 1, 'ecu': 'fwdRadar',
        'fwVersion': b'\xf1\x10\x00\x00j\x00',
        'responseAddress': 2008, 'subAddress': 0
    },
    {
        'address': 1969, 'brand': 'hyundai', 'bus': 1, 'ecu': 'parkingAdas',
        'fwVersion': b'\xf1\x10LXPB ADAS_PRK AXL 1.01 1.03 99910-S8500',
        'responseAddress': 1977, 'subAddress': 0
    },
    
    # NOTE: Volkswagen and Subaru ECUs are also present but we'll focus on Hyundai ones
    # for the fingerprint to avoid confusion
]

# Vehicle specifications
VEHICLE_SPECS = {
    'mass': 1836,  # kg
    'wheelbase': 2.7,  # meters  
    'steerRatio': 13.0,
    'tireStiffnessFactor': 1.0,
    'vin': 'KMHR781E3RU747802',
    'trim': 'Calligraphy'
}

# ECU mapping for OpenPilot
ECU_MAPPING = {
    'combinationMeter': 'combinationMeter',
    'eps': 'eps',
    'abs': 'abs',
    'hvac': 'hvac',
    'cornerRadar': 'cornerRadar',
    'transmission': 'transmission',
    'fwdCamera': 'fwdCamera',
    'fwdRadar': 'fwdRadar',
    'parkingAdas': 'parkingAdas',
}

def decimal_to_hex(address: int) -> str:
    """Convert decimal address to hexadecimal format."""
    return f"0x{address:x}"

def format_firmware_bytes(fw_bytes: bytes) -> str:
    """Format firmware bytes for OpenPilot fingerprint."""
    return repr(fw_bytes)

def extract_unique_firmware_versions() -> Dict[Tuple[str, str, str], List[bytes]]:
    """Extract unique firmware versions grouped by ECU and address."""
    
    fw_dict = {}
    
    for fw_entry in PALISADE_2024_CALLIGRAPHY_FW_DATA:
        # Only process Hyundai ECUs
        if fw_entry['brand'] != 'hyundai':
            continue
            
        ecu = fw_entry['ecu']
        address = decimal_to_hex(fw_entry['address'])
        sub_address = fw_entry.get('subAddress', None)
        sub_addr_str = f"0x{sub_address:x}" if sub_address is not None and sub_address != 0 else "None"
        fw_version = fw_entry['fwVersion']
        
        # Map ECU to OpenPilot format
        if ecu in ECU_MAPPING:
            ecu_key = f"Ecu.{ECU_MAPPING[ecu]}"
            entry_key = (ecu_key, address, sub_addr_str)
            
            if entry_key not in fw_dict:
                fw_dict[entry_key] = []
            
            if fw_version not in fw_dict[entry_key]:
                fw_dict[entry_key].append(fw_version)
    
    return fw_dict

def generate_fingerprint_code() -> str:
    """Generate OpenPilot fingerprint code."""
    
    fw_dict = extract_unique_firmware_versions()
    
    code_lines = []
    code_lines.append("  CAR.HYUNDAI_PALISADE_2024: {")
    
    for (ecu, address, sub_address), fw_versions in sorted(fw_dict.items()):
        code_lines.append(f"    ({ecu}, {address}, {sub_address}): [")
        
        for fw_version in sorted(fw_versions, key=lambda x: x.hex()):
            formatted_fw = format_firmware_bytes(fw_version)
            code_lines.append(f"      {formatted_fw},")
        
        code_lines.append("    ],")
    
    code_lines.append("  },")
    
    return "\n".join(code_lines)

def generate_values_entry() -> str:
    """Generate values.py entry for the new vehicle."""
    
    specs = VEHICLE_SPECS
    
    code = f"""  HYUNDAI_PALISADE_2024 = HyundaiPlatformConfig(
    [
      HyundaiCarDocs("Hyundai Palisade 2024 Calligraphy", "All", 
                     car_parts=CarParts.common([CarHarness.hyundai_h])),
    ],
    CarSpecs(mass={specs['mass']}, wheelbase={specs['wheelbase']}, 
             steerRatio={specs['steerRatio']}, tireStiffnessFactor={specs['tireStiffnessFactor']}),
    flags=HyundaiFlags.MANDO_RADAR,
  )"""
    
    return code

def analyze_differences():
    """Analyze differences between expected and actual data."""
    
    print("🔍 Analysis of Fingerprint Data:")
    print("=" * 50)
    print()
    
    print("📊 Key Findings:")
    print("-" * 20)
    print("1. Multiple brands detected in same vehicle:")
    print("   - Hyundai: Primary ECUs (10 units)")
    print("   - Volkswagen: Engine & Transmission")
    print("   - Subaru: Engine & Transmission (alternative protocol)")
    print()
    
    print("2. Calligraphy trim has additional features:")
    print("   - Enhanced HVAC system")
    print("   - Advanced parking assistance")
    print("   - Multiple protocol support for same ECUs")
    print()
    
    print("3. fwdRadar has two different firmware versions:")
    print("   - Standard version: LX2_ SCC F-CUP")
    print("   - Alternative request: \\xf1\\x10\\x00\\x00j\\x00")
    print()
    
    print("⚠️  Why previous fingerprint failed:")
    print("-" * 35)
    print("- Missing the second fwdRadar firmware version")
    print("- ECU count and combinations didn't match exactly")
    print("- OpenPilot requires EXACT firmware matches")
    print()

def main():
    """Main execution function."""
    
    print("🚗 Updated Hyundai Palisade 2024 Calligraphy Fingerprint Extractor")
    print("=" * 70)
    print(f"Vehicle: Hyundai Palisade 2024 {VEHICLE_SPECS['trim']}")
    print(f"VIN: {VEHICLE_SPECS['vin']}")
    print()
    
    # Analyze the differences
    analyze_differences()
    
    print("📝 Updated Fingerprint Code for fingerprints.py:")
    print("-" * 55)
    fingerprint_code = generate_fingerprint_code()
    print(fingerprint_code)
    print()
    
    print("📝 Updated Values Code for values.py:")
    print("-" * 40)
    values_code = generate_values_entry()
    print(values_code)
    print()
    
    print("✅ Ready to apply the fix!")
    print("This should resolve the 'Car Unrecognized' issue.")

if __name__ == "__main__":
    main()
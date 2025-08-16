#!/usr/bin/env python3
"""
Hyundai Palisade 2024 Fingerprint Extractor

This tool extracts and converts carFw data from carParams for the 2024 Hyundai Palisade
to generate appropriate fingerprint entries for OpenPilot.

Author: OpenPilot Community
Date: 2024
License: MIT
"""

import json
import re
from typing import Dict, List, Tuple, Any

# Raw carFw data extracted from carParams for 2024 Hyundai Palisade
PALISADE_2024_FIRMWARE_DATA = [
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
        'address': 1975, 'brand': 'hyundai', 'bus': 1, 'ecu': 'cornerRadar',
        'fwVersion': b'\xf1\x00LX2 BCW RR 2.00 , 3.00 (\x81SW#\x02h\x02\x81',
        'responseAddress': 1983, 'subAddress': 0
    },
    {
        'address': 1971, 'brand': 'hyundai', 'bus': 1, 'ecu': 'hvac',
        'fwVersion': b"\xf1\x00LX2   97250-S8BH0CONTROL ASS'Y-DATC  1.03 LX2PE ATC 1.4 1.00  ",
        'responseAddress': 1979, 'subAddress': 0
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
    {
        'address': 1969, 'brand': 'hyundai', 'bus': 1, 'ecu': 'parkingAdas',
        'fwVersion': b'\xf1\x10LXPB ADAS_PRK AXL 1.01 1.03 99910-S8500',
        'responseAddress': 1977, 'subAddress': 0
    },
]

# Vehicle specifications extracted from carParams
VEHICLE_SPECS = {
    'mass': 1836,  # kg
    'wheelbase': 2.7,  # meters  
    'steerRatio': 13.0,
    'tireStiffnessFactor': 1.0,
    'vin': 'KMHR781E3RU747802'
}

# ECU mapping for OpenPilot compatibility
ECU_MAPPING = {
    'combinationMeter': 'combinationMeter',
    'eps': 'eps', 
    'abs': 'abs',
    'cornerRadar': 'cornerRadar',
    'hvac': 'hvac',
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
    
    for fw_entry in PALISADE_2024_FIRMWARE_DATA:
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
      HyundaiCarDocs("Hyundai Palisade 2024", "All", 
                     car_parts=CarParts.common([CarHarness.hyundai_h])),
    ],
    CarSpecs(mass={specs['mass']}, wheelbase={specs['wheelbase']}, 
             steerRatio={specs['steerRatio']}, tireStiffnessFactor={specs['tireStiffnessFactor']}),
    flags=HyundaiFlags.MANDO_RADAR,
  )"""
    
    return code

def generate_summary_report() -> str:
    """Generate summary report of extracted data."""
    
    fw_dict = extract_unique_firmware_versions()
    specs = VEHICLE_SPECS
    
    report = []
    report.append("=" * 70)
    report.append("Hyundai Palisade 2024 Fingerprint Extraction Report")
    report.append("=" * 70)
    report.append("")
    
    report.append("🚗 Vehicle Information:")
    report.append("   - Make: Hyundai")
    report.append("   - Model: Palisade")
    report.append("   - Year: 2024")
    report.append(f"   - VIN: {specs['vin']}")
    report.append(f"   - Mass: {specs['mass']} kg")
    report.append(f"   - Wheelbase: {specs['wheelbase']} m")
    report.append("")
    
    report.append("🔧 Detected ECUs:")
    for i, (ecu, address, sub_address) in enumerate(sorted(fw_dict.keys()), 1):
        ecu_name = ecu.replace("Ecu.", "")
        report.append(f"   {i:2d}. {ecu_name:15s} - Address: {address:6s} - Sub: {sub_address}")
    report.append("")
    
    report.append("📊 Summary Statistics:")
    report.append(f"   - Total ECUs: {len(fw_dict)}")
    total_fw_versions = sum(len(versions) for versions in fw_dict.values())
    report.append(f"   - Total Firmware Versions: {total_fw_versions}")
    report.append("")
    
    return "\n".join(report)

def generate_installation_instructions() -> str:
    """Generate installation and testing instructions."""
    
    instructions = []
    instructions.append("📋 Installation Instructions:")
    instructions.append("-" * 30)
    instructions.append("")
    instructions.append("1. Code Integration:")
    instructions.append("   - Add values.py code to: opendbc/car/hyundai/values.py")
    instructions.append("   - Add fingerprint code to: opendbc/car/hyundai/fingerprints.py")
    instructions.append("")
    instructions.append("2. Testing:")
    instructions.append("   - Validate syntax: python3 -m py_compile values.py fingerprints.py")
    instructions.append("   - Test on device using custom installer URL")
    instructions.append("   - Verify vehicle recognition (no 'Car Unrecognized' message)")
    instructions.append("")
    instructions.append("3. Contributing:")
    instructions.append("   - Create GitHub fork of openpilot")
    instructions.append("   - Submit pull request with detailed description")
    instructions.append("   - Include testing results and vehicle specifications")
    instructions.append("")
    
    return "\n".join(instructions)

def main():
    """Main execution function."""
    
    print("🚗 Hyundai Palisade 2024 Fingerprint Extractor")
    print("=" * 50)
    print()
    
    # Generate summary report
    summary = generate_summary_report()
    print(summary)
    
    # Generate fingerprint code
    print("📝 Fingerprint Code for fingerprints.py:")
    print("-" * 50)
    fingerprint_code = generate_fingerprint_code()
    print(fingerprint_code)
    print()
    
    # Generate values code
    print("📝 Values Code for values.py:")
    print("-" * 50)
    values_code = generate_values_entry()
    print(values_code)
    print()
    
    # Generate installation instructions
    instructions = generate_installation_instructions()
    print(instructions)
    
    print("✅ Extraction completed successfully!")

if __name__ == "__main__":
    main()
# OpenPilot Fingerprinting Guide

## Overview

This guide provides comprehensive instructions for adding fingerprint support for new vehicles in OpenPilot. Fingerprinting is the process by which OpenPilot identifies the connected vehicle by reading firmware versions from Electronic Control Units (ECUs).

## What is Fingerprinting?

**Fingerprinting** is OpenPilot's method to automatically detect the vehicle model by:
- Reading firmware versions from various ECUs
- Matching these versions against known patterns
- Configuring the appropriate vehicle parameters

## Prerequisites

### Hardware Requirements
- ✅ Official comma device (comma 3/3X)
- ✅ Compatible OBD-II harness
- ✅ WiFi connection for data upload
- ✅ Comma.ai account

### Technical Skills
- ✅ Basic Git/GitHub knowledge
- ✅ Python fundamentals
- ✅ Understanding of hexadecimal numbers
- ✅ Ability to read openpilot codebase

## Fingerprinting Process (2.0)

### Step 1: Record Drive Data
1. **Connect Device**: Ensure comma device is properly connected
2. **Record Drive**: Drive for 10-15 minutes in a safe area
3. **Upload Data**: Return home and connect to WiFi to upload

### Step 2: Extract Firmware Data
1. **Access Portal**: Visit https://my.comma.ai/useradmin
2. **Login**: Use your openpilot account credentials
3. **Select Drive**: Choose your most recent drive recording
4. **Select Segment**: Choose segment 0 (first segment)
5. **Find carParams**: Select carParams from the log dropdown
6. **Extract carFw**: Copy all firmware version data

### Step 3: Process the Data
Convert the extracted data into openpilot format:

```python
# Example extracted data
fw_data = {
    'address': 2004,
    'brand': 'hyundai',
    'ecu': 'eps', 
    'fwVersion': b'\\xf1\\x00LXP MDPS C 1.00 1.00 56310S8620\\x00 4LXPC100',
    'subAddress': 0
}

# Convert to openpilot fingerprint format
fingerprint_entry = {
    (Ecu.eps, 0x7d4, None): [
        b'\\xf1\\x00LXP MDPS C 1.00 1.00 56310S8620\\x00 4LXPC100',
    ]
}
```

### Step 4: Update Code Files
Add the new vehicle to two key files:

#### values.py
```python
HYUNDAI_PALISADE_2024 = HyundaiPlatformConfig(
  [
    HyundaiCarDocs("Hyundai Palisade 2024", "All", 
                   car_parts=CarParts.common([CarHarness.hyundai_h])),
  ],
  CarSpecs(mass=1836, wheelbase=2.7, steerRatio=13.0, tireStiffnessFactor=1.0),
  flags=HyundaiFlags.MANDO_RADAR,
)
```

#### fingerprints.py
```python
CAR.HYUNDAI_PALISADE_2024: {
  (Ecu.abs, 0x7d1, None): [
    b'\\xf1\\x00LX ESC \\x0b 103#\\x03) 58910-S8700',
  ],
  (Ecu.eps, 0x7d4, None): [
    b'\\xf1\\x00LXP MDPS C 1.00 1.00 56310S8620\\x00 4LXPC100',
  ],
  # ... additional ECUs
},
```

## Common ECU Types

| ECU | Description | Typical Address Range |
|-----|-------------|----------------------|
| `abs` | Anti-lock Braking System | 0x7d1 |
| `eps` | Electronic Power Steering | 0x7d4 |
| `fwdCamera` | Forward Camera | 0x7c4 |
| `fwdRadar` | Forward Radar | 0x7d0 |
| `engine` | Engine Control Module | 0x7e0 |
| `transmission` | Transmission Control | 0x7e1 |

## Testing and Validation

### Code Validation
```bash
# Check Python syntax
python3 -m py_compile values.py fingerprints.py

# Test imports
python3 -c "from values import CAR; print('Syntax OK')"
```

### Real-world Testing
1. **Fork Repository**: Create personal fork on GitHub
2. **Install Custom Branch**: Use installer with your branch
3. **Test Recognition**: Verify vehicle is recognized
4. **Validate Functions**: Test basic openpilot functions

## Contributing Back

### Pull Request Process
1. **Create Branch**: Use descriptive branch name
2. **Commit Changes**: Write clear commit messages
3. **Test Thoroughly**: Ensure no regressions
4. **Submit PR**: Include detailed description
5. **Respond to Reviews**: Address feedback promptly

### PR Requirements
- ✅ Clear description of changes
- ✅ Real-world testing results
- ✅ No syntax errors
- ✅ Follows coding standards
- ✅ Documentation updates

## Troubleshooting

### Empty carFw Data
If `carFw` is empty, check:
- Cable connections (CAT5, USB-C)
- Fuse integrity
- OBD-II port functionality
- Device power supply

### Recognition Issues
- Verify address formats (hex vs decimal)
- Check ECU naming consistency
- Ensure firmware data is complete
- Validate against similar vehicles

## Best Practices

### Data Quality
- ✅ Use real firmware data only
- ✅ Verify all addresses and formats
- ✅ Test with actual hardware
- ✅ Document data sources

### Code Quality
- ✅ Follow existing patterns
- ✅ Maintain alphabetical ordering
- ✅ Use consistent formatting
- ✅ Add meaningful comments

### Safety
- ✅ Test in safe environments only
- ✅ Never modify existing fingerprints without cause
- ✅ Follow local traffic laws
- ✅ Report issues promptly

## Resources

### Official Documentation
- [OpenPilot Docs](https://docs.comma.ai)
- [Fingerprinting Wiki](https://github.com/commaai/openpilot/wiki/Fingerprinting)
- [Contributing Guidelines](https://github.com/commaai/openpilot/blob/master/docs/CONTRIBUTING.md)

### Community
- [Discord Server](https://discord.comma.ai)
- [GitHub Discussions](https://github.com/commaai/openpilot/discussions)
- [Reddit Community](https://reddit.com/r/Comma_ai)

---

*This guide is based on OpenPilot's latest fingerprinting procedures and community best practices.*
name = 'Adversary Emulation for Thesis'
description = 'A Caldera plugin to emulate ransomware precursor TTPs for automated forensic dataset generation, based on thesis research.'
address = None # No UI component

async def enable(services):
    print(f"INFO: Plugin '{name}' - ENABLE hook called. Trusting dynamic parser loading.")
    if hasattr(services, 'get_services'):
        available_services = services.get_services()
        print(f"DEBUG (enable hook): Available services in ServiceRegistry: {list(available_services.keys())}")
    elif isinstance(services, dict):
        print(f"DEBUG (enable hook): Available service keys: {list(services.keys())}")
    else:
        print(f"DEBUG (enable hook): 'services' object type: {type(services)}")
    pass

async def expansion(services):
    print(f"INFO: Plugin '{name}' - EXPANSION hook called.")
    pass

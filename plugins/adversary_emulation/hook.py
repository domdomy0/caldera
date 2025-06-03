name = 'Adversary Emulation'
description = 'A Caldera plugin to emulate ransomware precursor TTPs for automated forensic dataset generation, based on thesis research.'
address = None # No UI component

async def enable(services):
    if hasattr(services, 'get_services'): 
        available_services = services.get_services()
    elif isinstance(services, dict): 
    else:
    pass

async def expansion(services):
    pass

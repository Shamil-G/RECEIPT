from receipt_parameter import using, app_name


if using == 'DEV_WIN_HOME':
    BASE = f'D:/Shamil/{app_name}'
elif using == 'DEV_WIN':
    BASE = f'C:/Shamil/{app_name}'
else:
    BASE = f'/home/cut_pdf/{app_name}'

if using[0:7] != 'DEV_WIN':
    host = 'localhost'
    port = 5000
    os = 'unix'
    debug_level = 2
    service_host_002 = 'notes.gov4c.kz'
    service_port_002 = 5001
    service_host_004 = 'notes.gov4c.kz'
    service_port_004 = 5002
else:
    host = 'localhost'
    port = 80
    os = '!unix'
    debug_level = 4
    service_host_002 = 'notes.gov4c.kz'
    service_port_002 = 5001
    service_host_004 = 'notes.gov4c.kz'
    service_port_004 = 5002

LOG_FILE = f'{BASE}/pdd.log'
SPOOL = f'{BASE}/spool'
debug = True
trace_malloc = False

print(f"=====> CONFIG. using: {using}, BASE: {BASE}, app_name: {app_name}")



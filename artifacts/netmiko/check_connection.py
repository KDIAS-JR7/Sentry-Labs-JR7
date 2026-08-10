from netmiko import ConnectHandler
from datetime import datetime
import os

device = {
    'device_type': 'cisco_ios',
    'host': 'R1',
    'username': 'admin',
    'password': 'cisco123',
    'ssh_config_file': '/root/.ssh/config',
}

# Ensure a logs directory exists
os.makedirs('logs', exist_ok=True)
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")

try:
    print(f"--- Sentry-Pod: Harvesting Data from R1 [{timestamp}] ---")
    connection = ConnectHandler(**device)

    # Capture the full config
    config_data = connection.send_command("show run")

    # Save to the shared volume
    filename = f"logs/R1_golden_config_{timestamp}.txt"
    with open(filename, "w") as f:
        f.write(config_data)

    print(f"Success! Data saved to: {filename}")
    connection.disconnect()

except Exception as e:
    print(f"Extraction Failed: {e}")

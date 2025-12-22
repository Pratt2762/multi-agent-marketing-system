# Script to update executor.py with Adobe execution capabilities

old_init = """    def __init__(self):
        # Policy values are loaded dynamically via policy_loader
        pass"""

new_init = """    def __init__(self, adobe_client=None, execute_to_adobe=False):
        \"\"\"
        Initialize executor with optional Adobe client.

        Args:
            adobe_client: AdobeAEPClient or MockAdobeClient instance
            execute_to_adobe: If True, execute actions to Adobe APIs (write mode)
                             If False, only simulate/log actions (read-only mode)
        \"\"\"
        # Policy values are loaded dynamically via policy_loader
        self.adobe_client = adobe_client
        self.execute_to_adobe = execute_to_adobe

        if self.execute_to_adobe and not self.adobe_client:
            raise ValueError("Adobe client required when execute_to_adobe=True")"""

# Read file
with open('backend/logic/executor.py', 'r') as f:
    content = f.read()

# Replace __init__ method
content = content.replace(old_init, new_init)

# Write back
with open('backend/logic/executor.py', 'w') as f:
    f.write(content)

print("Updated executor.py __init__ method")

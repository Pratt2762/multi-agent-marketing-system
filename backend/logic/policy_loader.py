import json
import os

POLICY_FILE_PATH = "policy.json"

class PolicyLoader:
    """
    Loads and provides access to the dynamic policy rules from policy.json.
    """
    _instance = None
    _policy = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PolicyLoader, cls).__new__(cls)
            cls._instance._load_policy()
        return cls._instance

    def _load_policy(self):
        try:
            # Construct the absolute path to the policy file
            # Assuming policy.json is in the root of the workspace
            policy_path = os.path.join(os.getcwd(), POLICY_FILE_PATH)
            
            with open(policy_path, 'r') as f:
                self._policy = json.load(f)
        except FileNotFoundError:
            print(f"Error: Policy file not found at {POLICY_FILE_PATH}. Using empty policy.")
            self._policy = {}
        except json.JSONDecodeError:
            print(f"Error: Policy file {POLICY_FILE_PATH} is invalid JSON. Using empty policy.")
            self._policy = {}

    def get_policy(self):
        """Returns the loaded policy dictionary."""
        return self._policy

    def get_value(self, *keys, default=None):
        """
        Retrieves a nested value from the policy using a sequence of keys.
        Example: get_value('budget', 'increase_factor')
        """
        current = self._policy
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current

# Global instance for easy access
policy_loader = PolicyLoader()
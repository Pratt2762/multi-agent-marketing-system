import json
from datetime import datetime
from backend.logic.policy_loader import policy_loader

class AgentLogger:
    """
    Handles structured logging for the agent's run cycle.
    Logs are stored in a list and can be retrieved as a structured object.
    """
    def __init__(self):
        self.log_history = []
        self.trace_mode = policy_loader.get_value('logging', 'trace_mode', default=False)
        self.current_step_log = {}

    def start_step(self, week):
        """Initializes the log for a new simulation step."""
        self.current_step_log = {
            "timestamp": datetime.utcnow().isoformat(),
            "week": week,
            "actions_executed": [],
            "numeric_modifications": {},
            "raw_llm_output": None,
            "llm_prompt": None,
            "final_performance_metrics": None
        }

    def log_prompt(self, prompt_text):
        """Records the prompt sent to the LLM."""
        if self.trace_mode:
            self.current_step_log["llm_prompt"] = prompt_text

    def log_raw_output(self, raw_output):
        """Records the raw output from the LLM."""
        if self.trace_mode:
            self.current_step_log["raw_llm_output"] = raw_output

    def log_action(self, action_type, target_id, details=None):
        """Records a qualitative action interpreted from the LLM output."""
        if self.trace_mode:
            log_entry = {
                "type": action_type,
                "target_id": target_id
            }
            if details:
                log_entry.update(details)
            self.current_step_log["actions_executed"].append(log_entry)

    def log_numeric_change(self, target_id, field, old_value, new_value):
        """Records a numeric modification applied by the Executor."""
        if self.trace_mode:
            key = f"{target_id}_{field}"
            self.current_step_log["numeric_modifications"][key] = {
                "field": field,
                "old": old_value,
                "new": new_value
            }

    def log_final_performance(self, metrics):
        """Records the final simulated performance metrics."""
        self.current_step_log["final_performance_metrics"] = metrics
        
    def end_step(self):
        """Finalizes the current step log and adds it to history."""
        self.log_history.append(self.current_step_log)
        self.current_step_log = {}

    def get_history(self):
        """Returns the full log history."""
        return self.log_history

# Global instance for easy access
agent_logger = AgentLogger()
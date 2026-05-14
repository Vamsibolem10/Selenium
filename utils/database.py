import json
import os
from datetime import datetime
from utils.logger import log

class AuditDatabase:
    DB_FILE = "logs/audit_history.json"

    @staticmethod
    def save_result(result):
        """Saves audit results to a JSON database for historical tracking."""
        os.makedirs("logs", exist_ok=True)
        
        history = []
        if os.path.exists(AuditDatabase.DB_FILE):
            with open(AuditDatabase.DB_FILE, "r") as f:
                try:
                    history = json.load(f)
                except:
                    history = []

        # Add metadata
        result["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        history.append(result)

        with open(AuditDatabase.DB_FILE, "w") as f:
            json.dump(history, f, indent=4)
        
        log.info(f"Result saved to historical database: {AuditDatabase.DB_FILE}")

    @staticmethod
    def get_last_run():
        if os.path.exists(AuditDatabase.DB_FILE):
            with open(AuditDatabase.DB_FILE, "r") as f:
                history = json.load(f)
                return history[-1] if history else None
        return None

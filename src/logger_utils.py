import os
import sys
import datetime
import builtins

class LoggerConfig:
    def __init__(self, base_dir="Runs"):
        self.base_dir = base_dir
        self.run_dir = None
        self.output_dir = None
        self.log_file = None
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr

    def start_run(self):
        # Create timestamped directory name (Sanitized for Windows)
        now = datetime.datetime.now()
        timestamp = now.strftime("%m-%d-%Y_%H-%M")
        
        self.run_dir = os.path.join(self.base_dir, timestamp)
        self.output_dir = os.path.join(self.run_dir, "output")
        
        # Create directories
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Setup log file
        self.log_file = open(os.path.join(self.run_dir, "log.txt"), "a", encoding='utf-8')
        
        # Redirect stdout/stderr
        sys.stdout = self
        sys.stderr = self
        
        print(f"[{datetime.datetime.now()}] Run started: {self.run_dir}")
        return self.output_dir

    def write(self, message):
        self._original_stdout.write(message)
        if self.log_file:
            self.log_file.write(message)
            self.log_file.flush()

    def flush(self):
        self._original_stdout.flush()
        if self.log_file:
            self.log_file.flush()

    def stop_run(self):
        if self.log_file:
            print(f"[{datetime.datetime.now()}] Run finished.")
            self.log_file.close()
            self.log_file = None
        
        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr

# Singleton instance
run_logger = LoggerConfig()

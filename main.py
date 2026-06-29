import os
import sys
import subprocess
import threading
import time
import signal
from datetime import datetime, timezone, timedelta

# TERMINAL COLOR CONSTANTS
COLOR_RESET = "\033[0m"
COLOR_API = "\033[92m"      # Green
COLOR_FRONTEND = "\033[94m" # Blue
COLOR_SCRAPER = "\033[93m"  # Yellow
COLOR_SYSTEM = "\033[95m"   # Magenta/Purple
COLOR_ERROR = "\033[91m"    # Red

# GLOBAL PROCESS TRACKER FOR GRACEFUL SHUTDOWN
active_processes = []
shutdown_event = threading.Event()

def log_system(msg):
    print(f"{COLOR_SYSTEM}[SYSTEM]{COLOR_RESET} {msg}")

def log_error(msg):
    print(f"{COLOR_ERROR}[ERROR]{COLOR_RESET} {msg}")

def log_reader(pipe, prefix, color):
    """
    Reads the standard output/error stream of a subprocess line-by-line
    and prints it to the console with the corresponding color prefix.
    """
    try:
        for line in iter(pipe.readline, b''):
            decoded = line.decode('utf-8', errors='ignore').rstrip()
            if decoded:
                print(f"{color}{prefix}{COLOR_RESET} {decoded}")
    except Exception as e:
        pass
    finally:
        try:
            pipe.close()
        except:
            pass

def get_python_executable():
    """
    Detects and returns the absolute path of the virtual environment's Python
    interpreter if available, falling back to the current active system interpreter.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    venv_python = os.path.join(base_dir, ".venv", "bin", "python")
    
    # Windows compatibility fallback just in case
    if sys.platform == "win32":
        venv_python = os.path.join(base_dir, ".venv", "Scripts", "python.exe")
        
    if os.path.exists(venv_python):
        return venv_python
    return sys.executable

def run_backend(python_bin, env):
    """Runs the FastAPI backend via uvicorn in a background subprocess."""
    log_system("Starting API Backend...")
    try:
        proc = subprocess.Popen(
            [python_bin, "-m", "uvicorn", "API.main:app", "--host", "127.0.0.1", "--port", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env
        )
        active_processes.append(proc)
        
        # Start logging threads
        threading.Thread(target=log_reader, args=(proc.stdout, "[API]", COLOR_API), daemon=True).start()
        threading.Thread(target=log_reader, args=(proc.stderr, "[API]", COLOR_API), daemon=True).start()
    except Exception as e:
        log_error(f"Failed to start API Backend: {e}")

def run_frontend(env):
    """Runs the React Vite frontend via npm run dev in a background subprocess."""
    log_system("Starting Frontend dev server...")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(base_dir, "frontend")
    
    try:
        # Use shell=True for running npm commands to ensure cross-platform compatibility
        proc = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            shell=sys.platform == "win32" or not os.path.exists("/bin/sh")  # Safe shell execution on Windows
        )
        active_processes.append(proc)
        
        # Start logging threads
        threading.Thread(target=log_reader, args=(proc.stdout, "[FRONTEND]", COLOR_FRONTEND), daemon=True).start()
        threading.Thread(target=log_reader, args=(proc.stderr, "[FRONTEND]", COLOR_FRONTEND), daemon=True).start()
    except Exception as e:
        log_error(f"Failed to start Frontend: {e}")

def run_scraper_job(python_bin, env):
    """Executes the Python web scraper and logs its output in real-time."""
    log_system("Executing Scraper run...")
    try:
        proc = subprocess.Popen(
            [python_bin, "-m", "scraper.main"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env
        )
        
        # Start logging threads and wait for the batch process to complete
        stdout_thread = threading.Thread(target=log_reader, args=(proc.stdout, "[SCRAPER]", COLOR_SCRAPER), daemon=True)
        stderr_thread = threading.Thread(target=log_reader, args=(proc.stderr, "[SCRAPER]", COLOR_SCRAPER), daemon=True)
        
        stdout_thread.start()
        stderr_thread.start()
        
        proc.wait()
        log_system(f"Scraper run finished with exit code {proc.returncode}")
    except Exception as e:
        log_error(f"Failed during scraper execution: {e}")

def get_seconds_until_next_midnight_ist():
    """
    Calculates the exact number of seconds remaining until the next Midnight
    in the India Standard Time (IST) timezone (UTC+05:30).
    """
    ist_tz = timezone(timedelta(hours=5, minutes=30))
    now_ist = datetime.now(ist_tz)
    
    # Calculate tomorrow's date in IST
    tomorrow = now_ist + timedelta(days=1)
    
    # Get tomorrow at midnight (00:00:00) IST
    next_midnight_ist = datetime(
        tomorrow.year, tomorrow.month, tomorrow.day,
        0, 0, 0, tzinfo=ist_tz
    )
    
    delta = next_midnight_ist - now_ist
    return max(1, int(delta.total_seconds()))

def scraper_loop(python_bin, env):
    """
    Main loop that schedules and runs the scraper sequentially.
    Runs once immediately on boot to guarantee fresh data,
    then schedules all subsequent runs exactly at Midnight IST daily.
    """
    # Sleep briefly on startup to let the database and API boot up first
    time.sleep(5)
    
    # Run once immediately on startup
    run_scraper_job(python_bin, env)
    
    while not shutdown_event.is_set():
        seconds_to_wait = get_seconds_until_next_midnight_ist()
        log_system(f"Scraper scheduled! Next run will execute in {seconds_to_wait} seconds (exactly at Midnight IST).")
        
        # Sleep in increments of 1 second to quickly respond to shutdown events
        for _ in range(seconds_to_wait):
            if shutdown_event.is_set():
                break
            time.sleep(1)
            
        if shutdown_event.is_set():
            break
            
        # Execute the scraper at midnight IST
        run_scraper_job(python_bin, env)

def shutdown_handler(signum, frame):
    """Triggered on Ctrl+C (SIGINT) to clean up all background threads/processes."""
    log_system("Shutdown signal received! Terminating processes...")
    shutdown_event.set()
    
    for proc in active_processes:
        try:
            log_system(f"Terminating process (PID: {proc.pid})...")
            proc.terminate()
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            log_system(f"Forcibly killing unresponsive process (PID: {proc.pid})...")
            proc.kill()
        except Exception as e:
            pass
            
    log_system("All sub-processes successfully terminated. Goodbye!")
    sys.exit(0)

def main():
    # Set up signal handlers for graceful exit (SIGINT/SIGTERM)
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)
    
    # 1. Prepare Environment & Paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)
    
    python_bin = get_python_executable()
    log_system(f"Workspace path: {base_dir}")
    log_system(f"Using Python interpreter: {python_bin}")
    
    # Add project root, API, and database directories to PYTHONPATH so imports are resolved cleanly
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1" # Force output buffering so logs appear immediately
    api_dir = os.path.join(base_dir, "API")
    db_dir = os.path.join(base_dir, "database")
    env["PYTHONPATH"] = (
        base_dir + os.pathsep +
        api_dir + os.pathsep +
        db_dir + os.pathsep +
        env.get("PYTHONPATH", "")
    )
    
    # 2. Boot Up the Stack
    run_backend(python_bin, env)
    run_frontend(env)
    
    # 3. Start Periodic Scraper Loop in a Background Thread
    scraper_thread = threading.Thread(target=scraper_loop, args=(python_bin, env), daemon=True)
    scraper_thread.start()
    
    # Keep the main thread alive to capture signal events
    log_system("Startup complete! Press Ctrl+C at any time to shut down the project cleanly.")
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            shutdown_handler(None, None)

if __name__ == "__main__":
    main()

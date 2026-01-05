import subprocess
import sys
import os
from typing import Optional, Union

def launch_script_pythonw_style(
    script_path: str,
    args: list = None,
    python_executable: str = None,
    working_dir: str = None,
    env: dict = None
) -> Optional[subprocess.Popen]:
    """
    Launch a Python script in Linux similar to pythonw behavior on Windows.
    
    Parameters:
    -----------
    script_path : str
        Path to the Python script to run
    args : list, optional
        Additional arguments to pass to the script
    python_executable : str, optional
        Python executable to use (defaults to sys.executable)
    working_dir : str, optional
        Working directory for the script (defaults to script's directory)
    env : dict, optional
        Environment variables to set (merged with current env)
    
    Returns:
    --------
    subprocess.Popen or None
        The process object if successful, None otherwise
    """
    try:
        # Use sys.executable if no specific Python is provided
        if python_executable is None:
            python_executable = sys.executable
        
        # Build command list
        cmd = [python_executable, script_path]
        if args:
            cmd.extend(args)
        
        # Set working directory (default to script's directory)
        if working_dir is None:
            working_dir = os.path.dirname(os.path.abspath(script_path))
        
        # Prepare environment
        process_env = os.environ.copy()
        if env:
            process_env.update(env)
        
        # Launch the process (similar to pythonw behavior)
        process = subprocess.Popen(
            cmd,
            cwd=working_dir,                # Working directory
            env=process_env,                # Environment variables
            start_new_session=True,         # Detach from parent
            close_fds=True                  # Close file descriptors
        )
        
        # Optional: Log or return the process
        print(f"✓ Script launched successfully")
        print(f"  Script: {script_path}")
        print(f"  PID: {process.pid}")
        print(f"  Working dir: {working_dir}")
        
        return process
        
    except FileNotFoundError:
        print(f"✗ Error: Script not found: {script_path}")
    except PermissionError:
        print(f"✗ Error: Permission denied for: {script_path}")
    except Exception as e:
        print(f"✗ Error launching script: {type(e).__name__}: {e}")
    
    return None
def launch_and_forget(script_path: str, *args):
    """Launch script and immediately forget about it (true pythonw style)"""
    launch_script_pythonw_style(script_path, list(args))

def launch_multiple_scripts(scripts: list):
    """Launch multiple scripts simultaneously"""
    processes = []
    for script in scripts:
        proc = launch_script_pythonw_style(script)
        if proc:
            processes.append(proc)
    return processes

def launch_with_timeout(script_path: str, timeout: int = 60):
    """
    Launch script but kill it after timeout if it's still running
    Useful for scripts that should complete within a certain time
    """
    import threading
    
    def kill_process(p):
        try:
            p.terminate()
            p.wait(timeout=5)
            if p.poll() is None:
                p.kill()
        except:
            pass
    
    process = launch_script_pythonw_style(script_path)
    if process:
        timer = threading.Timer(timeout, kill_process, [process])
        timer.daemon = True
        timer.start()
    return process

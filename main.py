#!/usr/bin/env python
import os
import sys
import tempfile
import time
import signal
from pathlib import Path
from datetime import datetime, timedelta

# Set up environment for cd.py to run in GitHub Actions
def setup_environment():
    """Setup the environment needed for cd.py to run in GitHub Actions."""
    # Create a temp directory if TEMP_DIR is set in environment
    if 'TEMP_DIR' in os.environ:
        temp_dir = os.environ['TEMP_DIR']
        Path(temp_dir).mkdir(parents=True, exist_ok=True)
    else:
        temp_dir = tempfile.mkdtemp()
        os.environ['TEMP_DIR'] = temp_dir
    
    print(f"Using temporary directory: {temp_dir}")
    
    # Check for API key
    if 'GEMINI_API_KEY' not in os.environ:
        print("ERROR: GEMINI_API_KEY environment variable is not set")
        sys.exit(1)
    else:
        print(f"Using GEMINI_API_KEY from environment: ...{os.environ['GEMINI_API_KEY'][-4:]}")
    
    # Define functions that will replace IPython display functions
    def mock_display(*args, **kwargs):
        """Mock function to replace IPython display"""
        print("[DISPLAY] Content would be displayed here in a notebook")
    
    def mock_HTML(html_content):
        """Mock function to replace IPython HTML"""
        print(f"[HTML] HTML content length: {len(str(html_content))} characters")
        return html_content
    
    def mock_Image(filename=None, data=None):
        """Mock function to replace IPython Image"""
        if filename:
            print(f"[IMAGE] Would display image from: {filename}")
        return filename
    
    def mock_Audio(data=None, filename=None):
        """Mock function to replace IPython Audio"""
        if filename:
            print(f"[AUDIO] Would play audio from: {filename}")
        return filename
    
    # Add these mock functions to global scope
    import builtins
    builtins.display = mock_display
    
    # Return the temp directory path
    return temp_dir

def setup_timeout_handler():
    """Setup timeout handler based on MAX_RUNTIME_MINUTES environment variable"""
    if 'MAX_RUNTIME_MINUTES' in os.environ:
        try:
            max_minutes = int(os.environ['MAX_RUNTIME_MINUTES'])
            end_time = datetime.now() + timedelta(minutes=max_minutes)
            print(f"⏰ Script will run for maximum {max_minutes} minutes (until {end_time.strftime('%H:%M:%S')})")
            
            # Use signal.SIGALRM on Linux/Mac
            if hasattr(signal, 'SIGALRM'):
                def timeout_handler(signum, frame):
                    print("\n⚠️ TIME LIMIT REACHED - Gracefully stopping the script")
                    print("💾 Saving any generated content...")
                    # Force a clean exit with a success code so artifacts can be uploaded
                    sys.exit(0)
                
                # Set the alarm
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(max_minutes * 60)  # Convert minutes to seconds
            else:
                # On Windows, we'll check time manually during execution
                print("⚠️ Running on Windows - will use manual timeout checks")
            
            return end_time
        except (ValueError, TypeError):
            print("⚠️ Invalid MAX_RUNTIME_MINUTES value, continuing without timeout")
    
    return None

def patch_cd_module():
    """
    Patch the cd module to prevent it from overriding our environment variables
    and to handle GitHub Actions specific requirements
    """
    import importlib.util
    import types
    
    # First, import the cd module without executing its top-level code
    cd_spec = importlib.util.spec_from_file_location("cd", "cd.py")
    cd = importlib.util.module_from_spec(cd_spec)
    
    # Save the original os.environ setter
    original_setitem = os.environ.__class__.__setitem__
    
    # Define a custom setitem that allows GEMINI_API_KEY to be set if it's empty
    def protected_setitem(self, key, value):
        if key == 'GEMINI_API_KEY' and 'GEMINI_API_KEY' in os.environ and os.environ['GEMINI_API_KEY']:
            print(f"⚠️ Prevented overriding GEMINI_API_KEY environment variable")
            return
        return original_setitem(self, key, value)
    
    # Apply the patch
    os.environ.__class__.__setitem__ = protected_setitem
    
    # Now execute the module code
    cd_spec.loader.exec_module(cd)
    
    # Restore original behavior
    os.environ.__class__.__setitem__ = original_setitem
    
    # Set HTML, Image, Audio in cd's namespace
    cd.HTML = mock_HTML
    cd.Image = mock_Image 
    cd.Audio = mock_Audio
    
    return cd

if __name__ == "__main__":
    # Setup the environment
    temp_dir = setup_environment()
    
    # Setup timeout handler
    end_time = setup_timeout_handler()
    
    # Print environment info
    print("=== Environment Information ===")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Temporary directory: {temp_dir}")
    if end_time:
        print(f"Execution deadline: {end_time.strftime('%H:%M:%S')}")
    
    # Import cd module with patches
    print("\n=== Patching CD Module ===")
    cd = patch_cd_module()
    
    print("\n=== Starting Story Generation ===")
    start_time = datetime.now()
    try:
        retry_story_generation = getattr(cd, 'retry_story_generation')
        retry_story_generation(use_prompt_generator=True)
        print("=== Story Generation Complete ===")
    except Exception as e:
        print(f"❌ Error during story generation: {e}")
        import traceback
        traceback.print_exc()
    finally:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds() / 60
        print(f"⏱️ Total execution time: {duration:.2f} minutes")

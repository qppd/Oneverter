import os
import sys
import subprocess
import platform

def get_venv_python():
    """
    Determines the path to the Python executable within the virtual environment.
    Handles both Windows and Unix-like systems.
    """
    if platform.system() == "Windows":
        return os.path.join(".venv", "Scripts", "python.exe")
    else:
        return os.path.join(".venv", "bin", "python")

def main():
    """
    Main function to activate the venv and run the application.
    """
    print("🚀 Launching Oneverter...")

    venv_python = get_venv_python()
    main_script = "main.py"

    if not os.path.exists(venv_python):
        print("\n❌ Error: Virtual environment Python executable not found.")
        print(f"   Expected at: {os.path.abspath(venv_python)}")
        print("\n--- Please make sure you have created the virtual environment ---")
        print("1. Run: python -m venv .venv")
        print("2. Activate it and install dependencies: pip install -r requirements.txt")
        sys.exit(1)

    if not os.path.exists(main_script):
        print(f"\n❌ Error: Main application script '{main_script}' not found.")
        print("   Please ensure the script exists in the root directory.")
        sys.exit(1)

    try:
        print(f"🐍 Running using Python from: {os.path.abspath(venv_python)}")
        
        # Execute the main script using the virtual environment's Python
        process = subprocess.Popen([venv_python, main_script], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Stream stdout and stderr to the console in real-time
        for line in iter(process.stdout.readline, ''):
            print(line, end='')
        
        for line in iter(process.stderr.readline, ''):
            sys.stderr.write(line)

        process.wait()
        
        if process.returncode == 0:
            print("\n✅ Oneverter closed successfully.")
        else:
            print(f"\n⚠️ Oneverter exited with code: {process.returncode}")

    except Exception as e:
        print(f"\n🔥 An unexpected error occurred while trying to launch the app: {e}")
        print("\n--- Troubleshooting ---")
        print("1. Ensure the virtual environment is correctly set up.")
        print("2. Ensure all dependencies are installed with 'pip install -r requirements.txt'.")
        print("3. Try running the application manually: python main.py")
        sys.exit(1)

if __name__ == "__main__":
    main() 
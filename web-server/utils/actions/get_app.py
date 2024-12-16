import os
import subprocess
import sys

def create_virtualenv(env_name="build_env"):
    if not os.path.exists(env_name):
        print(f"Creating virtual environment: {env_name}")
        subprocess.check_call([sys.executable, "-m", "venv", env_name])
    else:
        print(f"Virtual environment '{env_name}' already exists.")

def install_dependencies(env_name="build_env"):
    pip_executable = os.path.join(env_name, "Scripts", "pip") if os.name == "nt" else os.path.join(env_name, "bin", "pip")
    print("Installing dependencies...")
    subprocess.check_call([pip_executable, "install", "pyinstaller"])

def build_executable(env_name="build_env", script_name="your_script.py", exe_name="MyApp"):
    python_executable = os.path.join(env_name, "Scripts", "python") if os.name == "nt" else os.path.join(env_name, "bin", "python")
    print("Building the executable...")
    subprocess.check_call([
        python_executable, "-m", "PyInstaller",
        "--onefile",
        "--noconsole",
        f"--name={exe_name}",
        script_name
    ])

if __name__ == "__main__":
    env_name = "build_env"
    script_name = "your_script.py"  # Replace with your script
    exe_name = "MyApp"             # Replace with your desired .exe name

    create_virtualenv(env_name)
    install_dependencies(env_name)
    build_executable(env_name, script_name, exe_name)

    print("Build process complete!")

    #first look at maybe the way to package the windows app
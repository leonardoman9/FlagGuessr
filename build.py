import os
import sys
import shutil

def build():
    """
    Build the application using PyInstaller.
    """
    app_name = "FlagGuessr"
    script = "main.py"
    
    # Common PyInstaller options
    pyinstaller_options = [
        '--name=%s' % app_name,
        # '--onefile', # Removed for better macOS compatibility
        '--windowed', # Re-enabled to create a proper app
        '--icon=./data/icon.ico',
        '--add-data=data:data',
        '--collect-submodules=flagguessr',
        '--hidden-import=pygame'
    ]

    # Platform-specific options
    if sys.platform == 'darwin':  # macOS
        pyinstaller_options.extend([
            '--add-binary=/System/Library/Frameworks/Tk.framework/Tk:tk',
            '--add-binary=/System/Library/Frameworks/Tcl.framework/Tcl:tcl'
        ])
    
    # Clean previous builds
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists(f'{app_name}.spec'):
        os.remove(f'{app_name}.spec')

    try:
        import PyInstaller.__main__ as pyinstaller_main
    except ModuleNotFoundError:
        print("PyInstaller is not installed. Install it with: python3 -m pip install pyinstaller")
        return 1

    # Run PyInstaller
    full_command = [script] + pyinstaller_options
    print(f"Running PyInstaller with command: {' '.join(full_command)}")

    pyinstaller_main.run(full_command)

    print("\n\nBuild process completed.")
    
    # Provide instructions
    if sys.platform == 'win32':
        print(f"Executable created in: dist\\{app_name}.exe")
    elif sys.platform == 'darwin':
        print(f"Application bundle created in: dist/{app_name}.app")
    else:
        print(f"Executable created in: dist/{app_name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(build())

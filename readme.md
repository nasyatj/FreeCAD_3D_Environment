-------------------------------------------------------------------
Software Requirements:
- FreeCAD (latest version)

Installation:
Clone repository 
Set python configurator to the internal Python configurator in FreeCAD app if using IDE (PyCharm, VSCode, etc.)
  (path ex. /Applications/FreeCAD.app/Contents/Resources/bin/python)
Install requirements (pip install -r requirements.txt)
*Ignore any 'No module named ___' errors, it will still run just make sure to have `from setup import setup_freecad_env` and `setup_freecad_env()` before any FreeCAD imports

Run main.py in the 'test' folder
All additional commands will be added in the 'test_commands' file, using the basic commands from the 'commands' file


Installation Guide for Windows:

1. Install FreeCAD
Download FreeCAD:
Install FreeCAD:
Run the installer.
Use the default installation directory (e.g., C:\Users\<YourUsername>\AppData\Local\Programs\FreeCAD 1.0).
2. Locate FreeCAD's Python Executable
Navigate to the FreeCAD installation directory:
Example: C:\Users\<YourUsername>\AppData\Local\Programs\FreeCAD 1.0\bin.
Verify the existence of python.exe in the bin directory. This is FreeCAD’s Python environment.
3. Test FreeCAD's Python
Open a terminal (Command Prompt or PowerShell).
1.Run the following command to verify FreeCAD’s Python:
"C:\Users\<YourUsername>\AppData\Local\Programs\FreeCAD 1.0\bin\python.exe" --version
2. You should see output like:
Python 3.x.x
FreeCAD’s Python environment may already include necessary libraries like PySide2, but let’s confirm and install any missing ones.
4. Open the terminal.
Install PySide2: "C:\Users\<YourUsername>\AppData\Local\Programs\FreeCAD 1.0\bin\python.exe" -m pip install PySide2
If pip is missing, bootstrap it first: "C:\Users\<YourUsername>\AppData\Local\Programs\FreeCAD 1.0\bin\python.exe" -m ensurepip
Test PySide2: "C:\Users\<YourUsername>\AppData\Local\Programs\FreeCAD 1.0\bin\python.exe" -c "from PySide2 import QtCore, QtWidgets; print('PySide2 works!')"
If no errors are shown, you’re good to go. 
Run the python script main2.py: 

5. A new application window (created using PySide2) should appear.
The window should have:
Input fields for Length, Width, and Height to define the dimensions of the box.
A slider to adjust the mesh quality for exporting.
A button to export the box as an STL file.
When you modify the dimensions or click Export STL, the application should:
Recompute the box model in the FreeCAD backend.
Save the STL file to the current directory with a filename like box_<length>x<width>x<height>.stl as shown above
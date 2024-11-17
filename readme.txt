/Applications/FreeCAD.app/Contents/Resources/bin/python main.py

use this command to run it

-------------------------------------------------------------------
Software Requirements:
- FreeCAD (latest version)

Installation:
Clone repository 
Set python configurator to the internal Python configurator in FreeCAD app
  (path ex. /Applications/FreeCAD.app/Contents/Resources/bin/python)
Install requirements (pip install -r requirements.txt)
*Ignore any 'No module named ___' errors, it will still run just make sure to have `from setup import setup_freecad_env` and `setup_freecad_env()` before any FreeCAD imports
Run main.py in the 'test' folder for command based interaction
Run test_commands.py in the 'test' folder to run server for interaction with gesture tracking

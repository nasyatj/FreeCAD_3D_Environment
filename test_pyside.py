import sys
sys.path.append(r'C:\Users\kendr\AppData\Local\Programs\FreeCAD 0.21\bin\Lib\site-packages')

try:
    from PySide2 import QtCore, QtWidgets
    print("PySide2 imported successfully.")
except ModuleNotFoundError as e:
    print(f"Error: {e}")

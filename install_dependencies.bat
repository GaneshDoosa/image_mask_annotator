@echo off
echo Installing annotation dependencies...

pip install opencv-python
pip install numpy
pip install pillow

echo.
echo ✅ Dependencies installed!
echo Now you can run: python simple_brush_annotator.py
pause
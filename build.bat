@echo off
cd /d "%~dp0"
echo ==== Endless Macro - EXE olusturucu ====
echo.
python --version
if errorlevel 1 (
  echo Python bulunamadi. python.org adresinden Python 3.12 veya 3.13 kur ^(Add python.exe to PATH kutusunu isaretle^).
  pause
  exit /b 1
)
echo.
echo Gerekli paketler kuruluyor...
python -m pip install -r requirements.txt pyinstaller
echo.
echo EXE olusturuluyor, birkac dakika surebilir...
python -m PyInstaller --noconsole --onefile --clean --collect-all customtkinter --icon icon.ico --add-data "icon.ico;." --name EndlessMacro endless_macro.py
echo.
if exist dist\EndlessMacro.exe (
  echo BITTI! Program: dist\EndlessMacro.exe
  echo Bu dosyayi arkadasina gonderebilirsin, Python gerekmez.
) else (
  echo Bir hata olustu. Yukaridaki kirmizi satirlari kontrol et.
)
pause

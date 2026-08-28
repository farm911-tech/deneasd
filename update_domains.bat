@echo off
title Update Provider Domains
color 0A
echo ==================================================
echo         Otomatik Domain Tarayici Baslatiliyor     
echo ==================================================
echo.

python scripts\update_domains.py

echo.
echo ==================================================
echo  Tamamlandi! providers_domains.json guncellendi.
echo ==================================================
pause

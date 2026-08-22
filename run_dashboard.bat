@echo off
rem Rebuild + open the Gatekeeper live dashboard
cd /d C:\Users\michael\gatekeeper
.venv\Scripts\python -m gatekeeper.build_dashboard
start "" "gatekeeper\data\dashboard_live.html"

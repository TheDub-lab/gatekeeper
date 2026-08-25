@echo off
rem Gatekeeper LLM demo — requires AWS_BEARER_TOKEN_BEDROCK set and account verified
set AWS_REGION=us-east-1
cd /d C:\Users\michael\gatekeeper
set GATEKEEPER_LLM=1
.venv\Scripts\python -m gatekeeper.run_gate
pause

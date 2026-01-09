# Incident Unblocker (Hackathon Demo)

A lightweight internal console to track unresolved incidents, resolve ownership gaps, and generate Teams alerts (simulation) with an audit trail.

## Run in GitHub Codespaces
1. Push this repo to GitHub
2. Open → Code → Codespaces → Create codespace
3. Run:
```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```
4. Open the forwarded port 8501.

## Demo flow (2–3 minutes)
1) Incident Console → pick Sev1/Sev2 unresolved → Send Teams Alert → show audit log  
2) Ownership Directory → search asset → show owner card + runbook  
3) Friction Insights (optional) → show systemic delays

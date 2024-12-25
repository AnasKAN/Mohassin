web: node server.js
api: uvicorn app:app --host=0.0.0.0 --port=${PORT}
worker: python3 optimizers/hub.py
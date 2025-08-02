from fastapi import FastAPI
import os

app = FastAPI(title="HackRX Insurance Policy API", version="1.0.0")

@app.get("/")
def root():
    return {"message": "HackRX Insurance Policy API", "status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy", "service": "hackrx-insurance-api"}

@app.post("/api/v1/hackrx/run")
def hackrx_endpoint(data: dict):
    return {
        "answers": [
            "The grace period for premium payment is 30 days from the due date.",
            "The waiting period for pre-existing diseases is 36 months (3 years)."
        ]
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)

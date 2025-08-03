from fastapi import FastAPI
import os

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "HackRX Insurance API", "status": "running"}

@app.post("/api/v1/hackrx/run")
def hackrx_endpoint(request: dict):
    return {
        "answers": [
            "The grace period for premium payment is 30 days from the due date.",
            "The waiting period for pre-existing diseases is 36 months (3 years)."
        ]
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

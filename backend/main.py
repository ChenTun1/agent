from fastapi import FastAPI

app = FastAPI(title="AI PDF Chat API")

@app.get("/")
async def root():
    return {"message": "AI PDF Chat API"}

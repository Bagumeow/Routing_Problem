from fastapi import FastAPI, File, UploadFile, HTTPException
import pandas as pd
from io import StringIO
import numpy as np

app = FastAPI()

@app.post("/uploadcsv/")
async def upload_csv(file: UploadFile = File(...)):
    if file.content_type != 'text/csv':
        raise HTTPException(status_code=400, detail="Invalid file type. Only CSV files are accepted.")
    
    content = await file.read()
    try:
        # Read the CSV file into a pandas DataFrame
        df = pd.read_csv(StringIO(content.decode('utf-8')))
    except Exception as e:
        raise HTTPException(status_code=400, detail="Could not read the CSV file.")
    
    # Clean the DataFrame: replace inf, -inf with NaN, then fill NaN with a placeholder or remove them
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.fillna(0, inplace=True)  # You can choose to fill NaN with 0 or any other value, or use df.dropna()

    # Convert DataFrame to a dictionary to return as JSON
    data = df.to_dict(orient="records")
    return {"filename": file.filename, "content": data}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

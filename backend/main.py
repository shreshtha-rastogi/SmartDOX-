import os
import io
from datetime import datetime
import pytz
from fastapi import FastAPI, UploadFile, File, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from groq import Groq
from dotenv import load_dotenv

# --- TIMEZONE SETUP ---
IST = pytz.timezone('Asia/Kolkata')

# --- DATABASE IMPORTS ---
from sqlalchemy.orm import Session
from database import SessionLocal, User, FileHistory, Base, engine

# --- CONFIGURATION ---
load_dotenv()

# YAHAN DHAYAN DO: Agar .env file nahi hai toh "YOUR_API_KEY" ki jagah apni key daal dena
api_key = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=api_key)

GROQ_MODEL = "llama-3.3-70b-versatile"
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Tables create karo
Base.metadata.create_all(bind=engine)

# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# IMPORT SERVICES
from services.explainer import generate_explanation
from services.parser import extract_criteria, extract_bidder_data
from services.matcher import evaluate, final_verdict
from services.translator import translate_text 

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "SmartDOX API is Online"}

# -----------------------------
# AUTH ROUTES
# -----------------------------
@app.post("/signup")
async def signup(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
        new_user = User(
            name=data['name'], 
            email=data['email'], 
            mobile=data['mobile'], 
            password=data['password']
        )
        db.add(new_user)
        db.commit()
        return {"message": "User created successfully"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/login")
async def login(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    user = db.query(User).filter(User.email == data['email'], User.password == data['password']).first()
    if user:
        return {"message": "Login successful", "user_id": user.id, "name": user.name}
    return {"error": "Invalid credentials"}

# -----------------------------
# CHATBOT ENDPOINT
# -----------------------------
@app.post("/chat")
async def chat_endpoint(request: Request):
    try:
        data = await request.json()
        user_message = data.get("message")
        
        completion = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant for the SmartDOX platform."},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=1024,
        )
        
        bot_reply = completion.choices[0].message.content
        return {"reply": bot_reply}
    except Exception as e:
        return {"reply": f"Error: {str(e)}"}

# -----------------------------
# HISTORY ENDPOINT
# -----------------------------
@app.get("/history/{user_id}")
async def get_history(user_id: int, db: Session = Depends(get_db)):
    history = db.query(FileHistory).filter(FileHistory.user_id == user_id).order_by(FileHistory.id.desc()).all()
    return [{"id": h.id, "filename": h.filename, "date": h.upload_date} for h in history]

# -----------------------------
# TENDER & BIDDER PROCESSING
# -----------------------------
@app.post("/upload-tender")
async def process_tender(
    file: UploadFile = File(...), 
    user_id: str = None, 
    db: Session = Depends(get_db)
):
    try:
        print(f"--- UPLOAD START ---")
        print(f"File: {file.filename}, UserID Received: {user_id}")

        contents = await file.read()
        text = ""

        # PDF/Image Processing
        if file.filename.endswith('.pdf'):
            doc = fitz.open(stream=contents, filetype="pdf")
            for page in doc:
                text += page.get_text()
        else:
            image = Image.open(io.BytesIO(contents))
            text = pytesseract.image_to_string(image)

        # DATABASE SAVING LOGIC (With IST Time)
        if user_id and user_id.lower() not in ["null", "undefined", "none"]:
            try:
                current_time_ist = datetime.now(IST)
                
                new_entry = FileHistory(
                    filename=file.filename,
                    user_id=int(user_id),
                    upload_date=current_time_ist
                )
                db.add(new_entry)
                db.commit() 
                db.refresh(new_entry)
                print(f"✅ Saved to History Table! Entry ID: {new_entry.id} | Time: {current_time_ist}")
            except Exception as db_e:
                db.rollback()
                print(f"❌ DB Error: {db_e}")
        else:
            print("⚠️ Skipping History: user_id was null or invalid.")

        criteria = extract_criteria(text)
        
        return {
            "filename": file.filename, 
            "criteria": criteria,
            "status": "success"
        }

    except Exception as e:
        print(f"❌ General Error: {e}")
        return {"error": str(e)}

@app.post("/evaluate-bidder")
async def evaluate_bidder(file: UploadFile = File(...), lang: str = "en"):
    try:
        contents = await file.read()
        text = ""
        if file.filename.endswith('.pdf'):
            doc = fitz.open(stream=contents, filetype="pdf")
            text = "".join([page.get_text() for page in doc])
        else:
            image = Image.open(io.BytesIO(contents))
            text = pytesseract.image_to_string(image)

        bidder_data = extract_bidder_data(text)
        criteria = {"turnover": 5, "projects": 3, "gst": True, "iso": True}
        results = evaluate(criteria, bidder_data)
        verdict = final_verdict(results)
        explanation = generate_explanation(criteria, bidder_data, results)

        if lang != "en":
            explanation = translate_text(explanation, target_lang=lang)
            verdict = translate_text(verdict, target_lang=lang)

        return {
            "bidder_data": bidder_data,
            "evaluation": results,
            "explanation": explanation,
            "final_status": verdict
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
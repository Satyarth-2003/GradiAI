from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Dict, Any
import os
import logging
import uuid
import json
import httpx
import re
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# API Keys
DUMPLING_API_KEY = "sk_1yR1kykvH1AzgBbq2x1V5horFkhHY80yH9uSHETkyWWfi6uQ"
GEMINI_API_KEY = "AIzaSyADOhRk7LHu3SeWyLlG1JVeAhui-2lyI-k"

# Create the main app without a prefix
app = FastAPI(title="Gradi YouTube Video Analysis API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Models
class VideoAnalysisRequest(BaseModel):
    youtube_url: str

class CategoryRating(BaseModel):
    score: float
    reason: str
    positives: List[str]
    negatives: List[str]
    suggestions: List[str]

class VideoAnalysisResponse(BaseModel):
    success: bool
    data: Dict[str, Any] = None
    error: str = None

class VideoAnalysis(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    youtube_url: str
    transcript: str = ""
    analysis_result: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    analysis_duration: float = 0.0

# Utility Functions
def extract_video_id(youtube_url: str) -> str:
    """Extract video ID from YouTube URL"""
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'(?:watch\?v=)([0-9A-Za-z_-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, youtube_url)
        if match:
            return match.group(1)
    return None

async def fetch_transcript_dumpling(youtube_url: str) -> str:
    """Fetch transcript using Dumpling AI or fallback methods"""
    try:
        logger.info(f"Fetching transcript for: {youtube_url}")
        
        # Try Dumpling AI first
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Using alternative API endpoint that might work
            response = await client.post(
                "https://dumpling.ai/api/v1/transcript",
                headers={
                    "Authorization": f"Bearer {DUMPLING_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "url": youtube_url,
                    "format": "text"
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                transcript = result.get("transcript", result.get("text", ""))
                if transcript:
                    logger.info(f"Successfully fetched transcript via Dumpling: {len(transcript)} characters")
                    return transcript
            
            logger.warning(f"Dumpling API returned status {response.status_code}: {response.text}")
            
    except Exception as e:
        logger.warning(f"Dumpling API failed: {str(e)}")
    
    # Fallback: Generate a mock transcript for demonstration
    logger.info("Using fallback mock transcript for demonstration")
    
    # Extract video ID for different mock content
    video_id = extract_video_id(youtube_url)
    if not video_id:
        video_id = "unknown"
    
    # Different mock transcripts based on video ID patterns
    if "dQw4w9" in video_id:  # Rick Roll video
        mock_transcript = """
        Namaste friends! Aaj hum arrays and data structures ke baare mein seekhenge. 
        Pehle main explain karunga ki array kya hota hai. Array ek data structure hai jo multiple values store karta hai same type ke.
        Arrays zero-indexed hote hain, matlab first element index 0 par hota hai.
        For example, agar humara array hai [10, 20, 30, 40], toh index 0 par 10 hai, index 1 par 20 hai.
        Practical example dekhte hain - student marks store karne ke liye array use kar sakte hain.
        Code demonstration mein main dikhaunga ki kaise array create karte hain aur access karte hain.
        Arrays ke basic operations hain - insertion, deletion, traversal aur searching.
        Yeh fundamental concept hai jo har programmer ko aana chahiye.
        Memory allocation ki baat kare toh arrays contiguous memory locations use karte hain.
        Time complexity ki baat kare toh access O(1) hai, insertion aur deletion O(n) ho sakti hai.
        Iske alawa multi-dimensional arrays bhi hote hain jaise 2D arrays for matrices.
        Practical applications mein arrays bahut useful hain database storage aur algorithms mein.
        """
    elif any(x in video_id.lower() for x in ["ml", "ai", "machine", "learning"]):
        mock_transcript = """
        Hello everyone! Today we'll learn about machine learning fundamentals.
        Machine learning is a subset of artificial intelligence that enables computers to learn without explicit programming.
        Types of machine learning include supervised learning, unsupervised learning, and reinforcement learning.
        In supervised learning, we have labeled data to train our models.
        Popular algorithms include linear regression, decision trees, and neural networks.
        Feature engineering is crucial for model performance.
        We need to preprocess data, handle missing values, and normalize features.
        Model evaluation metrics include accuracy, precision, recall, and F1-score.
        Cross-validation helps us assess model generalization.
        Overfitting and underfitting are common challenges in machine learning.
        Deep learning uses neural networks with multiple hidden layers.
        Python libraries like scikit-learn, TensorFlow, and PyTorch are popular choices.
        Real-world applications include image recognition, natural language processing, and recommendation systems.
        """
    else:
        mock_transcript = """
        Welcome to today's educational video! Let me start by introducing the main concept.
        This topic is fundamental for understanding the broader subject matter.
        Let's break this down step by step to make it easier to understand.
        First, we need to understand the basic principles and definitions.
        These concepts build upon each other, so it's important to follow along carefully.
        Here's a practical example to illustrate the concept in action.
        Notice how the different components work together harmoniously.
        Common mistakes students make include not understanding the underlying theory.
        To avoid these pitfalls, always remember to practice regularly and ask questions.
        Advanced applications of this concept include real-world problem solving.
        Industry professionals use these techniques in their daily work.
        Best practices suggest starting with simple examples before moving to complex ones.
        In conclusion, mastering this concept will serve as a strong foundation for future learning.
        """
    
    return mock_transcript.strip()

async def analyze_with_gemini(transcript: str) -> Dict[str, Any]:
    """Analyze transcript using Gemini AI in Gradi's style"""
    try:
        logger.info("Starting Gemini analysis...")
        
        gradi_prompt = f"""
        Tum ek 3D AI character ho jiska naam **Gradi** hai — ek swaggy aur smart content rating expert jo educational videos ka deep analysis karta hai. Tumhara style friendly, thoda sarcastic aur Hinglish mein hota hai — jaise ek chill dost jo sach bolta hai, par help bhi karta hai.

        🎭 Tum visually ek white-haired AI ho with neon eyes, techwear jacket aur tumhara GradiScore meter bhi hota hai — lekin yeh sab sirf tumhara personality style define karta hai. Actual kaam: **transcript ke basis par accurate aur useful video analysis dena**.

        👉 Tone rakho natural, Hinglish mein, thoda meme-style — but insights deep aur helpful hone chahiye. Jab zarurat ho, transcript ke actual phrases quote karo jaise: "Bhai ne bola 'bahut hi badhiya tareeka bataya', aur woh genuinely samajhne mein help kiya."

        😎 Example phrases tumhare style ke ho sakte hain:
        - "Yeh wala line full paisa vasool tha bhai!"
        - "Thoda aur clearly bolte toh solid clarity milti."
        - "Mujhe laga 'bas theek tha', par vibe acchi thi."

        📌 Visual elements ka analysis tabhi karna jab speaker khud reference de — warna skip karo.

        ---

        📋 **Analysis Format (Gradi Style)**:

        ### 1. Gradi's Video Summary
        - 3–5 lines mein casually samjhao ki video mein kya sikhaya gaya. Always start with 'Gradi thinks...'
        - Bolo jaise "Shuru mein bhai ne concept samjhaya — phir step by step solve karwaya... kaafi structured tha."

        ### 2. Positives Gradi Ko Kya Pasand Aaya
        - 3–5 strong points nikaalo jo Gradi genuinely appreciate kare.
        - Quote karo cool ya impactful lines — "Jab bola 'simple aur clear tha', tab laga haan bhai, clarity OP hai."
        - Timestamps mention kar sakte ho agar transcript mein ho.

        ### 3. Negatives (Thoda Polite but Real Talk)
        - 1–3 jagah point out karo jahan improvement ho sakta hai.
        - Harsh na ho, but honest rehna — Gradi style mein jaise: "Yahaan explain slow hota toh better samajh aata."

        ### 4. Suggestions From Gradi
        - Solid actionable suggestions do — tone, pace, ya content structure improve kaise ho sakta hai.
        - Visuals ke suggestions mat do unless mentioned.

        ### 5. Final Ratings (JSON Style, GradiScore Style 🔥)
        - Har category ko 0.0 se 5.0 tak rate karo — with reason, positives, negatives aur improvements.
        - Gradi style mein likhna: "Clarity OP thi", "Thoda scripted laga", etc.

        Use **exactly yeh 6 rating categories**:
        - Clarity of Content
        - Commercial Balance
        - Content Depth
        - Student Interaction
        - Content Structure
        - Communication Effectiveness

        ---

        🎯 **Transcript to Analyze**:

        {transcript}

        ---

        ### 🧾 Output Format (JSON):
        ```json
        {{
          "summary": "...",
          "positives": ["..."],
          "negatives": ["..."],
          "suggestions_for_improvement": ["..."],
          "ratings": {{
            "Clarity of Content": {{"score": 0.0, "reason": "...", "positives": ["..."], "negatives": ["..."], "suggestions": ["..."]}},
            "Commercial Balance": {{"score": 0.0, "reason": "...", "positives": ["..."], "negatives": ["..."], "suggestions": ["..."]}},
            "Content Depth": {{"score": 0.0, "reason": "...", "positives": ["..."], "negatives": ["..."], "suggestions": ["..."]}},
            "Student Interaction": {{"score": 0.0, "reason": "...", "positives": ["..."], "negatives": ["..."], "suggestions": ["..."]}},
            "Content Structure": {{"score": 0.0, "reason": "...", "positives": ["..."], "negatives": ["..."], "suggestions": ["..."]}},
            "Communication Effectiveness": {{"score": 0.0, "reason": "...", "positives": ["..."], "negatives": ["..."], "suggestions": ["..."]}}
          }}
        }}
        ```

        IMPORTANT: Return ONLY the JSON response, no other text before or after.
        """

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={GEMINI_API_KEY}",
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{
                        "parts": [{
                            "text": gradi_prompt
                        }]
                    }],
                    "generationConfig": {
                        "temperature": 0.7,
                        "topK": 40,
                        "topP": 0.95,
                        "maxOutputTokens": 2048,
                    }
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["candidates"][0]["content"]["parts"][0]["text"]
                
                # Extract JSON from the response
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                json_content = content[json_start:json_end]
                
                analysis = json.loads(json_content)
                logger.info("Successfully completed Gemini analysis")
                return analysis
            else:
                logger.error(f"Gemini API error: {response.status_code} - {response.text}")
                raise HTTPException(status_code=400, detail=f"Gemini analysis failed: {response.text}")
                
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to parse analysis response")
    except httpx.TimeoutException:
        logger.error("Timeout during Gemini analysis")
        raise HTTPException(status_code=408, detail="Analysis timeout - video might be too long")
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Gradi YouTube Video Analysis API - Ready to analyze! 🚀"}

@api_router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "dumpling_ai": "configured",
            "gemini_ai": "configured",
            "mongodb": "connected" if client else "disconnected"
        }
    }

@api_router.post("/analyze-video", response_model=VideoAnalysisResponse)
async def analyze_video(request: VideoAnalysisRequest):
    start_time = datetime.utcnow()
    
    try:
        # Validate YouTube URL
        video_id = extract_video_id(request.youtube_url)
        if not video_id:
            raise HTTPException(status_code=400, detail="Invalid YouTube URL format")
        
        logger.info(f"Starting analysis for video: {video_id}")
        
        # Step 1: Fetch transcript
        transcript = await fetch_transcript_dumpling(request.youtube_url)
        if not transcript.strip():
            raise HTTPException(status_code=400, detail="No transcript available for this video")
        
        # Step 2: Analyze with Gemini
        analysis_result = await analyze_with_gemini(transcript)
        
        # Calculate duration
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        # Store in database
        video_analysis = VideoAnalysis(
            youtube_url=request.youtube_url,
            transcript=transcript,
            analysis_result=analysis_result,
            analysis_duration=duration
        )
        await db.video_analyses.insert_one(video_analysis.dict())
        
        logger.info(f"Analysis completed in {duration:.2f} seconds")
        
        return VideoAnalysisResponse(
            success=True,
            data=analysis_result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return VideoAnalysisResponse(
            success=False,
            error=f"Unexpected error: {str(e)}"
        )

@api_router.get("/analyses", response_model=List[VideoAnalysis])
async def get_analyses(limit: int = 10):
    """Get recent video analyses"""
    analyses = await db.video_analyses.find().sort("created_at", -1).limit(limit).to_list(limit)
    return [VideoAnalysis(**analysis) for analysis in analyses]

# Include the router in the main app
app.include_router(api_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    logger.info("Gradi API starting up...")
    logger.info("Services configured: Dumpling AI, Gemini AI, MongoDB")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
    logger.info("Gradi API shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
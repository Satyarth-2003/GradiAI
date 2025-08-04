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
from datetime import datetime, timedelta
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
app = FastAPI(title="GradiAI YouTube Video Analysis API")

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
    """Fetch transcript using Dumpling AI"""
    try:
        logger.info(f"Fetching transcript for: {youtube_url}")
        
        # Use the correct Dumpling AI API endpoint
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://app.dumplingai.com/api/v1/get-youtube-transcript",
                headers={
                    "Authorization": f"Bearer {DUMPLING_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "videoUrl": youtube_url,
                    "includeTimestamps": False,
                    "timestampsToCombine": 5,
                    "preferredLanguage": "en"
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                transcript = result.get("transcript", result.get("text", ""))
                if transcript:
                    logger.info(f"Successfully fetched transcript from Dumpling AI: {len(transcript)} characters")
                    return transcript
                else:
                    logger.error("Empty transcript received from Dumpling AI")
                    raise HTTPException(status_code=400, detail="No transcript available for this video")
            else:
                logger.error(f"Dumpling API error: {response.status_code} - {response.text}")
                raise HTTPException(status_code=400, detail=f"Failed to fetch transcript: {response.text}")
                
    except httpx.TimeoutException:
        logger.error("Timeout while fetching transcript from Dumpling AI")
        raise HTTPException(status_code=408, detail="Timeout while fetching transcript")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching transcript from Dumpling AI: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching transcript: {str(e)}")

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

        async with httpx.AsyncClient(timeout=90.0) as client:
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
    return {"message": "GradiAI YouTube Video Analysis API - Ready to analyze! 🚀"}

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
        
        # Step 1: Check cache for existing analysis (within last 7 days)
        cache_expiry = datetime.utcnow() - timedelta(days=7)
        cached_analysis = await db.video_analyses.find_one({
            "youtube_url": request.youtube_url,
            "created_at": {"$gte": cache_expiry}
        })
        
        if cached_analysis:
            logger.info(f"Found cached analysis for video: {video_id}")
            
            # Add cache metadata to response
            analysis_result = cached_analysis["analysis_result"]
            analysis_result["_cache_info"] = {
                "from_cache": True,
                "cached_at": cached_analysis["created_at"].isoformat(),
                "original_duration": cached_analysis["analysis_duration"]
            }
            
            return VideoAnalysisResponse(
                success=True,
                data=analysis_result
            )
        
        logger.info(f"No valid cache found, proceeding with fresh analysis for video: {video_id}")
        
        # Step 2: Fetch transcript from Dumpling AI
        transcript = await fetch_transcript_dumpling(request.youtube_url)
        if not transcript.strip():
            raise HTTPException(status_code=400, detail="No transcript available for this video")
        
        # Step 3: Analyze with Gemini
        analysis_result = await analyze_with_gemini(transcript)
        
        # Calculate duration
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        # Add fresh analysis metadata
        analysis_result["_cache_info"] = {
            "from_cache": False,
            "analyzed_at": datetime.utcnow().isoformat(),
            "analysis_duration": duration
        }
        
        # Step 4: Store in database (remove old entries for same URL)
        await db.video_analyses.delete_many({"youtube_url": request.youtube_url})
        
        video_analysis = VideoAnalysis(
            youtube_url=request.youtube_url,
            transcript=transcript,
            analysis_result=analysis_result,
            analysis_duration=duration
        )
        await db.video_analyses.insert_one(video_analysis.dict())
        
        logger.info(f"Fresh analysis completed in {duration:.2f} seconds")
        
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
    logger.info("GradiAI API starting up...")
    logger.info("Services configured: Dumpling AI, Gemini AI, MongoDB")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
    logger.info("GradiAI API shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
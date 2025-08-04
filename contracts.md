# Gradi YouTube Video Analysis - Integration Contracts

## API Contracts

### Backend Endpoints

#### 1. POST /api/analyze-video
**Request:**
```json
{
  "youtube_url": "https://youtube.com/watch?v=dQw4w9WgXcQ"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "summary": "Gradi thinks... Bhai ne arrays aur data structures ko bahut clearly explain kiya hai!...",
    "positives": ["Clear introduction with 'Namaste friends'...", "..."],
    "negatives": ["Thoda fast pace tha...", "..."],
    "suggestions_for_improvement": ["Add more pauses between concepts...", "..."],
    "ratings": {
      "Clarity of Content": {
        "score": 4.2,
        "reason": "Concepts clearly explain kiye...",
        "positives": ["Step-by-step breakdown", "..."],
        "negatives": ["Pace thoda fast tha", "..."],
        "suggestions": ["Add more pauses between concepts", "..."]
      },
      // ... other 5 categories
    }
  }
}
```

#### 2. GET /api/health
Simple health check endpoint

## Mock Data Replacement

### Frontend Mock Data (mockData.js)
Currently using static mock responses for:
- Video analysis results
- 6 category ratings with scores
- Gradi's Hinglish commentary style

**To Replace:** Remove mockData.js usage and call real backend API

## Backend Implementation Plan

### 1. Dumpling AI Integration
- **Purpose:** Fetch YouTube video transcripts  
- **API Key:** `sk_1yR1kykvH1AzgBbq2x1V5horFkhHY80yH9uSHETkyWWfi6uQ`
- **Endpoint:** Extract transcript from YouTube URL
- **Error Handling:** Invalid URLs, private videos, no transcript available

### 2. Gemini AI Integration  
- **Purpose:** Analyze transcript in Gradi's style
- **API Key:** `AIzaSyADOhRk7LHu3SeWyLlG1JVeAhui-2lyI-k`
- **Model:** `gemini-1.5-pro`
- **Prompt:** Use exact Gradi personality prompt with transcript analysis
- **Output:** JSON response with exact format matching mockData structure

### 3. Database Models (Optional)
```python
class VideoAnalysis:
    youtube_url: str
    transcript: str
    analysis_result: dict
    created_at: datetime
    analysis_duration: float
```

## Frontend & Backend Integration

### 1. API Service Layer
Create `src/services/api.js`:
```javascript
const analyzeVideo = async (youtubeUrl) => {
  const response = await axios.post(`${API}/analyze-video`, {
    youtube_url: youtubeUrl
  });
  return response.data;
};
```

### 2. Replace Mock Usage
In `GradiAnalyzer.jsx`:
- Remove `import { mockAnalysisData } from '../data/mockData';`
- Replace `setAnalysisResult(mockAnalysisData);` with actual API call
- Add proper error handling for API failures

### 3. Loading States
- Show progress: "Fetching transcript..." → "Analyzing with Gemini..." → "Complete!"
- Handle timeouts (Gemini can take 30-60 seconds)
- Error states for invalid URLs or API failures

## Error Handling Strategy

### Frontend
- Invalid YouTube URL format
- Network timeouts
- API server errors
- Empty analysis results

### Backend  
- Dumpling API failures (invalid URL, no transcript)
- Gemini API rate limits or errors
- Malformed transcript data
- JSON parsing errors

## Testing Plan

### Backend Testing
1. Test Dumpling AI transcript fetching
2. Test Gemini AI analysis with real transcript
3. Test error scenarios (invalid URLs, API failures)
4. Verify JSON response format matches frontend expectations

### Integration Testing
1. Full flow: YouTube URL → transcript → analysis → display
2. Error handling for each API failure point
3. Loading states and timeouts
4. Multiple video types (educational, coding, general)

## Performance Considerations

- Transcript fetching: 2-5 seconds
- Gemini analysis: 15-45 seconds  
- Total expected time: 20-50 seconds
- Add progress indicators for user experience
- Consider caching analyzed videos to avoid re-processing
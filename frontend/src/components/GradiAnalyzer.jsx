import React, { useState } from 'react';
import { Card, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Star, Play, Youtube, Zap, Brain, Target, AlertCircle } from 'lucide-react';
import { apiService } from '../services/api';

const GradiCharacter = ({ isProcessing, overallScore }) => {
  return (
    <div className="relative flex items-center justify-center mb-8">
      <div className={`gradi-character ${isProcessing ? 'processing' : ''}`}>
        <div className="character-head">
          <div className="hair"></div>
          <div className="face">
            <div className="eye left-eye"></div>
            <div className="eye right-eye"></div>
            <div className="mouth"></div>
          </div>
          <div className="techwear-collar"></div>
        </div>
        {isProcessing && (
          <div className="processing-rings">
            <div className="ring ring-1"></div>
            <div className="ring ring-2"></div>
            <div className="ring ring-3"></div>
          </div>
        )}
      </div>
      {overallScore && (
        <div className="speech-bubble">
          <div className="bubble-content">
            <span className="text-sm font-medium">Gradi Score</span>
            <div className="flex items-center gap-1 mt-1">
              {[1,2,3,4,5].map(star => (
                <Star 
                  key={star} 
                  className={`w-4 h-4 ${star <= Math.round(overallScore) ? 'fill-yellow-400 text-yellow-400' : 'text-gray-400'}`}
                />
              ))}
              <span className="ml-2 text-cyan-400 font-bold">{overallScore.toFixed(1)}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const StarRating = ({ score, size = 'w-5 h-5' }) => {
  return (
    <div className="flex items-center gap-1">
      {[1,2,3,4,5].map(star => (
        <Star 
          key={star} 
          className={`${size} ${star <= Math.round(score) ? 'fill-yellow-400 text-yellow-400' : 'text-gray-400'}`}
        />
      ))}
      <span className="ml-2 text-cyan-400 font-bold">{score.toFixed(1)}/5</span>
    </div>
  );
};

const CategoryCard = ({ category, data }) => {
  const getScoreColor = (score) => {
    if (score >= 4) return 'text-green-400';
    if (score >= 3) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getScoreLabel = (score) => {
    if (score >= 4.5) return 'Outstanding! 🔥';
    if (score >= 4) return 'Great Work! ⭐';
    if (score >= 3) return 'Good! 👍';
    if (score >= 2) return 'Average 📈';
    return 'Needs Work 💪';
  };

  const icons = {
    'Clarity of Content': Target,
    'Commercial Balance': Zap,
    'Content Depth': Brain,
    'Student Interaction': Play,
    'Content Structure': Target,
    'Communication Effectiveness': Zap
  };

  const Icon = icons[category] || Target;

  return (
    <Card className="bg-gray-800/50 border-purple-500/30 mb-4">
      <CardContent className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <Icon className="w-6 h-6 text-cyan-400" />
            <h3 className="text-lg font-semibold text-white">{category}</h3>
          </div>
          <div className="flex items-center gap-3">
            <StarRating score={data.score} />
            <span className={`text-sm font-medium ${getScoreColor(data.score)}`}>
              {getScoreLabel(data.score)}
            </span>
          </div>
        </div>
        
        <div className="mb-4">
          <Progress value={(data.score / 5) * 100} className="h-2 bg-gray-700" />
        </div>

        <p className="text-gray-300 mb-4 text-sm">{data.reason}</p>

        <div className="grid md:grid-cols-3 gap-4 text-sm">
          <div>
            <h4 className="text-green-400 font-medium mb-2">Positives:</h4>
            <ul className="space-y-1">
              {data.positives.map((positive, idx) => (
                <li key={idx} className="text-green-300 flex items-start gap-1">
                  <span className="text-green-400 mt-1">+</span>
                  {positive}
                </li>
              ))}
            </ul>
          </div>
          
          <div>
            <h4 className="text-yellow-400 font-medium mb-2">Areas to improve:</h4>
            <ul className="space-y-1">
              {data.negatives.map((negative, idx) => (
                <li key={idx} className="text-yellow-300 flex items-start gap-1">
                  <span className="text-yellow-400 mt-1">-</span>
                  {negative}
                </li>
              ))}
            </ul>
          </div>
          
          <div>
            <h4 className="text-cyan-400 font-medium mb-2">Suggestions:</h4>
            <ul className="space-y-1">
              {data.suggestions.map((suggestion, idx) => (
                <li key={idx} className="text-cyan-300 flex items-start gap-1">
                  <span className="text-cyan-400 mt-1">→</span>
                  {suggestion}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

const GradiAnalyzer = () => {
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [analysisStage, setAnalysisStage] = useState('');
  const [error, setError] = useState(null);

  const handleAnalysis = async () => {
    if (!youtubeUrl) return;

    setIsAnalyzing(true);
    setAnalysisResult(null);
    setError(null);

    try {
      // Stage 1: Fetching transcript
      setAnalysisStage('Fetching transcript from Dumpling AI...');
      
      // Stage 2: Analyzing
      setAnalysisStage('Gradi is analyzing with Gemini AI...');
      
      // Stage 3: Processing
      setAnalysisStage('Preparing detailed analysis...');
      
      // Make actual API call
      const response = await apiService.analyzeVideo(youtubeUrl);
      
      if (response.success) {
        setAnalysisResult(response.data);
      } else {
        throw new Error(response.error || 'Analysis failed');
      }
      
    } catch (err) {
      console.error('Analysis error:', err);
      setError(err.message);
    } finally {
      setIsAnalyzing(false);
      setAnalysisStage('');
    }
  };

  const getOverallScore = () => {
    if (!analysisResult) return 0;
    const scores = Object.values(analysisResult.ratings).map(r => r.score);
    return scores.reduce((a, b) => a + b, 0) / scores.length;
  };

  const getOverallScoreLabel = (score) => {
    if (score >= 4.5) return 'Outstanding Performance! 🔥';
    if (score >= 4) return 'Great Work! ⭐';
    if (score >= 3) return 'Good Performance! 👍';
    if (score >= 2) return 'Average Performance 📈';
    return 'Needs Improvement 💪';
  };

  return (
    <div className="min-h-screen gradi-bg">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-white mb-2 flex items-center justify-center gap-3">
              <Youtube className="w-8 h-8 text-red-500" />
              YouTube Video Analysis
            </h1>
            <p className="text-gray-300">
              Apne educational video ka YouTube link paste karo - Gradi automatic transcript fetch karke detailed analysis dega! 🚀
            </p>
          </div>

          {/* Gradi Character */}
          <GradiCharacter 
            isProcessing={isAnalyzing} 
            overallScore={analysisResult ? getOverallScore() : null} 
          />

          {/* Input Section */}
          <Card className="bg-gray-800/50 border-purple-500/30 mb-8">
            <CardContent className="p-6">
              <div className="flex gap-4">
                <Input 
                  placeholder="https://youtube.com/watch?v=dQw4w9WgXcQ"
                  value={youtubeUrl}
                  onChange={(e) => setYoutubeUrl(e.target.value)}
                  className="flex-1 bg-gray-700/50 border-gray-600 text-white placeholder-gray-400"
                />
                <Button 
                  onClick={handleAnalysis}
                  disabled={isAnalyzing || !youtubeUrl}
                  className="px-8 bg-gradient-to-r from-cyan-500 to-purple-500 hover:from-cyan-600 hover:to-purple-600 text-white font-medium"
                >
                  {isAnalyzing ? (
                    <div className="flex items-center gap-2">
                      <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                      Analyzing...
                    </div>
                  ) : (
                    <>
                      <Zap className="w-4 h-4 mr-2" />
                      Gradi Analysis Start Karo! 🔥
                    </>
                  )}
                </Button>
              </div>
              {isAnalyzing && (
                <div className="mt-4 text-center">
                  <p className="text-cyan-400 text-sm">{analysisStage}</p>
                </div>
              )}
              <p className="text-xs text-gray-400 mt-2">
                Try sample URL: <span className="text-cyan-400 cursor-pointer" onClick={() => setYoutubeUrl('https://youtube.com/watch?v=dQw4w9WgXcQ')}>
                  https://youtube.com/watch?v=dQw4w9WgXcQ
                </span> (for data structures demo)
              </p>
            </CardContent>
          </Card>

          {/* Analysis Results */}
          {analysisResult && (
            <div className="space-y-6">
              {/* Overall Score */}
              <Card className="bg-gradient-to-r from-purple-800/30 to-blue-800/30 border-purple-500/50">
                <CardContent className="p-8 text-center">
                  <h2 className="text-2xl font-bold text-white mb-2 flex items-center justify-center gap-2">
                    <Zap className="w-6 h-6 text-yellow-400" />
                    Overall GradiScore
                  </h2>
                  <p className="text-gray-300 mb-4">Saare categories ka combined rating</p>
                  
                  <div className="text-6xl font-bold text-cyan-400 mb-4">
                    {getOverallScore().toFixed(1)}
                  </div>
                  
                  <div className="flex items-center justify-center mb-4">
                    <StarRating score={getOverallScore()} size="w-8 h-8" />
                  </div>
                  
                  <Badge className="bg-purple-600 text-white px-4 py-2 text-lg">
                    {getOverallScoreLabel(getOverallScore())}
                  </Badge>
                </CardContent>
              </Card>

              {/* Summary */}
              <Card className="bg-gray-800/50 border-purple-500/30">
                <CardContent className="p-6">
                  <h3 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                    <Brain className="w-5 h-5 text-cyan-400" />
                    📱 Gradi's Video Summary
                  </h3>
                  <p className="text-gray-300 leading-relaxed">{analysisResult.summary}</p>
                </CardContent>
              </Card>

              {/* Positives and Negatives */}
              <div className="grid md:grid-cols-2 gap-6">
                <Card className="bg-green-900/20 border-green-500/30">
                  <CardContent className="p-6">
                    <h3 className="text-lg font-semibold text-green-400 mb-4">
                      ✅ Positives - Jo Gradi Ko Pasand Aaya
                    </h3>
                    <ul className="space-y-3">
                      {analysisResult.positives.map((positive, idx) => (
                        <li key={idx} className="text-green-300 flex items-start gap-2">
                          <span className="text-green-400 mt-1 text-sm">•</span>
                          {positive}
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>

                <Card className="bg-yellow-900/20 border-yellow-500/30">
                  <CardContent className="p-6">
                    <h3 className="text-lg font-semibold text-yellow-400 mb-4">
                      ⚠️ Negatives - Improvement Areas
                    </h3>
                    <ul className="space-y-3">
                      {analysisResult.negatives.map((negative, idx) => (
                        <li key={idx} className="text-yellow-300 flex items-start gap-2">
                          <span className="text-yellow-400 mt-1 text-sm">•</span>
                          {negative}
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              </div>

              {/* Detailed Ratings */}
              <div>
                <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
                  <Target className="w-6 h-6 text-purple-400" />
                  🔥 Detailed Category Ratings
                </h2>
                <p className="text-gray-400 mb-6">Har category ka detailed breakdown</p>
                
                {Object.entries(analysisResult.ratings).map(([category, data]) => (
                  <CategoryCard key={category} category={category} data={data} />
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default GradiAnalyzer;
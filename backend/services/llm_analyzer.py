import google.generativeai as genai
import os
from typing import Dict, Any
import logging
import json

logger = logging.getLogger(__name__)

class LLMAnalyzer:
    def __init__(self):
        api_key = os.getenv("GOOGLE_AI_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_AI_API_KEY environment variable not set")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
    async def analyze_exercise(self, video_path: str, exercise_type: str) -> Dict[str, Any]:
        """Analyze exercise form using Gemini Vision - sends entire video!"""
        
        try:
            logger.info(f"Uploading video to Gemini for analysis...")
            
            # Upload video file to Gemini
            video_file = genai.upload_file(path=video_path)
            logger.info(f"Video uploaded: {video_file.uri}")
            
            # Wait for video to be processed
            import time
            while video_file.state.name == "PROCESSING":
                time.sleep(1)
                video_file = genai.get_file(video_file.name)
            
            if video_file.state.name == "FAILED":
                raise ValueError("Video processing failed")
            
            # Create exercise-specific prompt
            prompt = self._create_prompt(exercise_type)
            
            # Generate analysis
            logger.info("Generating analysis with Gemini...")
            response = self.model.generate_content(
                [video_file, prompt],
                generation_config=genai.GenerationConfig(
                    temperature=0.4,
                    max_output_tokens=2000,
                )
            )
            
            # Parse response
            result = self._parse_response(response.text, exercise_type)
            
            # Clean up uploaded file
            genai.delete_file(video_file.name)
            
            return result
            
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            return self._fallback_response(str(e))
    
    def _create_prompt(self, exercise_type: str) -> str:
        """Create exercise-specific analysis prompt"""
        
        prompts = {
            "back-squat": """
You are an expert strength coach analyzing a back squat video. Watch the entire video carefully and provide detailed form feedback.

Evaluate these aspects (score each 0-100):
1. **Depth** (25%): Hip crease should go below knee at bottom position
2. **Knee Tracking** (25%): Knees should track over toes without collapsing inward (valgus)
3. **Back Angle** (25%): Spine should stay neutral, avoid excessive forward lean
4. **Bar Path** (25%): Bar should move in a vertical line, no forward drift

IMPORTANT: You must respond with ONLY valid JSON. No explanations, no markdown, no additional text. Just the JSON object.

{
  "overall_score": 75,
  "exercise_breakdown": {
    "depth": {"score": 80, "feedback": "Good depth, hip crease below knee"},
    "knee_tracking": {"score": 70, "feedback": "Minor knee valgus on descent"},
    "back_angle": {"score": 75, "feedback": "Maintains neutral spine throughout"},
    "bar_path": {"score": 80, "feedback": "Vertical bar path with slight forward drift"}
  },
  "strengths": ["Good depth achieved", "Maintains neutral spine"],
  "areas_for_improvement": ["Knee tracking could be improved", "Bar path has slight forward drift"],
  "specific_cues": ["Push knees out on descent", "Keep chest up", "Drive hips forward"]
}

The overall_score should be the average of the 4 category scores. Be specific and constructive.
""",
            "front-squat": """
You are an expert strength coach analyzing a front squat video. Watch the entire video carefully and provide detailed form feedback.

Evaluate these aspects (score each 0-100):
1. **Depth** (25%): Hip crease should go below knee at bottom
2. **Elbow Position** (25%): Elbows should stay high, parallel to ground
3. **Torso Angle** (25%): Torso should stay upright, minimal forward lean
4. **Bar Path** (25%): Bar should move vertically

IMPORTANT: You must respond with ONLY valid JSON. No explanations, no markdown, no additional text. Just the JSON object.

{
  "overall_score": 75,
  "exercise_breakdown": {
    "depth": {"score": 80, "feedback": "Good depth, hip crease below knee"},
    "elbow_position": {"score": 70, "feedback": "Elbows drop slightly on descent"},
    "torso_angle": {"score": 75, "feedback": "Maintains upright torso"},
    "bar_path": {"score": 80, "feedback": "Vertical bar path"}
  },
  "strengths": ["Good depth achieved", "Maintains upright torso"],
  "areas_for_improvement": ["Elbow position could be improved", "Bar path has slight forward drift"],
  "specific_cues": ["Keep elbows high", "Stay upright", "Drive hips forward"]
}

The overall_score should be the average of the 4 category scores. Be specific and constructive.
""",
            "conventional-deadlift": """
You are an expert strength coach analyzing a conventional deadlift video. Watch the entire video carefully and provide detailed form feedback.

Evaluate these aspects (score each 0-100):
1. **Starting Position** (25%): Hips above knees, shoulders over bar, back flat
2. **Back Angle** (25%): Neutral spine throughout the entire lift
3. **Bar Path** (25%): Bar stays close to body, moves vertically
4. **Hip Extension** (25%): Full hip lockout at top, shoulders back

IMPORTANT: You must respond with ONLY valid JSON. No explanations, no markdown, no additional text. Just the JSON object.

{
  "overall_score": 75,
  "exercise_breakdown": {
    "depth": {"score": 80, "feedback": "Good depth, hip crease below knee"},
    "elbow_position": {"score": 70, "feedback": "Elbows drop slightly on descent"},
    "torso_angle": {"score": 75, "feedback": "Maintains upright torso"},
    "bar_path": {"score": 80, "feedback": "Vertical bar path"}
  },
  "strengths": ["Good depth achieved", "Maintains upright torso"],
  "areas_for_improvement": ["Elbow position could be improved", "Bar path has slight forward drift"],
  "specific_cues": ["Keep elbows high", "Stay upright", "Drive hips forward"]
}

The overall_score should be the average of the 4 category scores. Be specific and constructive.
""",
            "sumo-deadlift": """
You are an expert strength coach analyzing a sumo deadlift video. Watch the entire video carefully and provide detailed form feedback.

Evaluate these aspects (score each 0-100):
1. **Stance Width** (25%): Wide stance with toes pointed out 30-45 degrees
2. **Back Angle** (25%): Neutral spine, more upright torso than conventional
3. **Bar Path** (25%): Vertical bar path, stays very close to body
4. **Hip Extension** (25%): Full hip lockout at top, shoulders back

IMPORTANT: You must respond with ONLY valid JSON. No explanations, no markdown, no additional text. Just the JSON object.

{
  "overall_score": 75,
  "exercise_breakdown": {
    "depth": {"score": 80, "feedback": "Good depth, hip crease below knee"},
    "elbow_position": {"score": 70, "feedback": "Elbows drop slightly on descent"},
    "torso_angle": {"score": 75, "feedback": "Maintains upright torso"},
    "bar_path": {"score": 80, "feedback": "Vertical bar path"}
  },
  "strengths": ["Good depth achieved", "Maintains upright torso"],
  "areas_for_improvement": ["Elbow position could be improved", "Bar path has slight forward drift"],
  "specific_cues": ["Keep elbows high", "Stay upright", "Drive hips forward"]
}

The overall_score should be the average of the 4 category scores. Be specific and constructive.
"""
        }
        
        return prompts.get(exercise_type, prompts["back-squat"])
    
    def _parse_response(self, response_text: str, exercise_type: str) -> Dict[str, Any]:
        """Parse LLM response into structured feedback"""
        
        try:
            logger.info(f"Raw Gemini response: {response_text[:1000]}...")
            
            # Remove markdown code blocks if present
            response_text = response_text.strip()
            if response_text.startswith('```'):
                lines = response_text.split('\n')
                response_text = '\n'.join(lines[1:-1])
            
            # Extract JSON
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start == -1 or end == 0:
                logger.error("No JSON found in response")
                logger.error(f"Full response: {response_text}")
                raise ValueError("No JSON found in response")
            
            json_str = response_text[start:end]
            logger.info(f"Extracted JSON: {json_str}")
            
            feedback = json.loads(json_str)
            
            # Validate structure
            required_keys = ['overall_score', 'exercise_breakdown', 'strengths', 'areas_for_improvement', 'specific_cues']
            if not all(key in feedback for key in required_keys):
                logger.error(f"Missing required keys. Found: {list(feedback.keys())}")
                logger.error(f"Required: {required_keys}")
                raise ValueError("Missing required keys in response")
            
            logger.info(f"Successfully parsed Gemini response with score: {feedback['overall_score']}")
            
            return {
                "feedback": feedback,
                "screenshots": [],
                "metrics": {
                    "analysis_method": "llm_vision",
                    "model": "gemini-2.0-flash"
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
            logger.error(f"Response text: {response_text[:500]}")
            return self._fallback_response(f"Parse error: {str(e)}")
    
    def _fallback_response(self, error_msg: str) -> Dict[str, Any]:
        """Return fallback response when analysis fails"""
        return {
            "feedback": {
                "overall_score": 0,
                "exercise_breakdown": {},
                "strengths": [],
                "areas_for_improvement": ["Analysis failed - please try uploading again"],
                "specific_cues": [
                    "Ensure video shows full body from side angle",
                    "Use good lighting",
                    "Keep camera steady"
                ]
            },
            "screenshots": [],
            "metrics": {
                "error": error_msg,
                "analysis_method": "llm_vision_failed"
            }
        }


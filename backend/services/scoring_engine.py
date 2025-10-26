import logging
from typing import Dict, List, Any, Union
import numpy as np
from config.exercise_standards import (
    get_exercise_standards, 
    get_exercise_weights, 
    get_category_score
)

logger = logging.getLogger(__name__)

class ScoringEngine:
    """Unified scoring engine using research-based biomechanics standards"""
    
    def __init__(self, exercise_type: str):
        self.exercise_type = exercise_type
        self.standards = get_exercise_standards(exercise_type)
        self.weights = get_exercise_weights(exercise_type)
        
        if not self.standards:
            logger.warning(f"No standards found for exercise type: {exercise_type}")
    
    def score_metric(self, metric_name: str, value: Union[float, List[float]]) -> Dict[str, Any]:
        """
        Score a single metric based on exercise standards
        
        Args:
            metric_name: Name of the metric (e.g., 'depth', 'knee_angle')
            value: Single value or list of values to score
            
        Returns:
            {
                "score": 0-100,
                "category": "excellent|good|acceptable|poor",
                "value": float,
                "ideal_range": tuple,
                "deviation": float,
                "message": str
            }
        """
        if metric_name not in self.standards:
            logger.warning(f"Unknown metric: {metric_name} for {self.exercise_type}")
            return {
                "score": 50,
                "category": "unknown",
                "value": value,
                "ideal_range": (0, 100),
                "deviation": 0,
                "message": f"Unknown metric: {metric_name}"
            }
        
        # Handle single value or list of values
        if isinstance(value, list):
            if not value:
                return self._score_failed_metric(metric_name, "No data")
            avg_value = np.mean([v for v in value if v is not None and v > 0])
            if np.isnan(avg_value):
                return self._score_failed_metric(metric_name, "Invalid data")
            value = avg_value
        
        if value is None or value <= 0:
            return self._score_failed_metric(metric_name, "No measurement")
        
        ranges = self.standards[metric_name]
        
        # Determine category and score
        category, ideal_range = self._categorize_value(value, ranges)
        score = get_category_score(category)
        
        # Calculate deviation from ideal range
        deviation = self._calculate_deviation(value, ideal_range)
        
        # Generate message
        message = self._generate_metric_message(metric_name, value, category, ideal_range)
        
        return {
            "score": score,
            "category": category,
            "value": round(value, 1),
            "ideal_range": ideal_range,
            "deviation": round(deviation, 1),
            "message": message
        }
    
    def score_exercise(self, metrics: Dict[str, Union[float, List[float]]]) -> Dict[str, Any]:
        """
        Score entire exercise based on all metrics
        
        Args:
            metrics: Dictionary of metric_name -> value(s)
            
        Returns:
            {
                "overall_score": 0-100,
                "breakdown": Dict of metric scores,
                "strengths": List[str],
                "areas_for_improvement": List[str],
                "specific_cues": List[str]
            }
        """
        breakdown = {}
        weighted_scores = []
        strengths = []
        improvements = []
        cues = []
        
        for metric_name, value in metrics.items():
            metric_score = self.score_metric(metric_name, value)
            breakdown[metric_name] = metric_score
            
            # Add to weighted score calculation
            weight = self.weights.get(metric_name, 0.1)  # Default weight
            weighted_scores.append(metric_score["score"] * weight)
            
            # Generate feedback based on score
            if metric_score["score"] >= 80:
                strengths.append(metric_score["message"])
            elif metric_score["score"] < 60:
                improvements.append(metric_score["message"])
                cues.append(self._generate_cue(metric_name, metric_score["category"]))
        
        # Calculate overall score
        overall_score = int(np.sum(weighted_scores)) if weighted_scores else 0
        
        # Ensure we have some feedback
        if not strengths:
            strengths.append("Good effort on the exercise!")
        if not improvements:
            improvements.append("Continue practicing to improve form")
        if not cues:
            cues.append("Focus on maintaining proper technique throughout the movement")
        
        return {
            "overall_score": overall_score,
            "breakdown": breakdown,
            "strengths": strengths,
            "areas_for_improvement": improvements,
            "specific_cues": cues
        }
    
    def _categorize_value(self, value: float, ranges: Dict[str, Union[tuple, str]]) -> tuple:
        """Determine category and ideal range for a value"""
        for category in ["excellent", "good", "acceptable", "poor"]:
            if category in ranges:
                range_val = ranges[category]
                if isinstance(range_val, tuple) and self._in_range(value, range_val):
                    return category, range_val
                elif isinstance(range_val, str) and range_val == "outside acceptable":
                    # This is for ranges that don't fit in acceptable
                    continue
        
        # Default to poor if no range matches
        return "poor", ranges.get("poor", (0, 100))
    
    def _in_range(self, value: float, range_tuple: tuple) -> bool:
        """Check if value is within range"""
        if not isinstance(range_tuple, tuple) or len(range_tuple) != 2:
            return False
        return range_tuple[0] <= value <= range_tuple[1]
    
    def _calculate_deviation(self, value: float, ideal_range: tuple) -> float:
        """Calculate how far value deviates from ideal range"""
        if not isinstance(ideal_range, tuple) or len(ideal_range) != 2:
            return 0
        
        ideal_center = (ideal_range[0] + ideal_range[1]) / 2
        return abs(value - ideal_center)
    
    def _generate_metric_message(self, metric_name: str, value: float, category: str, ideal_range: tuple) -> str:
        """Generate human-readable message for metric"""
        metric_display = metric_name.replace("_", " ").title()
        
        if category == "excellent":
            return f"Excellent {metric_display.lower()}: {value:.1f}°"
        elif category == "good":
            return f"Good {metric_display.lower()}: {value:.1f}°"
        elif category == "acceptable":
            return f"Acceptable {metric_display.lower()}: {value:.1f}°"
        else:
            return f"Needs improvement in {metric_display.lower()}: {value:.1f}° (ideal: {ideal_range[0]}-{ideal_range[1]}°)"
    
    def _generate_cue(self, metric_name: str, category: str) -> str:
        """Generate specific cue for improvement"""
        cues = {
            "depth": "Focus on reaching proper depth while maintaining form",
            "knee_angle": "Work on knee positioning throughout the movement",
            "torso_angle": "Maintain proper torso position and avoid excessive lean",
            "knee_tracking": "Keep knees tracking over your toes",
            "bar_path": "Focus on maintaining a vertical bar path",
            "hip_angle": "Work on hip positioning and mobility",
            "back_angle": "Maintain neutral spine throughout the movement",
            "stance_width": "Adjust your stance width for optimal positioning",
            "hip_extension": "Focus on full hip extension at the top"
        }
        
        return cues.get(metric_name, "Focus on proper technique for this aspect")
    
    def _score_failed_metric(self, metric_name: str, reason: str) -> Dict[str, Any]:
        """Score a metric that couldn't be measured"""
        return {
            "score": 0,
            "category": "failed",
            "value": 0,
            "ideal_range": (0, 100),
            "deviation": 0,
            "message": f"Could not measure {metric_name.replace('_', ' ')} - {reason}"
        }

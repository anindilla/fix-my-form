"""
Exercise Standards Configuration

Research-based biomechanics thresholds for exercise form analysis.
Sources: NSCA, Rippetoe's Starting Strength, Biomechanics research papers
"""

EXERCISE_STANDARDS = {
    "back-squat": {
        "depth": {
            "excellent": (85, 95),    # Hip angle at bottom (degrees)
            "good": (95, 105),
            "acceptable": (105, 120),
            "poor": (120, 180)
        },
        "knee_angle": {
            "excellent": (80, 100),   # Knee angle at bottom
            "good": (70, 80),
            "acceptable": (60, 70),
            "poor": (0, 60)
        },
        "torso_angle": {
            "excellent": (0, 15),     # Forward lean from vertical
            "good": (15, 30),
            "acceptable": (30, 45),
            "poor": (45, 90)
        },
        "knee_tracking": {
            "excellent": (-0.02, 0.02),  # Valgus/varus (normalized)
            "good": (-0.05, -0.02),
            "acceptable": (-0.08, -0.05),
            "poor": "outside acceptable"
        },
        "bar_path": {
            "excellent": (0.95, 1.05),  # Vertical bar path ratio
            "good": (0.90, 0.95),
            "acceptable": (0.85, 0.90),
            "poor": (0, 0.85)
        }
    },
    
    "front-squat": {
        "depth": {
            "excellent": (85, 95),    # Hip angle at bottom
            "good": (95, 105),
            "acceptable": (105, 120),
            "poor": (120, 180)
        },
        "knee_angle": {
            "excellent": (80, 100),   # Knee angle at bottom
            "good": (70, 80),
            "acceptable": (60, 70),
            "poor": (0, 60)
        },
        "torso_angle": {
            "excellent": (0, 10),     # More upright than back squat
            "good": (10, 20),
            "acceptable": (20, 35),
            "poor": (35, 90)
        },
        "knee_tracking": {
            "excellent": (-0.02, 0.02),
            "good": (-0.05, -0.02),
            "acceptable": (-0.08, -0.05),
            "poor": "outside acceptable"
        },
        "bar_path": {
            "excellent": (0.95, 1.05),
            "good": (0.90, 0.95),
            "acceptable": (0.85, 0.90),
            "poor": (0, 0.85)
        }
    },
    
    "conventional-deadlift": {
        "hip_angle": {
            "excellent": (35, 50),     # Hip angle at start position
            "good": (30, 35),
            "acceptable": (25, 30),
            "poor": (0, 25)
        },
        "knee_angle": {
            "excellent": (120, 140),  # Knee angle at start position
            "good": (110, 120),
            "acceptable": (100, 110),
            "poor": (0, 100)
        },
        "back_angle": {
            "excellent": (0, 10),     # Neutral spine
            "good": (10, 20),
            "acceptable": (20, 30),
            "poor": (30, 90)
        },
        "bar_path": {
            "excellent": (0.95, 1.05),  # Vertical bar path
            "good": (0.90, 0.95),
            "acceptable": (0.85, 0.90),
            "poor": (0, 0.85)
        },
        "hip_extension": {
            "excellent": (160, 180),  # Hip extension at lockout
            "good": (150, 160),
            "acceptable": (140, 150),
            "poor": (0, 140)
        }
    },
    
    "sumo-deadlift": {
        "hip_angle": {
            "excellent": (70, 90),    # More upright hip position
            "good": (60, 70),
            "acceptable": (50, 60),
            "poor": (0, 50)
        },
        "knee_angle": {
            "excellent": (100, 120),  # Knee angle at start
            "good": (90, 100),
            "acceptable": (80, 90),
            "poor": (0, 80)
        },
        "stance_width": {
            "excellent": (1.5, 2.0),  # Relative to shoulder width
            "good": (1.3, 1.5),
            "acceptable": (1.1, 1.3),
            "poor": (0, 1.1)
        },
        "torso_angle": {
            "excellent": (0, 15),     # Upright torso
            "good": (15, 25),
            "acceptable": (25, 40),
            "poor": (40, 90)
        },
        "bar_path": {
            "excellent": (0.95, 1.05),
            "good": (0.90, 0.95),
            "acceptable": (0.85, 0.90),
            "poor": (0, 0.85)
        }
    }
}

# Scoring weights for different metrics (how much each contributes to overall score)
EXERCISE_WEIGHTS = {
    "back-squat": {
        "depth": 0.30,
        "knee_angle": 0.25,
        "torso_angle": 0.20,
        "knee_tracking": 0.15,
        "bar_path": 0.10
    },
    "front-squat": {
        "depth": 0.25,
        "knee_angle": 0.25,
        "torso_angle": 0.25,  # More important for front squat
        "knee_tracking": 0.15,
        "bar_path": 0.10
    },
    "conventional-deadlift": {
        "hip_angle": 0.25,
        "knee_angle": 0.20,
        "back_angle": 0.30,   # Most important - safety
        "bar_path": 0.15,
        "hip_extension": 0.10
    },
    "sumo-deadlift": {
        "hip_angle": 0.25,
        "knee_angle": 0.20,
        "stance_width": 0.20,
        "torso_angle": 0.20,
        "bar_path": 0.15
    }
}

# Minimum scores for each category
CATEGORY_SCORES = {
    "excellent": 95,
    "good": 80,
    "acceptable": 65,
    "poor": 40
}

def get_exercise_standards(exercise_type: str) -> dict:
    """Get standards for a specific exercise type"""
    return EXERCISE_STANDARDS.get(exercise_type, {})

def get_exercise_weights(exercise_type: str) -> dict:
    """Get scoring weights for a specific exercise type"""
    return EXERCISE_WEIGHTS.get(exercise_type, {})

def get_category_score(category: str) -> int:
    """Get score for a quality category"""
    return CATEGORY_SCORES.get(category, 40)

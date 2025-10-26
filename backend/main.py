async def _perform_analysis(request: AnalysisRequest) -> AnalysisResponse:
    """Perform the actual analysis with timeout protection"""
    # Download video from R2
    logger.info("Downloading video from R2...")
    video_path = await storage_service.download_video(request.filename)
    logger.info(f"Video downloaded to: {video_path}")
    
    # 1. Validate video quality - TEMPORARILY DISABLED FOR DEBUGGING
    logger.info("Skipping video quality validation for debugging...")
    
    # 2. Extract frames (adaptive)
    logger.info("Extracting frames from video...")
    frames = await video_processor.extract_frames(video_path)
    logger.info(f"Extracted {len(frames)} frames")
    
    # 3. Analyze poses with quality gate
    logger.info("Analyzing poses in frames...")
    pose_data = await pose_analyzer.analyze_poses(frames)
    logger.info(f"Analyzed {len(pose_data)} pose frames")
    
    # Check pose detection quality - TEMPORARILY DISABLED FOR DEBUGGING
    pose_success_rate = len(pose_data) / len(frames) if frames else 0
    logger.info(f"Pose detection success rate: {pose_success_rate:.1%}")
    
    # 4. Detect movement period (NEW!)
    logger.info("Detecting movement period...")
    try:
        movement_start, movement_end = movement_detector.detect_movement_period(pose_data, frames)
        logger.info(f"Movement detected: frames {movement_start}-{movement_end}")
        
        # Extract only the movement period for analysis
        movement_pose_data = pose_data[movement_start:movement_end + 1]
        movement_frames = frames[movement_start:movement_end + 1]
        logger.info(f"Analyzing {len(movement_pose_data)} frames of actual movement")
    except Exception as e:
        logger.warning(f"Movement detection failed: {e}, using entire video")
        movement_pose_data = pose_data
        movement_frames = frames
        movement_start, movement_end = 0, len(pose_data) - 1
    
    # 5. Run exercise analysis on movement period only
    exercise_type = request.exercise_type.lower()
    logger.info(f"Running {exercise_type} analysis on movement period...")
    
    if exercise_type == "back-squat":
        analysis_result = await squat_analyzer.analyze(movement_pose_data, movement_frames)
    elif exercise_type == "front-squat":
        analysis_result = await front_squat_analyzer.analyze(movement_pose_data, movement_frames)
    elif exercise_type == "conventional-deadlift":
        analysis_result = await deadlift_analyzer.analyze(movement_pose_data, movement_frames)
    elif exercise_type == "sumo-deadlift":
        analysis_result = await sumo_deadlift_analyzer.analyze(movement_pose_data, movement_frames)
    else:
        raise HTTPException(status_code=400, detail="Unsupported exercise type")
    
    logger.info("Exercise analysis completed successfully")
    
    # Generate and upload screenshots (optional)
    screenshot_urls = []
    try:
        if analysis_result.get("screenshots"):
            logger.info("Uploading screenshots...")
            screenshot_urls = await storage_service.upload_screenshots(
                analysis_result["screenshots"], 
                request.file_id
            )
            logger.info(f"Uploaded {len(screenshot_urls)} screenshots")
    except Exception as e:
        logger.warning(f"Screenshot upload failed: {e}")
        screenshot_urls = []
    
    # Create analysis response with movement info
    logger.info("Creating analysis response...")
    
    # Add movement analysis to metrics
    try:
        movement_analysis = movement_detector.get_movement_analysis(pose_data, frames)
        enhanced_metrics = {
            **analysis_result["metrics"],
            "movement_analysis": {
                "total_frames": movement_analysis["total_frames"],
                "movement_frames": len(movement_pose_data),
                "setup_frames": movement_analysis["setup_frames"],
                "rest_frames": movement_analysis["rest_frames"],
                "movement_period": f"{movement_start}-{movement_end}"
            }
        }
    except Exception as e:
        logger.warning(f"Movement analysis failed: {e}, using basic metrics")
        enhanced_metrics = {
            **analysis_result["metrics"],
            "movement_analysis": {
                "total_frames": len(pose_data),
                "movement_frames": len(movement_pose_data),
                "setup_frames": 0,
                "rest_frames": 0,
                "movement_period": f"{movement_start}-{movement_end}",
                "error": "movement_analysis_failed"
            }
        }
    
    analysis_response = AnalysisResponse(
        file_id=request.file_id,
        exercise_type=request.exercise_type,
        status="completed",
        feedback=analysis_result["feedback"],
        screenshots=screenshot_urls,
        metrics=enhanced_metrics
    )
    
    # Store the result
    analysis_results[request.file_id] = analysis_response
    logger.info(f"Analysis completed successfully for {request.file_id}")
    
    return analysis_response
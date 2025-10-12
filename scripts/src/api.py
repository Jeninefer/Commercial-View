"""
Commercial View Analytics API
FastAPI-based web service for portfolio analysis
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import json
import os
import subprocess
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import logging
import aiofiles

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Commercial View Analytics API",
    description="Portfolio analysis and financial analytics platform",
    version="1.0.0"
)

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Commercial View Analytics API",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "health": "/health",
            "portfolio_summary": "/portfolio/summary", 
            "latest_analysis": "/analysis/latest",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    # Check if data files exist
    data_path = Path("data/raw")
    data_files = list(data_path.glob("*")) if data_path.exists() else []
    
    # Check if exports directory exists
    exports_path = Path("abaco_runtime/exports")
    exports_exist = exports_path.exists()
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "data_files_available": len(data_files),
        "exports_directory": exports_exist,
        "system": "operational"
    }

@app.get("/analysis/latest")
async def latest_analysis():
    """Get the latest analysis results"""
    try:
        analytics_path = Path("abaco_runtime/exports/analytics")
        if not analytics_path.exists():
            return {"message": "No analytics directory found", "analyses": []}
        
        json_files = analytics_path.glob("*.json")
        analyses = []
        
        for file in sorted(json_files, key=os.path.getctime, reverse=True)[:5]:
            try:
                async with aiofiles.open(file, 'r') as f:
                    content = await f.read()
                    data = json.loads(content)
                
                total_records_dict = data.get("total_records", {})
                total_records = sum(total_records_dict.values()) if total_records_dict else 0
                
                analyses.append({
                    "filename": file.name,
                    "timestamp": data.get("processing_timestamp"),
                    "datasets": data.get("datasets_loaded", []),
                    "total_records": total_records
                })
            except Exception as e:
                logger.warning(f"Error reading {file}: {e}")
        
        return {
            "latest_analyses": analyses,
            "count": len(analyses),
            "api_timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error getting analyses: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/portfolio/summary")
async def portfolio_summary():
    """Get portfolio summary from latest analysis"""
    try:
        # Find the most recent analysis file
        analytics_path = Path("abaco_runtime/exports/analytics")
        if not analytics_path.exists():
            raise HTTPException(status_code=404, detail="No analytics data found")
        
        json_files = analytics_path.glob("*.json")
        json_files_list = list(json_files)  # Need list for max() function
        if not json_files_list:
            raise HTTPException(status_code=404, detail="No analysis files found")
        
        # Get the most recent file
        latest_file = max(json_files_list, key=os.path.getctime)
        
        async with aiofiles.open(latest_file, 'r') as f:
            content = await f.read()
            data = json.loads(content)
        
        return {
            "summary": data,
            "file": str(latest_file),
            "generated": data.get("processing_timestamp"),
            "api_timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error reading portfolio summary: {e}")
        raise HTTPException(status_code=500, detail=f"Error reading analysis: {str(e)}")

@app.get("/data/status")
async def data_status():
    """Check status of data files"""
    try:
        data_path = Path("data/raw")
        files_info = []
        
        if data_path.exists():
            for file in data_path.iterdir():
                if file.is_file():
                    stat = file.stat()
                    files_info.append({
                        "name": file.name,
                        "size_mb": round(stat.st_size / (1024*1024), 2),
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
        
        return {
            "data_directory": str(data_path),
            "files": files_info,
            "total_files": len(files_info),
            "total_size_mb": round(sum(f["size_mb"] for f in files_info), 2)
        }
    
    except Exception as e:
        logger.error(f"Error checking data status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analysis/trigger")
async def trigger_analysis():
    """Trigger a new portfolio analysis"""
    try:
        # Change to the correct directory
        os.chdir("/workspaces/Commercial-View")
        
        # Run the portfolio processor asynchronously
        process = await asyncio.create_subprocess_exec(
            "python", "src/process_portfolio.py",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=300
            )
            
            if process.returncode == 0:
                return {
                    "status": "success",
                    "message": "Analysis completed successfully",
                    "output": stdout.decode(),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "error", 
                    "message": "Analysis failed",
                    "error": stderr.decode(),
                    "timestamp": datetime.now().isoformat()
                }
        except asyncio.TimeoutError:
            process.kill()
            return {
                "status": "timeout",
                "message": "Analysis timed out after 5 minutes",
                "timestamp": datetime.now().isoformat()
            }
    
    except Exception as e:
        logger.error(f"Error triggering analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Add CORS middleware if needed
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

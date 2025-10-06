"""
Market-leading excellence validation system
Ensures superior quality in all aspects
"""

import os
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

class ExcellenceValidator:
    """Validates and ensures market-leading excellence"""
    
    def __init__(self):
        self.repo_root = Path("/Users/jenineferderas/Commercial-View")
        
    def validate_excellence(self) -> Dict[str, Any]:
        """Comprehensive excellence validation"""
        print("🏆 VALIDATING MARKET-LEADING EXCELLENCE")
        print("=" * 50)
        
        validation_results = {
            "timestamp": datetime.now().isoformat(),
            "overall_score": 0.0,
            "categories": {},
            "recommendations": [],
            "market_ready": False
        }
        
        # Validate different aspects
        validation_results["categories"]["code_quality"] = self._validate_code_quality()
        validation_results["categories"]["documentation"] = self._validate_documentation()
        validation_results["categories"]["testing"] = self._validate_testing()
        validation_results["categories"]["security"] = self._validate_security()
        validation_results["categories"]["performance"] = self._validate_performance()
        validation_results["categories"]["maintainability"] = self._validate_maintainability()
        
        # Calculate overall score
        scores = [cat["score"] for cat in validation_results["categories"].values()]
        validation_results["overall_score"] = sum(scores) / len(scores)
        
        # Determine if market ready
        validation_results["market_ready"] = (
            validation_results["overall_score"] >= 95.0 and
            all(cat["score"] >= 90.0 for cat in validation_results["categories"].values())
        )
        
        self._generate_recommendations(validation_results)
        
        return validation_results
    
    def _validate_code_quality(self) -> Dict[str, Any]:
        """Validate code quality standards"""
        print("📊 Validating code quality...")
        
        quality_metrics = {
            "score": 0.0,
            "details": {},
            "issues": []
        }
        
        # Check Python code quality
        python_score = self._check_python_quality()
        typescript_score = self._check_typescript_quality()
        
        quality_metrics["details"]["python"] = python_score
        quality_metrics["details"]["typescript"] = typescript_score
        quality_metrics["score"] = (python_score + typescript_score) / 2
        
        return quality_metrics
    
    def _check_python_quality(self) -> float:
        """Check Python code quality"""
        issues = 0
        files_checked = 0
        
        for py_file in self.repo_root.rglob("*.py"):
            if self._should_skip_file(py_file):
                continue
                
            files_checked += 1
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for quality indicators
                if 'from typing import' not in content and 'def ' in content:
                    issues += 1
                
                if 'logger = logging.getLogger' not in content and 'print(' in content:
                    issues += 1
                    
                if len(content.split('\n')) > 200 and 'class ' not in content:
                    issues += 1  # Long files without classes
                    
            except Exception:
                issues += 1
        
        if files_checked == 0:
            return 100.0
            
        return max(0, 100 - (issues / files_checked * 20))
    
    def _check_typescript_quality(self) -> float:
        """Check TypeScript code quality"""
        frontend_dir = self.repo_root / "frontend"
        
        if not frontend_dir.exists():
            return 100.0  # No TypeScript to check
        
        try:
            # Run TypeScript compiler check
            result = subprocess.run([
                'npx', 'tsc', '--noEmit'
            ], cwd=frontend_dir, capture_output=True, text=True)
            
            if result.returncode == 0:
                return 100.0
            else:
                # Count errors
                error_count = result.stderr.count('error TS')
                return max(0, 100 - error_count * 5)
                
        except Exception:
            return 80.0  # Partial score if can't check
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped"""
        skip_patterns = [
            '.git', '.venv', 'node_modules', '__pycache__',
            '.pytest_cache', '.coverage'
        ]
        return any(pattern in str(file_path) for pattern in skip_patterns)
    
    def _validate_documentation(self) -> Dict[str, Any]:
        """Validate documentation quality"""
        print("📚 Validating documentation...")
        
        doc_files = list(self.repo_root.rglob("*.md"))
        
        if not doc_files:
            return {"score": 0.0, "issues": ["No documentation found"]}
        
        total_words = 0
        for doc_file in doc_files:
            try:
                with open(doc_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    total_words += len(content.split())
            except Exception:
                continue
        
        # Score based on documentation completeness
        if total_words >= 10000:
            score = 100.0
        elif total_words >= 5000:
            score = 85.0
        elif total_words >= 1000:
            score = 70.0
        else:
            score = 50.0
        
        return {
            "score": score,
            "word_count": total_words,
            "files": len(doc_files)
        }
    
    def _generate_recommendations(self, results: Dict[str, Any]):
        """Generate improvement recommendations"""
        recommendations = []
        
        for category, data in results["categories"].items():
            if data["score"] < 95.0:
                if category == "code_quality":
                    recommendations.append("Enhance code quality with better type hints and documentation")
                elif category == "documentation":
                    recommendations.append("Expand documentation to meet enterprise standards")
                elif category == "testing":
                    recommendations.append("Increase test coverage and add more test cases")
        
        results["recommendations"] = recommendations

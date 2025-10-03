"""
Multi-LLM AI analysis module.
Provides insights from multiple AI personas using different LLM providers.
"""

from typing import Dict, List, Any, Optional
from enum import Enum
import json

from config import (
    OPENAI_API_KEY,
    ANTHROPIC_API_KEY,
    GOOGLE_CLOUD_PROJECT_ID,
    AI_PERSONAS
)


class LLMProvider(Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE_GEMINI = "google_gemini"


class AIAnalyzer:
    """
    Multi-persona AI analyzer that generates insights from different perspectives.
    """
    
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self.gemini_client = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize AI client connections."""
        if OPENAI_API_KEY:
            try:
                import openai
                self.openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
            except ImportError:
                print("OpenAI package not installed")
        
        if ANTHROPIC_API_KEY:
            try:
                import anthropic
                self.anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
            except ImportError:
                print("Anthropic package not installed")
        
        if GOOGLE_CLOUD_PROJECT_ID:
            try:
                from google.cloud import aiplatform
                aiplatform.init(project=GOOGLE_CLOUD_PROJECT_ID)
                self.gemini_client = True  # Simplified flag
            except ImportError:
                print("Google Cloud AI Platform package not installed")
    
    def _build_analysis_prompt(self, persona_key: str, data_summary: Dict[str, Any]) -> str:
        """
        Build a detailed prompt for AI analysis based on persona.
        """
        persona = AI_PERSONAS[persona_key]
        
        prompt = f"""You are analyzing financial and operational data from the perspective of a {persona['name']}.

Your perspective: {persona['perspective']}
Your focus areas: {persona['focus']}

Data Summary:
{json.dumps(data_summary, indent=2)}

Please provide:
1. Key observations from your perspective
2. Potential risks or opportunities you identify
3. Specific recommendations for action
4. Metrics or KPIs you would monitor closely

Keep your analysis concise but insightful, focusing on what matters most from your role's perspective.
"""
        return prompt
    
    def _call_openai(self, prompt: str, model: str = "gpt-4") -> str:
        """Call OpenAI API."""
        if not self.openai_client:
            return "OpenAI not configured"
        
        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert business analyst providing strategic insights."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error calling OpenAI: {str(e)}"
    
    def _call_anthropic(self, prompt: str, model: str = "claude-3-sonnet-20240229") -> str:
        """Call Anthropic Claude API."""
        if not self.anthropic_client:
            return "Anthropic not configured"
        
        try:
            message = self.anthropic_client.messages.create(
                model=model,
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text
        except Exception as e:
            return f"Error calling Anthropic: {str(e)}"
    
    def _call_gemini(self, prompt: str) -> str:
        """Call Google Gemini API."""
        if not self.gemini_client:
            return "Google Gemini not configured"
        
        try:
            from vertexai.preview.generative_models import GenerativeModel
            
            model = GenerativeModel("gemini-pro")
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error calling Gemini: {str(e)}"
    
    def analyze_from_persona(
        self, 
        persona_key: str, 
        data_summary: Dict[str, Any],
        provider: LLMProvider = LLMProvider.OPENAI
    ) -> Dict[str, Any]:
        """
        Generate analysis from a specific persona's perspective.
        
        Args:
            persona_key: Key from AI_PERSONAS config
            data_summary: Dictionary containing data to analyze
            provider: Which LLM provider to use
            
        Returns:
            Dictionary with persona info and analysis
        """
        if persona_key not in AI_PERSONAS:
            raise ValueError(f"Unknown persona: {persona_key}")
        
        persona = AI_PERSONAS[persona_key]
        prompt = self._build_analysis_prompt(persona_key, data_summary)
        
        # Call appropriate LLM
        if provider == LLMProvider.OPENAI:
            analysis = self._call_openai(prompt)
        elif provider == LLMProvider.ANTHROPIC:
            analysis = self._call_anthropic(prompt)
        elif provider == LLMProvider.GOOGLE_GEMINI:
            analysis = self._call_gemini(prompt)
        else:
            analysis = "Unknown provider"
        
        return {
            'persona': persona['name'],
            'perspective': persona['perspective'],
            'focus': persona['focus'],
            'analysis': analysis,
            'provider': provider.value
        }
    
    def generate_multi_persona_insights(
        self, 
        data_summary: Dict[str, Any],
        personas: Optional[List[str]] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Generate insights from multiple personas.
        
        Args:
            data_summary: Dictionary containing data to analyze
            personas: List of persona keys to use (defaults to all)
            
        Returns:
            Dictionary mapping persona keys to their analysis
        """
        if personas is None:
            personas = list(AI_PERSONAS.keys())
        
        insights = {}
        
        # Distribute personas across different LLM providers for diversity
        providers = [LLMProvider.OPENAI, LLMProvider.ANTHROPIC, LLMProvider.GOOGLE_GEMINI]
        
        for i, persona_key in enumerate(personas):
            provider = providers[i % len(providers)]
            
            # Skip if provider not configured
            if provider == LLMProvider.OPENAI and not self.openai_client:
                provider = LLMProvider.ANTHROPIC
            if provider == LLMProvider.ANTHROPIC and not self.anthropic_client:
                provider = LLMProvider.OPENAI
            
            insights[persona_key] = self.analyze_from_persona(
                persona_key, 
                data_summary, 
                provider
            )
        
        return insights
    
    def summarize_insights(self, insights: Dict[str, Dict[str, Any]]) -> str:
        """
        Create an executive summary from all persona insights.
        """
        summary_parts = ["=== MULTI-PERSONA AI ANALYSIS SUMMARY ===\n"]
        
        for persona_key, analysis in insights.items():
            summary_parts.append(f"\n--- {analysis['persona']} Perspective ---")
            summary_parts.append(f"Focus: {analysis['focus']}")
            summary_parts.append(f"\n{analysis['analysis']}\n")
        
        return "\n".join(summary_parts)


def analyze_data(data_summary: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to analyze data with all configured AI personas.
    """
    analyzer = AIAnalyzer()
    insights = analyzer.generate_multi_persona_insights(data_summary)
    summary = analyzer.summarize_insights(insights)
    
    return {
        'insights': insights,
        'summary': summary
    }

import google.generativeai as genai
import os
import json
from typing import Dict, Any
import logging
from datetime import datetime
import hashlib
import asyncio

logger = logging.getLogger(__name__)

class GeminiMarketInsights:
    """
    Market insights generator using Google's Gemini AI
    Analyzes demographic data to produce market insights
    """
    
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        genai.configure(api_key=api_key)
        
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config=genai.GenerationConfig(
                temperature=0.2,
                max_output_tokens=1500,
            )
        )
        
        self._cache = {}
    
    def _prepare_data_context(self, demographics_data: Dict[str, Any]) -> str:
        """Prepare demographic data context for Gemini"""
        radius_data = demographics_data.get("radius_data", {})
        
        # Organize data by radius
        context = {
            "current_demographics": {
                "1_mile": radius_data.get("1_mile", {}).get("current", {}),
                "3_mile": radius_data.get("3_mile", {}).get("current", {}), 
                "5_mile": radius_data.get("5_mile", {}).get("current", {})
            },
            "historical_demographics": {
                "1_mile": radius_data.get("1_mile", {}).get("historical", {}),
                "3_mile": radius_data.get("3_mile", {}).get("historical", {}),
                "5_mile": radius_data.get("5_mile", {}).get("historical", {})
            },
            "growth_metrics": demographics_data.get("growth_metrics", {}),
            "income_distribution": demographics_data.get("formatted_data", {}).get("income_distribution", {})
        }
        
        return json.dumps(context, indent=2)
    
    def _create_insights_prompt(self, data_context: str) -> str:
        """Create the prompt for Gemini"""
        return f"""You are an expert market analyst advising real estate developers and business investors. Analyze this demographic data to generate actionable market insights.

CONTEXT: Analyzing market area for development opportunities.
Format: Short, punchy insights that tell a story.
STRICT REQUIREMENTS:
1. Use ONLY the numbers and data provided - no external information
2. Focus on 5-mile radius data unless comparing across radii
3. Make insights actionable and business-focused
4. Keep each insight concise (under 60 characters)
5. Generate exactly 4 insights per category
6. Write like you're advising investors, not listing statistics

DEMOGRAPHIC DATA:
{data_context}

INTERPRETATION RULES:
- Transform raw numbers into market intelligence
- Focus on what the data MEANS for business decisions
- Connect multiple data points to reveal opportunities
- Use business-friendly language that investors understand
- Think: "What would a developer or retailer want to know?"

WRITING STYLE:
DON'T: "5-mile: 40714 bachelors degrees"
DO: "Highly educated market attracts premium retail"

DON'T: "Income growth: 77.46%"  
DO: "Rapidly gentrifying area (77% income surge)"

DON'T: "Median age 35.2 years"
DO: "Young professional hub drives tech demand"

ANALYSIS FRAMEWORK:
1. Demographic Strengths: What makes this market attractive for investment?
   - Look for: high income, education, growth rates, population density
   - Frame as: competitive advantages for businesses

2. Market Opportunities: What specific business opportunities exist?
   - Look for: underserved segments, growth trends, demographic gaps
   - Frame as: actionable development or business ideas

3. Target Demographics: Which customer segments should businesses focus on?
   - Look for: income brackets, age groups, household types
   - Frame as: specific customer personas businesses can target

OUTPUT FORMAT (JSON):
{{
  "demographic_strengths": [
    "Specific strength with number from data",
    "Another strength with metric",
    "Third strength with percentage",
    "Fourth strength with data point"
  ],
  "market_opportunities": [
    "Opportunity based on growth metric",
    "Market gap identified in data",
    "Trend-based opportunity",
    "Demographic opportunity"
  ],
  "target_demographics": [
    "Specific age/income segment",
    "Education-based segment",
    "Household type from data",
    "Geographic concentration"
  ]
}}

Remember: Write insights that would make an investor say "I need to act on this" not "interesting statistic"
"""
    
    def _create_cache_key(self, data_context: str) -> str:
        """Create cache key from data"""
        return hashlib.md5(data_context.encode()).hexdigest()[:16]
    
    def _parse_gemini_response(self, response_text: str) -> Dict[str, Any]:
        """Extract JSON from Gemini response"""
        response_text = response_text.strip()
        
        # Handle markdown code blocks
        if "```json" in response_text:
            start = response_text.find("```json") + 7
            end = response_text.find("```", start)
            response_text = response_text[start:end].strip()
        elif "```" in response_text:
            start = response_text.find("```") + 3
            end = response_text.find("```", start)
            response_text = response_text[start:end].strip()
        
        # Find JSON object
        start = response_text.find("{")
        end = response_text.rfind("}") + 1
        if start >= 0 and end > start:
            response_text = response_text[start:end]
        
        return json.loads(response_text)
    
    async def generate_insights_async(self, demographics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights asynchronously"""
        try:
            # Prepare data context
            data_context = self._prepare_data_context(demographics_data)
            
            # Check cache
            cache_key = self._create_cache_key(data_context)
            if cache_key in self._cache:
                logger.info(f"Returning cached Gemini insights")
                return self._cache[cache_key]
            
            # Generate prompt
            prompt = self._create_insights_prompt(data_context)
            
            # Call Gemini
            logger.info("Calling Gemini API for market insights")
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt
            )
            
            # Parse response
            insights = self._parse_gemini_response(response.text)
            
            # Validate structure
            for key in ["demographic_strengths", "market_opportunities", "target_demographics"]:
                if key not in insights or len(insights[key]) != 4:
                    raise ValueError(f"Invalid insights format for {key}")
            
            # Add metadata
            insights["insights_metadata"] = {
                "generated": True,
                "version": "1.0",
                "engine": "GeminiMarketInsights",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Cache result
            self._cache[cache_key] = insights
            
            return insights
            
        except Exception as e:
            logger.error(f"Gemini insights error: {str(e)}")
            return self._get_fallback_insights()
    
    def generate_insights(self, demographics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous wrapper for generate_insights_async"""
        try:
            # Try to get existing event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Can't use run_until_complete in running loop
                # Return fallback for now
                logger.warning("Cannot run async in current loop, using fallback")
                return self._get_fallback_insights()
            else:
                return loop.run_until_complete(self.generate_insights_async(demographics_data))
        except RuntimeError:
            # No event loop, create one
            return asyncio.run(self.generate_insights_async(demographics_data))
    
    def _get_fallback_insights(self) -> Dict[str, Any]:
        """Fallback insights when Gemini is unavailable"""
        return {
            "demographic_strengths": [
                "Market analysis in progress",
                "Data evaluation pending", 
                "Metrics under review",
                "Assessment ongoing"
            ],
            "market_opportunities": [
                "Opportunities being identified",
                "Market evaluation pending",
                "Analysis in progress",
                "Review underway"
            ],
            "target_demographics": [
                "Demographics being analyzed",
                "Segments under review",
                "Profiling in progress",
                "Assessment ongoing"
            ],
            "insights_metadata": {
                "generated": False,
                "version": "1.0",
                "engine": "GeminiMarketInsights",
                "error": "Fallback mode",
                "timestamp": datetime.utcnow().isoformat()
            }
        }


# Utility functions for easy integration
def generate_gemini_market_insights(demographics_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate market insights using Gemini (synchronous)"""
    try:
        generator = GeminiMarketInsights()
        return generator.generate_insights(demographics_data)
    except ValueError as e:
        logger.error(f"Gemini configuration error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return None


async def generate_gemini_market_insights_async(demographics_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate market insights using Gemini (asynchronous)"""
    try:
        generator = GeminiMarketInsights()
        return await generator.generate_insights_async(demographics_data)
    except ValueError as e:
        logger.error(f"Gemini configuration error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return None
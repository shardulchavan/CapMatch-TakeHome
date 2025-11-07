from typing import Dict, List, Any
import os
import logging

logger = logging.getLogger(__name__)

class MarketInsightsEngine:
    """
    Generates dynamic market insights based on demographic data
    Creates contextual strengths, opportunities, and target demographics
    """
    
    def __init__(self):
        # Thresholds for different market characteristics
        self.thresholds = {
            "high_income": 100000,
            "very_high_income": 150000,
            "high_growth": 10.0,
            "moderate_growth": 5.0,
            "high_education": 30.0,  # % with bachelor's or higher
            "young_population": 35,   # median age
            "mature_population": 45,
            "low_unemployment": 4.0,
            "very_low_unemployment": 3.0
        }
    
    def generate_insights(self, demographics_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Generate all insights based on demographics data
        Returns dict with strengths, opportunities, and demographics lists
        """
        # Extract key metrics from the data
        metrics = self._extract_metrics(demographics_data)
        
        return {
            "strengths": self._generate_strengths(metrics),
            "opportunities": self._generate_opportunities(metrics),
            "demographics": self._generate_target_demographics(metrics)
        }
    
    def _extract_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and calculate key metrics from raw demographics data"""
        metrics = {
            "population": {},
            "income": {},
            "growth": {},
            "employment": {},
            "education": {},
            "age": {}
        }
        
        # Get data for different radii
        radius_data = data.get("radius_data", {})
        
        # Population metrics
        for radius in ["1_mile", "3_mile", "5_mile"]:
            if radius in radius_data:
                current = radius_data[radius].get("current", {})
                
                # Handle both direct data and nested data structure
                if isinstance(current, dict):
                    if "data" in current:
                        current_data = current["data"]
                    else:
                        current_data = current
                else:
                    current_data = {}
                
                # Extract metrics
                pop = current_data.get("total_population", 0)
                metrics["population"][radius] = pop
                
                # Income - handle potentially aggregated values
                income = current_data.get("median_household_income", 0)
                # If income seems unreasonably high (>$1M), it might be aggregated
                if income > 1000000:
                    # Estimate based on typical values
                    income = income / (current_data.get("tract_count", 50))
                metrics["income"][radius] = income
                
                # Education percentage
                if pop > 0:
                    college_grads = sum([
                        current_data.get("bachelors_degree", 0),
                        current_data.get("masters_degree", 0),
                        current_data.get("professional_degree", 0),
                        current_data.get("doctorate_degree", 0)
                    ])
                    metrics["education"][radius] = (college_grads / pop) * 100
                else:
                    metrics["education"][radius] = 0
                
                # Age - handle aggregated median ages
                age = current_data.get("median_age", 0)
                if age > 100:  # Likely aggregated
                    age = age / (current_data.get("tract_count", 50))
                metrics["age"][radius] = age
                
                # Unemployment rate
                unemployment_rate = current_data.get("unemployment_rate", 0)
                if unemployment_rate == 0 and current_data.get("labor_force", 0) > 0:
                    unemployed = current_data.get("unemployed", 0)
                    labor_force = current_data.get("labor_force", 0)
                    unemployment_rate = (unemployed / labor_force) * 100
                metrics["employment"][radius] = unemployment_rate
        
        # Growth metrics
        growth_data = data.get("growth_metrics", {})
        metrics["growth"] = {
            "population": growth_data.get("population_growth", 0),
            "income": growth_data.get("income_growth", 0),
            "jobs": growth_data.get("job_growth", 0)
        }
        
        # Calculate income distribution percentages
        income_dist = data.get("formatted_data", {}).get("income_distribution", {})
        if income_dist and "Three Mile" in income_dist:
            dist = income_dist["Three Mile"]
            if len(dist) >= 4:
                metrics["income_distribution"] = {
                    "under_50k": dist[0],
                    "50k_100k": dist[1],
                    "100k_150k": dist[2],
                    "150k_plus": dist[3]
                }
        
        return metrics
    
    def _generate_strengths(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate market strengths based on metrics"""
        strengths = []
        
        # Population growth strength
        pop_growth = metrics["growth"]["population"]
        if pop_growth > self.thresholds["high_growth"]:
            strengths.append(f"Strong population growth ({pop_growth:.1f}% 5-year)")
        elif pop_growth > self.thresholds["moderate_growth"]:
            strengths.append(f"Steady population growth ({pop_growth:.1f}% 5-year)")
        
        # Income strength
        income_3mi = metrics["income"].get("3_mile", 0)
        if income_3mi > self.thresholds["very_high_income"]:
            strengths.append(f"Very high median income (${income_3mi/1000:.0f}K)")
        elif income_3mi > self.thresholds["high_income"]:
            strengths.append(f"High median income (${income_3mi/1000:.0f}K)")
        
        # Income growth
        income_growth = metrics["growth"]["income"]
        if income_growth > 20:
            strengths.append(f"Exceptional income growth ({income_growth:.1f}% 5-year)")
        elif income_growth > 10:
            strengths.append(f"Strong income growth ({income_growth:.1f}% 5-year)")
        
        # Education level
        edu_3mi = metrics["education"].get("3_mile", 0)
        if edu_3mi > 45:
            strengths.append(f"Highly educated population ({edu_3mi:.1f}% college+)")
        elif edu_3mi > self.thresholds["high_education"]:
            strengths.append(f"Well-educated workforce ({edu_3mi:.1f}% college+)")
        
        # Employment
        unemployment_3mi = metrics["employment"].get("3_mile", 100)
        if 0 < unemployment_3mi < self.thresholds["very_low_unemployment"]:
            strengths.append(f"Very low unemployment ({unemployment_3mi:.1f}%)")
        elif 0 < unemployment_3mi < self.thresholds["low_unemployment"]:
            strengths.append(f"Low unemployment rate ({unemployment_3mi:.1f}%)")
        
        # Population density
        pop_1mi = metrics["population"].get("1_mile", 0)
        pop_3mi = metrics["population"].get("3_mile", 0)
        if pop_1mi > 50000:
            strengths.append(f"High population density ({pop_1mi:,} in 1-mile)")
        
        # Job growth
        if metrics["growth"]["jobs"] > 15:
            strengths.append(f"Strong job growth ({metrics['growth']['jobs']:.1f}% 5-year)")
        
        # Age demographics
        age_3mi = metrics["age"].get("3_mile", 0)
        if 25 < age_3mi < self.thresholds["young_population"]:
            strengths.append("Young professional demographic")
        
        # Ensure we have at least 3 strengths
        if len(strengths) < 3:
            if pop_3mi > 100000:
                strengths.append(f"Large market area ({pop_3mi:,} population)")
            if metrics["growth"]["jobs"] > 0:
                strengths.append("Positive employment trends")
        
        return strengths[:4]  # Return top 4 strengths
    
    def _generate_opportunities(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate market opportunities based on metrics"""
        opportunities = []
        
        # High income opportunities
        income_dist = metrics.get("income_distribution", {})
        if income_dist.get("150k_plus", 0) > 30:
            opportunities.append("Large luxury/premium market segment")
        elif income_dist.get("100k_150k", 0) + income_dist.get("150k_plus", 0) > 40:
            opportunities.append("Strong upper-middle income market")
        
        # Growth-based opportunities
        if metrics["growth"]["population"] > 8 and metrics["growth"]["income"] > 15:
            opportunities.append("Expanding affluent population base")
        
        # Employment opportunities
        if metrics["growth"]["jobs"] > 5:
            opportunities.append("Growing employment base")
        elif 0 < metrics["employment"].get("3_mile", 100) < 4:
            opportunities.append("Strong job market attracting residents")
        
        # Age-based opportunities
        age_3mi = metrics["age"].get("3_mile", 0)
        if 25 < age_3mi < 35:
            opportunities.append("Tech-savvy millennial demographic")
        elif 35 <= age_3mi <= 45:
            opportunities.append("Prime spending demographic (35-45)")
        
        # Education-based opportunities
        if metrics["education"].get("3_mile", 0) > 40:
            opportunities.append("Educated consumer base values quality")
        
        # Income growth opportunities
        if metrics["growth"]["income"] > 25:
            opportunities.append("Rising disposable income")
        
        # Density opportunities
        pop_1mi = metrics["population"].get("1_mile", 1)
        pop_5mi = metrics["population"].get("5_mile", 1)
        if pop_1mi > 0 and pop_5mi > 0:
            density_ratio = (pop_1mi / pop_5mi) * 100
            if density_ratio > 15:
                opportunities.append("Dense urban core development")
        
        # Market size opportunities
        if metrics["population"].get("5_mile", 0) > 500000:
            opportunities.append("Large addressable market")
        
        # Tech sector opportunity (for Bay Area/tech hubs)
        if (metrics["income"].get("3_mile", 0) > 120000 and 
            metrics["education"].get("3_mile", 0) > 35):
            opportunities.append("Tech sector concentration")
        
        # Ensure we have at least 3 opportunities
        if len(opportunities) < 3:
            if metrics["growth"]["population"] > 0:
                opportunities.append("Growing retail/service demand")
            opportunities.append("Diverse demographic mix")
        
        return opportunities[:4]  # Return top 4 opportunities
    
    def _generate_target_demographics(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate target demographic descriptions"""
        demographics = []
        
        # Age-based demographics
        age_3mi = metrics["age"].get("3_mile", 40)
        if 25 < age_3mi < 30:
            demographics.append("Young professionals (25-34)")
        elif 28 < age_3mi < 38:
            demographics.append("Millennials (28-38)")
        elif 35 < age_3mi < 50:
            demographics.append("Gen X families (35-50)")
        elif age_3mi >= 45:
            demographics.append("Established households (45+)")
        
        # Income-based demographics
        income_3mi = metrics["income"].get("3_mile", 0)
        income_dist = metrics.get("income_distribution", {})
        
        if income_3mi > 150000:
            demographics.append("High-net-worth individuals")
        elif income_3mi > 100000:
            if income_dist.get("100k_150k", 0) > 15:
                demographics.append("Upper-middle income families")
            demographics.append("Affluent professionals")
        elif income_3mi > 75000:
            demographics.append("Middle-income households")
        
        # Education-based demographics
        edu_3mi = metrics["education"].get("3_mile", 0)
        if edu_3mi > 50:
            demographics.append("Advanced degree holders")
        elif edu_3mi > 35:
            demographics.append("College-educated workforce")
        
        # Employment-based demographics
        if metrics["growth"]["jobs"] > 10:
            demographics.append("Tech and finance workers")
        elif 0 < metrics["employment"].get("3_mile", 100) < 3:
            demographics.append("Dual-income households")
        
        # Lifestyle demographics
        if age_3mi < 35 and income_3mi > 80000:
            demographics.append("DINK couples (Double Income No Kids)")
        elif 35 < age_3mi < 45 and edu_3mi > 30:
            demographics.append("Family-oriented professionals")
        
        # Urban vs suburban
        pop_1mi = metrics["population"].get("1_mile", 0)
        if pop_1mi > 75000:
            demographics.append("Urban lifestyle enthusiasts")
        elif pop_1mi > 25000:
            demographics.append("Suburban commuters")
        
        # Remove duplicates and return top 4
        seen = set()
        unique_demographics = []
        for demo in demographics:
            if demo.lower() not in seen:
                seen.add(demo.lower())
                unique_demographics.append(demo)
        
        return unique_demographics[:4]
    
    def format_for_ui(self, insights: Dict[str, List[str]]) -> Dict[str, Any]:
        """Format insights for direct UI consumption"""
        return {
            "demographic_strengths": insights["strengths"],
            "market_opportunities": insights["opportunities"],
            "target_demographics": insights["demographics"],
            "insights_metadata": {
                "generated": True,
                "version": "1.0",
                "engine": "MarketInsightsEngine"
            }
        }


def generate_market_insights(demographics_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate market insights from demographics data
    Can be called from sync or async context
    """
    # Always try Gemini first
    try:
        # Import and use Gemini market insights
        from gemini_market_insights import generate_gemini_market_insights
        
        gemini_results = generate_gemini_market_insights(demographics_data)
        if gemini_results and gemini_results.get("insights_metadata", {}).get("generated"):
            logger.info("Successfully generated insights with Gemini")
            return gemini_results
        
    except ImportError:
        logger.error("Gemini market insights not available, using rule-based")
    except Exception as e:
        logger.error(f"Gemini insights failed: {e}, using rule-based")
    
    # Fallback to rule-based engine
    try:
        engine = MarketInsightsEngine()
        insights = engine.generate_insights(demographics_data)
        return engine.format_for_ui(insights)
    except Exception as e:
        logger.error(f"Error generating insights: {e}")
        return {
            "demographic_strengths": [
                "Data analysis in progress",
                "Market evaluation pending",
                "Demographics being analyzed"
            ],
            "market_opportunities": [
                "Market evaluation pending",
                "Opportunities being identified",
                "Analysis in progress"
            ],
            "target_demographics": [
                "Demographics being analyzed",
                "Segments under review",
                "Profiling in progress"
            ],
            "insights_metadata": {
                "generated": False,
                "version": "1.0",
                "error": str(e)
            }
        }
# CapMatch-TakeHomeCapMatch Market Intelligence System
🚀 What We Built

CapMatch Market Intelligence System is a lightning-fast demographic analysis tool that helps real estate developers and investors make data-driven decisions.
Give it any U.S. address, and within 30 seconds, you’ll receive comprehensive market insights powered by U.S. Census data and AI.

✨ The Magic Behind It
Here's How It Works

You Enter an Address
Example: 555 California St, San Francisco, CA

We Geocode It
Converts the address into coordinates using the Census Bureau’s geocoding service.

We Fetch Demographics
Pulls population, income, education, and employment data for 1, 3, and 5-mile radii.

AI Generates Insights
Google’s Gemini AI analyzes the data and produces actionable market intelligence.

You Get Beautiful Visualizations
Interactive maps, charts, and insights are displayed right in your browser.

🧰 Tech Stack
Backend (Python)

FastAPI for blazing-fast API endpoints

Census Bureau API for demographic data

Google Gemini AI for intelligent insights

Async/await everywhere for maximum speed

Frontend (React + TypeScript)

Clean, responsive UI built with Tailwind CSS

Interactive maps using Leaflet

Dynamic charts powered by Chart.js

Real-time data visualization

🛠️ Setting It Up
Prerequisites

Make sure you have these installed:

Python 3.10+

Node.js 16+

Git

Step 1: Clone the Repo
git clone https://github.com/your-org/capmatch-market-intelligence.git
cd capmatch-market-intelligence

Step 2: Backend Setup
# Navigate to backend
cd backend

# Create a virtual environment
python -m venv venv

# Activate it
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

Step 3: Set Up Your API Keys

Create a .env file in the backend directory:

# backend/.env
GEMINI_API_KEY=your_gemini_api_key_here
CENSUS_API_KEY=your_census_api_key_here  # Optional but recommended
USE_GEMINI_INSIGHTS=true

Getting API Keys

Gemini API: Go to Google AI Studio
 and create a free API key

Census API: Visit Census Bureau
 — free and instant!

Step 4: Frontend Setup
# From project root
cd frontend

# Install dependencies
npm install

Step 5: Fire It Up! 🔥
Start the Backend:
cd backend
python fastapi_app.py


You’ll see something like:

==============================
CapMatch Demographics Card API
==============================
Mode: Production
Census API Key: Configured
Server: http://localhost:8000
Docs: http://localhost:8000/docs
==============================

Start the Frontend:
# In a new terminal
cd frontend
npm start


Then visit http://localhost:3000
 — and you’re ready to go!

📊 Using the System
Quick Test

Go to http://localhost:3000

Enter an address like: 350 5th Ave, New York, NY 10118

Click "Analyze Market"

Watch the magic happen!

What You’ll See
🗺️ Demographics Card (First View)

Population circles on a mini-map

Key metrics: population, growth rate, education level

Click "View Full Analysis" for detailed insights

📈 Full Analysis Page

Population by radius (1, 3, 5 miles)

5-year growth trends

Income distribution charts

Education analysis

AI-generated market insights

Interactive population heatmap

📈 Understanding the Data
Population Metrics

Total population at different distances

Understand market density

Includes 5-year growth trends

Income Analysis

Median household income by radius

Income distribution (e.g., $50K vs. $150K+)

Income growth over 5 years

Market Insights (AI-Powered)

Demographic Strengths: What makes this area attractive

Market Opportunities: Business or investment opportunities

Target Demographics: Who to market to in this area

🏃‍♂️ Performance Optimizations

Optimized to run in under 30 seconds using:

Parallel Processing — Fetch data for all radii simultaneously

Smart Caching — Remember previously fetched data

Efficient Aggregation — Batch census tract processing

Fast AI Model — Uses Gemini 1.5 Flash for quick insights

🔧 Troubleshooting
Common Issues

❗ "Gemini not available, using rule-based insights"

Check your GEMINI_API_KEY in .env

Ensure google-generativeai is installed:

pip install google-generativeai


❗ "Census API returned status 400"

Verify your CENSUS_API_KEY

Or remove it to run without key

Check your internet connection

❗ Frontend won’t connect to backend

Ensure backend is running on port 8000

Check CORS settings if you’ve modified code
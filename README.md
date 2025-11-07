# 🧠 CapMatch Market Intelligence System

## 🚀 What We Built

**CapMatch Market Intelligence System** is a **lightning-fast demographic analysis tool** that helps **real estate developers and investors** make **data-driven decisions**.  
Give it any **U.S. address**, and within **30 seconds**, you’ll receive **comprehensive market insights** powered by **U.S. Census data** and **AI**.

---

## ✨ The Magic Behind It

### Here's How It Works

1. **You Enter an Address**  
   Example: `555 California St, San Francisco, CA`

2. **We Geocode It**  
   Converts the address into coordinates using the **Census Bureau’s geocoding service**.

3. **We Fetch Demographics**  
   Pulls **population, income, education, and employment data** for **1, 3, and 5-mile radii**.

4. **AI Generates Insights**  
   **Google’s Gemini AI** analyzes the data and produces **actionable market intelligence**.

5. **You Get Beautiful Visualizations**  
   Interactive **maps**, **charts**, and **insights** are displayed right in your browser.

---

## 🧰 Tech Stack

### **Backend (Python)**
- **FastAPI** for blazing-fast API endpoints  
- **Census Bureau API** for demographic data  
- **Google Gemini AI** for intelligent insights  
- **Async/await** everywhere for maximum speed  

### **Frontend (React + TypeScript)**
- Clean, responsive UI built with **Tailwind CSS**  
- **Interactive maps** using **Leaflet**  
- **Dynamic charts** powered by **Chart.js**  
- **Real-time data visualization**

---

## 🛠️ Setting It Up

### **Prerequisites**
Make sure you have these installed:
- **Python 3.10+**
- **Node.js 16+**
- **Git**

---

### **Step 1: Clone the Repo**

```bash
git clone https://github.com/your-org/capmatch-market-intelligence.git
cd capmatch-market-intelligence

### **Step 2: Backend Setup**
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
```

### **Step 3:Set Up Your API Keys**

Create a .env file in the backend directory:
```bash
# backend/.env
GEMINI_API_KEY=your_gemini_api_key_here
CENSUS_API_KEY=your_census_api_key_here  
```
### **Step 4:Frontend Setup**
```bash
# From project root
cd frontend

# Install dependencies
npm install
```
### **Step 5:Start the Backend**
```bash
cd backend
python fastapi_app.py
```

### **Step 5:Start the Frontend**
```bash
# In a new terminal
cd frontend
npm start
```

## 📊 Using the System

### 🧪 Quick Test

1. Go to [https://cap-match-take-home.vercel.app/](https://cap-match-take-home.vercel.app/)
2. Enter an address like: `350 5th Ave, New York, NY 10118`
3. Click **"Analyze Market"**
4. Watch the magic happen!

---

### 🗺️ What You’ll See

#### **Demographics Card (First View)**
- Population circles on a mini-map  
- Key metrics: population, growth rate, education level  
- Click **"View Full Analysis"** for detailed insights  

#### **Full Analysis Page**
- Population by radius (**1, 3, 5 miles**)  
- 5-year growth trends  
- Income distribution charts  
- Education analysis  
- **AI-generated market insights**  
- Interactive population **heatmap**

---

## 📈 Understanding the Data

### **Population Metrics**
- Total population at different distances  
- Understand **market density**  
- Includes **5-year growth trends**

### **Income Analysis**
- **Median household income** by radius  
- **Income distribution** (e.g., $50K vs. $150K+)  
- **Income growth** over 5 years  

### **Market Insights (AI-Powered)**
- **Demographic Strengths:** What makes this area attractive  
- **Market Opportunities:** Business or investment opportunities  
- **Target Demographics:** Who to market to in this area

## 📁 Project Structure
```
backend/
├── fastapi_app.py # Main API server
├── census_client.py # Census data fetching
├── census_geocoding_client.py # Address → Coordinates
├── radius_aggregator.py # Radius-based data aggregation
├── gemini_market_insights.py # AI insights generation
└── market_insights.py # Rule-based insights (fallback)

frontend/
├── components/
│ ├── SearchPage.tsx # Main search interface
│ ├── DemographicsCard.tsx # Summary card view
│ └── [other components] # Charts, maps, etc.
└── pages/
└── DemographicsDetail.tsx # Full analysis page
```



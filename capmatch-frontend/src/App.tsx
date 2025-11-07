import React from 'react';
import Chart from 'chart.js/auto';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import SearchPage from './components/SearchPage';
import DemographicsDetail from './pages/DemographicsDetail';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<SearchPage />} />
        <Route path="/analysis/:address" element={<DemographicsDetail />} />
      </Routes>
    </Router>
  );
}

export default App;
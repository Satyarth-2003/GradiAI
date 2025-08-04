import React from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import GradiAnalyzer from "./components/GradiAnalyzer";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<GradiAnalyzer />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
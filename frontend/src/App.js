// React app with dark-themed layout, full-page sections, and clean routing
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';
import AdminPage from './pages/AdminPage';
import ScanPage from './pages/ScanPage';
import TrackPage from './pages/TrackPage';
import HomePage from './pages/HomePage';

function App() {
  return (
    <Router>
      <div className="bg-dark text-white min-vh-100 d-flex flex-column">
        <header className="bg-gradient p-3 shadow-sm border-bottom border-light">
          <div className="container d-flex justify-content-between align-items-center">
            <h3 className="fw-bold text-white mb-0">GeoTrack</h3>
            <nav>
              <Link className="btn btn-sm btn-outline-light me-2" to="/">Home</Link>
              <Link className="btn btn-sm btn-outline-light me-2" to="/admin">Admin</Link>
              <Link className="btn btn-sm btn-outline-light me-2" to="/scan">Scan</Link>
              <Link className="btn btn-sm btn-outline-light" to="/track">Track</Link>
            </nav>
          </div>
        </header>

        <main className="flex-fill">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/admin" element={<AdminPage />} />
            <Route path="/scan" element={<ScanPage />} />
            <Route path="/track" element={<TrackPage />} />
          </Routes>
        </main>

        <footer className="text-center py-3 border-top border-light small">
          <span className="text-muted">© {new Date().getFullYear()} GeoTrack | ASU DDS Project</span>
        </footer>
      </div>
    </Router>
  );
}

export default App;
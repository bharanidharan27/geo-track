import React from 'react';
import { Link } from 'react-router-dom';

function HomePage() {
  return (
    <div className="d-flex flex-column justify-content-center align-items-center text-white bg-dark vh-100">
      <div className="text-center">
        <h1 className="display-3 fw-bold mb-3">📦 Welcome to GeoTrack</h1>
        <p className="lead">Effortless parcel tracking and logistics control with a distributed, real-time backend.</p>
        <div className="mt-4">
          <Link to="/admin" className="btn btn-warning btn-lg m-2">Admin Panel</Link>
          <Link to="/scan" className="btn btn-outline-light btn-lg m-2">Log Scan</Link>
          <Link to="/track" className="btn btn-primary btn-lg m-2">Track Parcel</Link>
        </div>
      </div>
    </div>
  );
}

export default HomePage;
import React, { useState } from 'react';

function ScanPage() {
  const [scan, setScan] = useState({ tracking_id: '', event_type: '', event_ts: '', facility_region: '', notes: '' });

  const handleTrackingId = (e) => {
    const tracking_id = e.target.value;
    const now = new Date();
    const isoString = now.toISOString().slice(0, 19);
    setScan((prev) => ({ ...prev, tracking_id, event_ts: isoString }));
  };

  const handleScan = async (e) => {
    e.preventDefault();
    const res = await fetch('http://localhost:8000/admin/scan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(scan)
    });
    const response = await res.json();
    alert(JSON.stringify(response));
  };

  return (
    <div className="d-flex flex-column justify-content-center align-items-center text-white bg-dark min-vh-100">
      <div className="text-center p-4" style={{ maxWidth: "600px", width: "100%" }}>
        <h2 className="mb-4">📍 Log Scan Event</h2>
        <form onSubmit={handleScan}>
          <input
            className="form-control mb-2"
            placeholder="Tracking ID"
            value={scan.tracking_id}
            onChange={handleTrackingId}
          />

          <select className="form-control mb-2" onChange={(e) => setScan({ ...scan, event_type: e.target.value })}>
            <option value="">Select Event Type</option>
            <option value="Package received at Store">Package received at Store</option>
            <option value="Package reached shipping facility">Package reached shipping facility</option>
            <option value="Package out in transit">Package out in transit</option>
            <option value="Package reached destination facility">Package reached destination facility</option>
            <option value="Package out of delivery">Package out of delivery</option>
            <option value="Package Delivered">Package Delivered</option>
          </select>

          <input
            className="form-control mb-2"
            placeholder="Timestamp"
            value={scan.event_ts}
            readOnly
          />

          <input
            className="form-control mb-2"
            placeholder="Facility Region"
            onChange={(e) => setScan({ ...scan, facility_region: e.target.value })}
          />
          <input
            className="form-control mb-3"
            placeholder="Notes (optional)"
            onChange={(e) => setScan({ ...scan, notes: e.target.value })}
          />
          <button className="btn btn-secondary w-100">Submit Scan Event</button>
        </form>
      </div>
    </div>
  );
}

export default ScanPage;
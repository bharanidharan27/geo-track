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

  const regionOptions = [
    'aws-us-east-1',
    'aws-us-west-2',
    'gcp-us-central1',
    'gcp-europe-west1',
    'azure-eastus',
    'azure-westus'
  ];

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
            <option value="handoff">handoff</option>
            <option value="arrival">arrival</option>
            <option value="departure">departure</option>
            <option value="out_for_delivery">out_for_delivery</option>
            <option value="delivered">delivered</option>
            <option value="exception">exception</option>
            <option value="rts">rts</option>
          </select>

          <input
            className="form-control mb-2"
            placeholder="Timestamp"
            value={scan.event_ts}
            readOnly
          />

          <select
            className="form-control mb-2"
            value={scan.facility_region}
            onChange={(e) => setScan({ ...scan, facility_region: e.target.value })}
          >
            <option value="">Select Facility Region</option>
            {regionOptions.map((region) => (
              <option key={region} value={region}>{region}</option>
            ))}
          </select>

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

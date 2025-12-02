import React, { useState } from 'react';

function TrackPage() {
  const [trackingID, setTrackingID] = useState('');
  const [result, setResult] = useState(null);

  const handleTrack = async (e) => {
    e.preventDefault();
    const res = await fetch(`http://localhost:8000/track/${trackingID}`);
    if (!res.ok) {
      alert("❌ Parcel not found");
      setResult(null);
      return;
    }
    const data = await res.json();
    setResult(data);
  };

  return (
    <div className="d-flex flex-column justify-content-center align-items-center text-white bg-dark min-vh-100">
      <div className="text-center p-4" style={{ maxWidth: "800px", width: "100%" }}>
        <h2 className="mb-4">📦 Track Parcel</h2>
        <form onSubmit={handleTrack} className="mb-4">
          <input className="form-control mb-3" placeholder="Enter Tracking ID" onChange={(e) => setTrackingID(e.target.value)} />
          <button className="btn btn-primary w-100">Track</button>
        </form>

        {result && (
          <div className="bg-light text-dark p-4 rounded">
            <h5>Status: {result.status}</h5>
            <h6>Current Region: {result.region}</h6>

            <hr />
            <h6 className="text-center">📍 Package Tracking Flow</h6>
            <ul className="timeline list-unstyled">
              {result.history.map((ev, i) => (
                <li key={i} className="mb-3">
                  <div className="fw-bold">{ev.event_type}</div>
                  <div className="small text-muted">
                    {ev.event_ts || ev.timestamp} — {ev.facility_region}
                  </div>
                  {ev.facility_location && (
                    <div className="text-muted">Location: {ev.facility_location}</div>
                  )}
                  {/* {ev.notes && <div className="fst-italic">{ev.notes}</div>} */}
                </li>
              ))}
            </ul>

            <hr />
            <h6 className="mt-4">📄 Scan History Table</h6>
            <table className="table table-striped">
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Event Type</th>
                  <th>Facility Region</th>
                  <th>Facility Location</th>
                  {/* <th>Notes</th> */}
                </tr>
              </thead>
              <tbody>
                {result.history.map((ev, i) => (
                  <tr key={i}>
                    <td>{ev.event_ts || ev.timestamp}</td>
                    <td>{ev.event_type}</td>
                    <td>{ev.facility_region || ev.location}</td>
                    <td>{ev.facility_location || '-'}</td>
                    {/* <td>{ev.notes || '-'}</td> */}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default TrackPage;
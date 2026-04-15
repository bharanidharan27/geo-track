import React, { useState } from 'react';

const statusLabels = {
  created: 'Created',
  in_transit: 'In Transit',
  out_for_delivery: 'Out for Delivery',
  delivered: 'Delivered',
  exception: 'Exception',
  failed_delivery: 'Delivery Attempt Failed',
  rts: 'Return to Sender',
};

function formatTimestamp(value) {
  if (!value) {
    return '-';
  }

  return new Date(value).toLocaleString();
}

function TrackPage() {
  const [trackingID, setTrackingID] = useState('');
  const [result, setResult] = useState(null);

  const handleTrack = async (e) => {
    e.preventDefault();
    const res = await fetch(`http://localhost:8000/track/${trackingID}`);
    if (!res.ok) {
      alert('Parcel not found');
      setResult(null);
      return;
    }

    const data = await res.json();
    setResult(data);
  };

  return (
    <div className="d-flex flex-column justify-content-center align-items-center text-white bg-dark min-vh-100">
      <div className="text-center p-4" style={{ maxWidth: '900px', width: '100%' }}>
        <h2 className="mb-4">Track Parcel</h2>
        <form onSubmit={handleTrack} className="mb-4">
          <input
            className="form-control mb-3"
            placeholder="Enter Tracking ID"
            onChange={(e) => setTrackingID(e.target.value)}
          />
          <button className="btn btn-primary w-100">Track</button>
        </form>

        {result && (
          <div className="bg-light text-dark p-4 rounded text-start">
            <h5>Status: {statusLabels[result.status] || result.status}</h5>
            <h6>Destination Region: {result.region}</h6>
            <div className="small text-muted mb-3">
              {result.source_location} to {result.destination_location}
            </div>

            <hr />
            <h6 className="text-center">Shipment Timeline</h6>
            <ul className="timeline list-unstyled">
              {result.history.map((ev) => (
                <li key={`${ev.sequence_no}-${ev.event_ts}-${ev.facility_id || 'facility'}`} className="mb-4 border-start border-2 ps-3">
                  <div className="fw-bold">{ev.event_label}</div>
                  {ev.event_message && <div>{ev.event_message}</div>}
                  <div className="small text-muted">{formatTimestamp(ev.event_ts)}</div>
                  <div className="small text-muted">
                    {ev.facility_location || '-'} | {ev.facility_region}
                  </div>
                  <div className="small text-muted">
                    Sequence {ev.sequence_no || '-'} | {ev.journey_stage || '-'} | {ev.facility_type || '-'}
                  </div>
                </li>
              ))}
            </ul>

            <hr />
            <h6 className="mt-4">Scan History Table</h6>
            <table className="table table-striped table-sm">
              <thead>
                <tr>
                  <th>Seq</th>
                  <th>Timestamp</th>
                  <th>Event</th>
                  <th>Journey Stage</th>
                  <th>Facility</th>
                  <th>Region</th>
                </tr>
              </thead>
              <tbody>
                {result.history.map((ev) => (
                  <tr key={`${ev.sequence_no}-${ev.event_ts}`}>
                    <td>{ev.sequence_no || '-'}</td>
                    <td>{formatTimestamp(ev.event_ts)}</td>
                    <td>{ev.event_label}</td>
                    <td>{ev.journey_stage || '-'}</td>
                    <td>{ev.facility_location || ev.facility_id || '-'}</td>
                    <td>{ev.facility_region || '-'}</td>
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

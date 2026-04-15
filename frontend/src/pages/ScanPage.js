import React, { useState } from 'react';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const eventOptions = [
  'order_submitted',
  'label_created',
  'picked_up',
  'arrived_origin_hub',
  'departed_origin_hub',
  'in_transit',
  'arrived_destination_hub',
  'arrived_delivery_station',
  'out_for_delivery',
  'delivered',
  'delay',
  'exception',
  'failed_delivery',
  'rts',
];

const regionOptions = [
  'aws-us-east-1',
  'aws-us-east-2',
  'aws-us-west-2',
  'aws-ap-south-1',
  'aws-ap-southeast-1',
];

function ScanPage() {
  const [scan, setScan] = useState({
    tracking_id: '',
    event_type: '',
    event_ts: '',
    facility_region: '',
    facility_location: '',
    facility_id: '',
    facility_type: '',
    sequence_no: '',
    journey_stage: '',
    event_message: '',
  });

  const handleTrackingId = (e) => {
    const tracking_id = e.target.value;
    const now = new Date();
    const isoString = now.toISOString().slice(0, 19);
    setScan((prev) => ({ ...prev, tracking_id, event_ts: isoString }));
  };

  const handleScan = async (e) => {
    e.preventDefault();
    try {
      const payload = {
        ...scan,
        sequence_no: scan.sequence_no ? Number(scan.sequence_no) : null,
      };

      const res = await fetch('http://localhost:8000/admin/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const data = await res.json();

      if (!res.ok) {
        if (res.status === 404) {
          toast.error('Tracking ID not found');
        } else {
          toast.error(`${data.detail || 'Scan failed'}`);
        }
        return;
      }

      toast.success(`Parcel successfully scanned at ${scan.facility_location || 'facility'}`);
    } catch (err) {
      toast.error('Network error while scanning');
    }
  };

  return (
    <div className="d-flex flex-column justify-content-center align-items-center text-white bg-dark min-vh-100">
      <ToastContainer position="top-center" autoClose={3000} />
      <div className="text-center p-4" style={{ maxWidth: '600px', width: '100%' }}>
        <h2 className="mb-4">Log Scan Event</h2>
        <form onSubmit={handleScan}>
          <input
            className="form-control mb-2"
            placeholder="Tracking ID"
            value={scan.tracking_id}
            onChange={handleTrackingId}
          />

          <select
            className="form-control mb-2"
            value={scan.event_type}
            onChange={(e) => setScan({ ...scan, event_type: e.target.value })}
          >
            <option value="">Select Event Type</option>
            {eventOptions.map((eventType) => (
              <option key={eventType} value={eventType}>
                {eventType}
              </option>
            ))}
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
              <option key={region} value={region}>
                {region}
              </option>
            ))}
          </select>

          <input
            className="form-control mb-2"
            placeholder="Facility Location"
            value={scan.facility_location}
            onChange={(e) => setScan({ ...scan, facility_location: e.target.value })}
          />

          <input
            className="form-control mb-2"
            placeholder="Facility ID"
            value={scan.facility_id}
            onChange={(e) => setScan({ ...scan, facility_id: e.target.value })}
          />

          <input
            className="form-control mb-2"
            placeholder="Facility Type"
            value={scan.facility_type}
            onChange={(e) => setScan({ ...scan, facility_type: e.target.value })}
          />

          <input
            className="form-control mb-2"
            placeholder="Sequence Number"
            value={scan.sequence_no}
            onChange={(e) => setScan({ ...scan, sequence_no: e.target.value })}
          />

          <input
            className="form-control mb-2"
            placeholder="Journey Stage"
            value={scan.journey_stage}
            onChange={(e) => setScan({ ...scan, journey_stage: e.target.value })}
          />

          <textarea
            className="form-control mb-3"
            placeholder="Event Message"
            rows="3"
            value={scan.event_message}
            onChange={(e) => setScan({ ...scan, event_message: e.target.value })}
          />

          <button className="btn btn-secondary w-100">Submit Scan Event</button>
        </form>
      </div>
    </div>
  );
}

export default ScanPage;

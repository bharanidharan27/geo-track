import React, { useState } from 'react';

function AdminPage() {
  const [account, setAccount] = useState({ name: '', tier: '', home_region: '' });
  const [carrier, setCarrier] = useState({ name: '', scac: '', contact_email: '' });
  const [parcel, setParcel] = useState({ tracking_id: '', account_id: '', carrier_id: '', destination_region: '' });

  const handleSubmit = async (endpoint, data) => {
    const res = await fetch(`http://localhost:8000/admin/${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    const response = await res.json();
    alert(JSON.stringify(response));
  };

  const carrierInfo = {
    UPS: { scac: "UPS1", contact_email: "support@ups.com" },
    USPS: { scac: "USPS1", contact_email: "support@usps.com" },
    FEDEX: { scac: "FDX1", contact_email: "support@fedex.com" },
    DHL: { scac: "DHL1", contact_email: "support@dhl.com" }
  };

  return (
    <div className="d-flex flex-column justify-content-center align-items-center text-white bg-dark min-vh-100">
      <div className="container p-4">
        <h2 className="text-center mb-4">🛠️ Admin Panel</h2>
        <div className="row">
          <div className="col-md-6">
            <h4 className="text-warning">Add Account</h4>
            <form onSubmit={(e) => { e.preventDefault(); handleSubmit('accounts', account); }}>
              <input className="form-control mb-2" placeholder="Name" onChange={(e) => setAccount({ ...account, name: e.target.value })} />
              <select className="form-control mb-2" onChange={(e) => setAccount({ ...account, tier: e.target.value })}>
                <option value="">Select Tier</option>
                <option value="free">Free</option>
                <option value="pro">Pro</option>
                <option value="enterprise">Enterprise</option>
              </select>
              <input className="form-control mb-3" placeholder="Home Region" onChange={(e) => setAccount({ ...account, home_region: e.target.value })} />
              <button className="btn btn-warning mb-4 w-100">Submit Account</button>
            </form>

            <h4 className="text-info">Add Carrier</h4>
            <form onSubmit={(e) => { e.preventDefault(); handleSubmit('carriers', carrier); }}>
              <select
                className="form-control mb-2"
                onChange={(e) => {
                  const name = e.target.value;
                  const details = carrierInfo[name] || { scac: '', contact_email: '' };
                  setCarrier({ name, ...details });
                }}
              >
                <option value="">Select Carrier</option>
                <option value="UPS">UPS</option>
                <option value="USPS">USPS</option>
                <option value="FEDEX">FEDEX</option>
                <option value="DHL">DHL</option>
              </select>
              <input
                className="form-control mb-2"
                placeholder="SCAC Code"
                value={carrier.scac}
                onChange={(e) => setCarrier({ ...carrier, scac: e.target.value })}
              />
              <input
                className="form-control mb-3"
                placeholder="Contact Email"
                value={carrier.contact_email}
                onChange={(e) => setCarrier({ ...carrier, contact_email: e.target.value })}
              />
              <button className="btn btn-info mb-4 w-100">Submit Carrier</button>
            </form>
          </div>

          <div className="col-md-6">
            <h4 className="text-success">Add Parcel</h4>
            <form onSubmit={(e) => { e.preventDefault(); handleSubmit('parcel', parcel); }}>
              <input className="form-control mb-2" placeholder="Tracking ID" onChange={(e) => setParcel({ ...parcel, tracking_id: e.target.value })} />
              <input className="form-control mb-2" placeholder="Account ID" onChange={(e) => setParcel({ ...parcel, account_id: e.target.value })} />
              <input className="form-control mb-2" placeholder="Carrier ID" onChange={(e) => setParcel({ ...parcel, carrier_id: e.target.value })} />
              <input className="form-control mb-3" placeholder="Destination Region" onChange={(e) => setParcel({ ...parcel, destination_region: e.target.value })} />
              <button className="btn btn-success w-100">Submit Parcel</button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AdminPage;
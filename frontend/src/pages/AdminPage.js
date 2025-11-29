import React, { useState } from 'react';

function AdminPage() {
  const [account, setAccount] = useState({ name: '', tier: '', home_region: '' });
  const [carrier, setCarrier] = useState({ name: '', scac: '', contact_email: '' });
  const [parcel, setParcel] = useState({
    tracking_id: '',
    account_id: '',
    carrier_id: '',
    origin_region: '',
    destination_region: ''
  });

  const [accountId, setAccountId] = useState('');
  const [carrierId, setCarrierId] = useState('');

  const regions = [
    "aws-us-west-2",
    "aws-us-east-1",
    "aws-us-east-2",
    "aws-ap-south-1",
    "aws-ap-southeast-1"
  ];

  const handleSubmit = async (endpoint, data) => {
    const res = await fetch(`http://localhost:8000/admin/${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    const response = await res.json();
    alert(JSON.stringify(response));

    if (endpoint === 'accounts' && response.account_id) {
      setAccountId(response.account_id);
      setParcel(prev => ({ ...prev, account_id: response.account_id }));
    } else if (endpoint === 'carriers' && response.carrier_id) {
      setCarrierId(response.carrier_id);
      setParcel(prev => ({ ...prev, carrier_id: response.carrier_id }));
    }
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
              <input
                className="form-control mb-2"
                placeholder="Name"
                onChange={(e) => setAccount({ ...account, name: e.target.value })}
              />
              <select className="form-control mb-2" onChange={(e) => setAccount({ ...account, tier: e.target.value })}>
                <option value="">Select Tier</option>
                <option value="free">Free</option>
                <option value="pro">Pro</option>
                <option value="enterprise">Enterprise</option>
              </select>
              <select
                className="form-control mb-3"
                onChange={(e) => setAccount({ ...account, home_region: e.target.value })}
              >
                <option value="">Select Home Region</option>
                {regions.map(region => (
                  <option key={region} value={region}>{region}</option>
                ))}
              </select>
              <button className="btn btn-warning mb-2 w-100">Submit Account</button>
            </form>
            {accountId && (
              <div className="alert alert-secondary mt-2">Account ID: <code>{accountId}</code></div>
            )}

            <h4 className="text-info mt-4">Add Carrier</h4>
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
              <button className="btn btn-info w-100">Submit Carrier</button>
            </form>
            {carrierId && (
              <div className="alert alert-secondary mt-2">Carrier ID: <code>{carrierId}</code></div>
            )}
          </div>

          <div className="col-md-6">
            <h4 className="text-success">Add Parcel</h4>
            <form onSubmit={(e) => { e.preventDefault(); handleSubmit('parcel', parcel); }}>
              <input
                className="form-control mb-2"
                placeholder="Tracking ID"
                onChange={(e) => setParcel({ ...parcel, tracking_id: e.target.value })}
              />
              <div className="form-control mb-2 bg-dark text-white border-secondary">
                Account ID: <code>{parcel.account_id || 'Not set yet'}</code>
              </div>
              <div className="form-control mb-2 bg-dark text-white border-secondary">
                Carrier ID: <code>{parcel.carrier_id || 'Not set yet'}</code>
              </div>
              <select
                className="form-control mb-2"
                onChange={(e) => setParcel({ ...parcel, origin_region: e.target.value })}
              >
                <option value="">Select Origin Region</option>
                {regions.map(region => (
                  <option key={region} value={region}>{region}</option>
                ))}
              </select>
              <select
                className="form-control mb-3"
                onChange={(e) => setParcel({ ...parcel, destination_region: e.target.value })}
              >
                <option value="">Select Destination Region</option>
                {regions.map(region => (
                  <option key={region} value={region}>{region}</option>
                ))}
              </select>
              <input
                className="form-control mb-2"
                placeholder="Source Location"
                onChange={(e) => setParcel({ ...parcel, source_location: e.target.value })}
              />
              <input
                className="form-control mb-3"
                placeholder="Destination Location"
                onChange={(e) => setParcel({ ...parcel, destination_location: e.target.value })}
              />
              <button className="btn btn-success w-100">Submit Parcel</button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AdminPage;
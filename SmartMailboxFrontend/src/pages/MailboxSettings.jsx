import React, { useState, useEffect } from 'react';
import { endpoints } from '../services/api';

const MailboxSettings = () => {
  const [mailboxes, setMailboxes] = useState([]);

  useEffect(() => {
    // Assumes you have an endpoint like GET /mailboxes/
    // You might need to add this to your services/api.js
    endpoints.fetchMailboxes().then(res => setMailboxes(res.data));
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-semibold text-gray-800">Connected Accounts</h2>
        <button className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700">
          + Connect New Mailbox
        </button>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Provider</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email Address</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Added On</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {mailboxes.map((box) => (
              <tr key={box.id}>
                <td className="px-6 py-4 capitalize text-gray-900">{box.provider}</td>
                <td className="px-6 py-4 text-gray-600 font-mono text-sm">{box.email_address}</td>
                <td className="px-6 py-4">
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    box.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {box.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-gray-400">
                   {new Date(box.created_at).toLocaleDateString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default MailboxSettings;

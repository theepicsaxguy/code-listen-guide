import React, { useState, useEffect } from 'react';
import { Check } from 'lucide-react';
import { useUser } from '../hooks';
import { PlanBadge } from './PlanBadge';

export const SettingsPage: React.FC = () => {
  const { data: user } = useUser();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [emailNotifications, setEmailNotifications] = useState(true);
  const [processingNotifications, setProcessingNotifications] = useState(true);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (user) {
      setName(user.name);
      setEmail(user.email);
    }
  }, [user]);

  const handleSave = () => {
    // TODO: Implement API call to update user settings
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  if (!user) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl space-y-6">
      <div className="bg-gray-800 rounded-xl overflow-hidden">
        <div className="p-6">
          <h2 className="text-xl font-semibold text-white">Profile Settings</h2>
        </div>
        <div className="p-6 space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Full Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-4 py-3 bg-gray-900 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Email Address</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-3 bg-gray-900 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm font-medium text-gray-300 mb-1">Current Plan</div>
              <PlanBadge plan={user.subscription_tier} />
            </div>
            <div className="text-sm text-gray-400">
              Member since {new Date(user.created_at).toLocaleDateString()}
            </div>
          </div>
        </div>
      </div>
      <div className="bg-gray-800 rounded-xl overflow-hidden">
        <div className="p-6">
          <h2 className="text-xl font-semibold text-white">Notification Preferences</h2>
        </div>
        <div className="p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm font-medium text-white mb-1">Email Notifications</div>
              <div className="text-xs text-gray-400">Receive updates about your account</div>
            </div>
            <button
              onClick={() => setEmailNotifications(!emailNotifications)}
              className={`relative w-12 h-6 rounded-full transition-colors ${emailNotifications ? 'bg-purple-500' : 'bg-gray-700'}`}
            >
              <div className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-transform ${emailNotifications ? 'translate-x-7' : 'translate-x-1'}`} />
            </button>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm font-medium text-white mb-1">Processing Notifications</div>
              <div className="text-xs text-gray-400">Get notified when audiobooks are complete</div>
            </div>
            <button
              onClick={() => setProcessingNotifications(!processingNotifications)}
              className={`relative w-12 h-6 rounded-full transition-colors ${processingNotifications ? 'bg-purple-500' : 'bg-gray-700'}`}
            >
              <div className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-transform ${processingNotifications ? 'translate-x-7' : 'translate-x-1'}`} />
            </button>
          </div>
        </div>
      </div>
      <div className="flex justify-end">
        <button
          onClick={handleSave}
          className="px-6 py-3 bg-purple-500 hover:bg-purple-600 text-white rounded-lg font-medium transition-colors flex items-center gap-2"
        >
          {saved ? (
            <>
              <Check size={18} />
              Saved!
            </>
          ) : (
            'Save Changes'
          )}
        </button>
      </div>
    </div>
  );
};

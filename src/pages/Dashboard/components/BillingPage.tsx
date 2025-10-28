import React from 'react';
import { CreditCard, Calendar, Download } from 'lucide-react';
import { useUser, usePaymentHistory } from '../hooks';
import type { Payment } from '../../../lib/types';

export const BillingPage: React.FC = () => {
  const { data: user } = useUser();
  const { data: paymentHistory, isLoading } = usePaymentHistory();

  if (!user) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
      </div>
    );
  }

  const payments = (paymentHistory as Payment[]) || [];

  // Calculate credits usage percentage
  // Note: This assumes credits_remaining is out of a total. Adjust based on actual API response
  const creditsUsed = 100 - (user.credits_remaining || 0); // Placeholder logic
  const creditsTotal = 100; // Placeholder - adjust based on actual plan
  const usagePercentage = (creditsUsed / creditsTotal) * 100;

  return (
    <div className="max-w-4xl space-y-6">
      <div className="bg-gray-800 border border-gray-700 rounded-xl p-8">
        <div className="flex items-start justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-white mb-2">
              {user.subscription_tier.charAt(0).toUpperCase() + user.subscription_tier.slice(1)} Plan
            </h2>
            <p className="text-gray-400">
              {user.subscription_status === 'active' ? 'Active subscription' : user.subscription_status}
            </p>
          </div>
          <button className="px-6 py-3 bg-purple-500 hover:bg-purple-600 text-white rounded-lg font-medium transition-colors">
            Upgrade Plan
          </button>
        </div>
        <div className="mb-6">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-medium text-gray-300">Credits Remaining</span>
            <span className="text-sm text-white font-medium">{user.credits_remaining}</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-3">
            <div
              className="bg-gradient-to-r from-purple-500 to-blue-500 h-3 rounded-full transition-all duration-300"
              style={{ width: `${100 - usagePercentage}%` }}
            />
          </div>
          <p className="text-xs text-gray-400 mt-2">Credits are replenished based on your plan</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 bg-gray-900 rounded-lg">
            <div className="text-2xl font-bold text-white mb-1">
              {user.subscription_tier === 'free' ? '10' : user.subscription_tier === 'professional' ? '100' : 'Unlimited'}
            </div>
            <div className="text-sm text-gray-400">Credits per month</div>
          </div>
          <div className="p-4 bg-gray-900 rounded-lg">
            <div className="text-2xl font-bold text-white mb-1">
              {user.subscription_tier === 'free' ? 'Public' : 'All'}
            </div>
            <div className="text-sm text-gray-400">Repository access</div>
          </div>
          <div className="p-4 bg-gray-900 rounded-lg">
            <div className="text-2xl font-bold text-white mb-1">
              {user.subscription_tier === 'enterprise' ? 'Priority' : 'Standard'}
            </div>
            <div className="text-sm text-gray-400">Processing queue</div>
          </div>
        </div>
      </div>
      <div className="bg-gray-800 border border-gray-700 rounded-xl overflow-hidden">
        <div className="p-6 border-b border-gray-700">
          <h3 className="text-lg font-semibold text-white">Payment History</h3>
        </div>
        {isLoading ? (
          <div className="flex items-center justify-center p-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500"></div>
          </div>
        ) : payments.length > 0 ? (
          <div className="divide-y divide-gray-700">
            {payments.map((payment) => (
              <div key={payment.id} className="p-6 flex items-center justify-between hover:bg-gray-750 transition-colors">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 bg-gray-900 rounded-lg flex items-center justify-center">
                    <Calendar size={20} className="text-gray-400" />
                  </div>
                  <div>
                    <div className="text-sm font-medium text-white mb-1">{payment.id}</div>
                    <div className="text-xs text-gray-400">
                      {new Date(payment.created_at).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric'
                      })}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-sm font-medium text-white">
                    ${(payment.amount_cents / 100).toFixed(2)}
                  </div>
                  <span
                    className={`px-3 py-1 rounded-full text-xs ${
                      payment.status === 'succeeded'
                        ? 'bg-green-500/20 border border-green-500/30 text-green-400'
                        : 'bg-gray-500/20 border border-gray-500/30 text-gray-400'
                    }`}
                  >
                    {payment.status}
                  </span>
                  <button className="p-2 hover:bg-gray-700 rounded-lg transition-colors" aria-label="Download Invoice">
                    <Download size={16} className="text-gray-400" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-12 text-center">
            <CreditCard size={48} className="text-gray-600 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-400 mb-2">No payment history</h3>
            <p className="text-sm text-gray-500">Your payments will appear here</p>
          </div>
        )}
      </div>
    </div>
  );
};

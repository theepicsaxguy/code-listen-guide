import React, { useState } from 'react';
import { CreditCard, Calendar, Download, Plus, FileText, DollarSign } from 'lucide-react';
import { useUser, usePaymentHistory } from '../hooks';
import type { Payment } from '../../../lib/types';


import { apiClient } from '../../../lib/api';

export const BillingPage: React.FC = () => {
  const { data: user } = useUser();
  const { data: paymentHistory, isLoading } = usePaymentHistory();
  const [showUpgradeDialog, setShowUpgradeDialog] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState('professional');

  if (!user) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  const payments = (paymentHistory?.payments as Payment[]) || [];

  // Calculate usage statistics
  const totalSpent = payments
    .filter(p => p.status === 'succeeded')
    .reduce((sum, p) => sum + p.amount_cents, 0);
  
  const currentMonth = new Date().getMonth();
  const currentYear = new Date().getFullYear();
  const monthlySpend = payments
    .filter(p => {
      const paymentDate = new Date(p.created_at);
      return p.status === 'succeeded' && 
             paymentDate.getMonth() === currentMonth && 
             paymentDate.getFullYear() === currentYear;
    })
    .reduce((sum, p) => sum + p.amount_cents, 0);

  const plans = [
    {
      id: 'free',
      name: 'Free',
      price: 0,
      credits: 10,
      features: ['Public repositories', 'Standard processing', 'Community support'],
    },
    {
      id: 'professional',
      name: 'Professional',
      price: 29,
      credits: 100,
      features: ['Private repositories', 'Priority processing', 'Email support', 'Advanced features'],
    },
    {
      id: 'team',
      name: 'Team',
      price: 99,
      credits: 500,
      features: ['Everything in Professional', 'Team collaboration', 'Shared workspaces', 'Priority support'],
    },
    {
      id: 'enterprise',
      name: 'Enterprise',
      price: null,
      credits: 'Unlimited',
      features: ['Everything in Team', 'Custom processing', 'Dedicated support', 'SLA guarantee', 'On-premise option'],
    },
  ];

  const currentPlan = plans.find(p => p.id === user.subscription_tier) || plans[0];

  const handleUpgrade = async () => {
    if (selectedPlan === 'enterprise') {
      // Handle enterprise contact form
      return;
    }
    try {
      const successUrl = new URL('/dashboard/billing?upgrade=success', window.location.origin).toString();
      const cancelUrl = new URL('/dashboard/billing', window.location.origin).toString();
      const session = await apiClient.createCheckoutSession(selectedPlan, successUrl, cancelUrl);
      if (session.url) {
        window.location.href = session.url;
      }
    } catch (error) {
      console.error("Failed to create checkout session", error);
    }
  };

  return (
    <div className="max-w-6xl space-y-6">
      {/* Current Plan Overview */}
      <div className="bg-gray-800 border border-gray-700 rounded-xl overflow-hidden">
        <div className="p-6 border-b border-gray-700">
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-xl font-semibold text-white">
                {currentPlan.name} Plan
              </h2>
              <p className="text-sm text-gray-400">
                {user.subscription_status === 'active' ? 'Active subscription' : user.subscription_status}
              </p>
            </div>
            {user.subscription_tier !== 'enterprise' && (
              <button onClick={() => setShowUpgradeDialog(true)} className="px-4 py-2 bg-purple-500 hover:bg-purple-600 text-white rounded-lg font-medium transition-colors flex items-center gap-2">
                <Plus className="mr-2 h-4 w-4" />
                Upgrade Plan
              </button>
            )}
          </div>
        </div>
        <div className="p-6 space-y-6">
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-400">Credits Remaining</span>
              <span className="font-medium text-white">{user.credits_remaining}</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-3">
              <div
                className="bg-purple-500 h-3 rounded-full transition-all duration-300"
                style={{ width: `${Math.min((user.credits_remaining / (typeof currentPlan.credits === 'number' ? currentPlan.credits : 100)) * 100, 100)}%` }}
              />
            </div>
            <p className="text-xs text-gray-400">
              {typeof currentPlan.credits === 'number' ? `${currentPlan.credits} credits per month` : 'Unlimited credits'}
            </p>
          </div>

          <hr className="border-gray-700" />

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 bg-gray-800 rounded-lg border border-gray-700">
              <div className="flex items-center gap-2 mb-2">
                <CreditCard className="h-4 w-4 text-gray-400" />
                <span className="text-sm text-gray-400">Monthly Credits</span>
              </div>
              <div className="text-2xl font-bold text-white">
                {typeof currentPlan.credits === 'number' ? currentPlan.credits : 'Unlimited'}
              </div>
            </div>
            <div className="p-4 bg-gray-800 rounded-lg border border-gray-700">
              <div className="flex items-center gap-2 mb-2">
                <DollarSign className="h-4 w-4 text-gray-400" />
                <span className="text-sm text-gray-400">This Month</span>
              </div>
              <div className="text-2xl font-bold text-white">
                ${(monthlySpend / 100).toFixed(2)}
              </div>
            </div>
            <div className="p-4 bg-gray-800 rounded-lg border border-gray-700">
              <div className="flex items-center gap-2 mb-2">
                <FileText className="h-4 w-4 text-gray-400" />
                <span className="text-sm text-gray-400">Total Spent</span>
              </div>
              <div className="text-2xl font-bold text-white">
                ${(totalSpent / 100).toFixed(2)}
              </div>
            </div>
          </div>
      </div>

      {/* Payment History */}
      <div className="bg-gray-800 border border-gray-700 rounded-xl overflow-hidden">
        <div className="p-6 border-b border-gray-700">
          <h2 className="text-xl font-semibold text-white">Payment History</h2>
          <p className="text-sm text-gray-400">View and download past invoices</p>
        </div>
        <div className="p-6">
          {isLoading ? (
            <div className="flex items-center justify-center p-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500"></div>
            </div>
          ) : payments.length > 0 ? (
            <div className="divide-y divide-gray-700">
              {payments.map((payment) => (
                <div key={payment.id} className="py-4 flex items-center justify-between hover:bg-gray-700 px-2 rounded transition-colors">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 bg-gray-700 rounded-lg flex items-center justify-center">
                      <Calendar className="h-5 w-5 text-gray-400" />
                    </div>
                    <div>
                      <div className="text-sm font-medium text-white">Invoice #{payment.id.slice(0, 8)}</div>
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
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${payment.status === 'succeeded' ? 'bg-green-500 text-white' : 'bg-gray-600 text-gray-300'}`}
                    >
                      {payment.status}
                    </span>
                    <button className="p-2 rounded-md text-gray-400 hover:bg-gray-700">
                      <Download className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-12 text-center">
              <CreditCard className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-white mb-2">No payment history</h3>
              <p className="text-sm text-gray-400">Your payments will appear here</p>
            </div>
          )}
        </div>
        </div>
      </div>

      {/* Upgrade Dialog */}
      {showUpgradeDialog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80">
          <div className="relative w-full max-w-4xl max-h-[90vh] overflow-y-auto bg-gray-800 border border-gray-700 rounded-xl shadow-lg">
            <div className="p-6 border-b border-gray-700">
              <h2 className="text-xl font-semibold text-white">Upgrade Your Plan</h2>
              <p className="text-sm text-gray-400">Choose a plan that fits your needs</p>
            </div>

            <div className="p-6 grid gap-4">
              {plans.filter(p => p.id !== 'free').map((plan) => (
                <label
                  key={plan.id}
                  className="flex items-start p-4 border border-gray-700 rounded-lg cursor-pointer hover:bg-gray-700 transition-colors"
                  htmlFor={plan.id}
                >
                  <input
                    type="radio"
                    id={plan.id}
                    name="plan"
                    value={plan.id}
                    checked={selectedPlan === plan.id}
                    onChange={() => setSelectedPlan(plan.id)}
                    className="mt-1 h-4 w-4 text-purple-500 focus:ring-purple-500 border-gray-600"
                  />
                  <div className="ml-4 flex-1">
                    <div className="flex items-center justify-between mb-2">
                      <div className="font-semibold text-lg text-white">{plan.name}</div>
                      <div className="text-2xl font-bold text-white">
                        {plan.price ? `$${plan.price}/mo` : 'Contact us'}
                      </div>
                    </div>
                    <p className="text-sm text-gray-400 mb-3">
                      {typeof plan.credits === 'number' ? `${plan.credits} credits per month` : 'Unlimited credits'}
                    </p>
                    <ul className="space-y-1">
                      {plan.features.map((feature, idx) => (
                        <li key={idx} className="text-sm flex items-center gap-2 text-gray-300">
                          <span className="text-purple-500">✓</span>
                          {feature}
                        </li>
                      ))}
                    </ul>
                  </div>
                </label>
              ))}
            </div>

            <div className="p-6 flex justify-end space-x-2 border-t border-gray-700">
              <button onClick={() => setShowUpgradeDialog(false)} className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg font-medium transition-colors">
                Cancel
              </button>
              <button onClick={handleUpgrade} className="px-4 py-2 bg-purple-500 hover:bg-purple-600 text-white rounded-lg font-medium transition-colors">
                {selectedPlan === 'enterprise' ? 'Contact Sales' : 'Upgrade Now'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

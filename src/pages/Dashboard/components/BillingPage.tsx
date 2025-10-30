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
  const [showUpgradeSuccess, setShowUpgradeSuccess] = useState(false);

  // Check for upgrade success in URL
  React.useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('upgrade') === 'success') {
      setShowUpgradeSuccess(true);
      // Clean up URL
      params.delete('upgrade');
      const newSearch = params.toString();
      const newUrl = newSearch ? `?${newSearch}` : window.location.pathname;
      window.history.replaceState({}, '', newUrl);
      // Hide success message after 5 seconds
      setTimeout(() => setShowUpgradeSuccess(false), 5000);
    }
  }, []);

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
      // Ensure we're on the billing tab when upgrade is clicked
      const successUrl = new URL(window.location.origin + '/dashboard');
      successUrl.searchParams.set('tab', 'billing');
      successUrl.searchParams.set('upgrade', 'success');
      
      const cancelUrl = new URL(window.location.origin + '/dashboard');
      cancelUrl.searchParams.set('tab', 'billing');
      
      const session = await apiClient.createCheckoutSession(
        selectedPlan,
        successUrl.toString(),
        cancelUrl.toString()
      );
      if (session.url) {
        window.location.href = session.url;
      }
    } catch (error) {
      console.error("Failed to create checkout session", error);
      alert("Failed to create checkout session. Please try again.");
    }
  };

  return (
    <div className="max-w-6xl space-y-6">
      {/* Success Message */}
      {showUpgradeSuccess && (
        <div className="bg-success/20 border border-success/30 text-success px-6 py-4 rounded-xl flex items-center justify-between animate-slide-down">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-success/30 rounded-full flex items-center justify-center">
              <span className="text-lg">✓</span>
            </div>
            <div>
              <div className="font-bold">Upgrade Successful!</div>
              <div className="text-sm opacity-90">Your subscription has been upgraded successfully.</div>
            </div>
          </div>
          <button
            onClick={() => setShowUpgradeSuccess(false)}
            className="text-success hover:text-success/80 transition-colors"
          >
            ✕
          </button>
        </div>
      )}

      {/* Current Plan Overview */}
      <div className="bg-gradient-card-primary rounded-xl overflow-hidden card-elevation">
        <div className="p-6 bg-gradient-to-r from-primary/10 to-accent/8">
          <div className="flex items-start justify-between">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <div className="w-10 h-10 rounded-xl bg-gradient-primary/20 flex items-center justify-center shadow-md shadow-primary/10">
                  <CreditCard className="h-5 w-5 icon-gradient" />
                </div>
                <h2 className="text-2xl font-bold text-foreground">
                  {currentPlan.name} Plan
                </h2>
              </div>
              <p className="text-sm text-muted-foreground font-medium ml-[52px]">
                {user.subscription_status === 'active' ? 'Active subscription' : user.subscription_status}
              </p>
            </div>
            {user.subscription_tier !== 'enterprise' && (
              <button 
                onClick={() => setShowUpgradeDialog(true)} 
                className="px-6 py-3 bg-gradient-primary hover:opacity-90 text-primary-foreground rounded-xl font-bold transition-all shadow-lg shadow-primary/20 hover:shadow-xl hover:shadow-primary/30 hover:-translate-y-0.5 flex items-center gap-2"
              >
                <Plus className="h-5 w-5" />
                Upgrade Plan
              </button>
            )}
          </div>
        </div>
        <div className="p-6 space-y-6">
          <div className="space-y-3">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground font-semibold">Credits Remaining</span>
              <span className="font-bold text-foreground text-lg">{user.credits_remaining}</span>
            </div>
            <div className="w-full bg-muted/50 rounded-full h-3 overflow-hidden">
              <div
                className="bg-gradient-primary h-full rounded-full transition-all duration-500 shadow-sm shadow-primary/30"
                style={{ width: `${Math.min((user.credits_remaining / (typeof currentPlan.credits === 'number' ? currentPlan.credits : 100)) * 100, 100)}%` }}
              />
            </div>
            <p className="text-xs text-muted-foreground font-medium">
              {typeof currentPlan.credits === 'number' ? `${currentPlan.credits} credits per month` : 'Unlimited credits'}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-6">
            <div className="p-5 bg-gradient-stat rounded-xl hover-card">
              <div className="flex items-center gap-2.5 mb-3">
                <CreditCard className="h-5 w-5 text-primary" />
                <span className="text-sm text-muted-foreground font-semibold">Monthly Credits</span>
              </div>
              <div className="text-3xl font-bold text-foreground">
                {typeof currentPlan.credits === 'number' ? currentPlan.credits : '∞'}
              </div>
            </div>
            <div className="p-5 bg-gradient-stat rounded-xl hover-card">
              <div className="flex items-center gap-2.5 mb-3">
                <DollarSign className="h-5 w-5 text-success" />
                <span className="text-sm text-muted-foreground font-semibold">This Month</span>
              </div>
              <div className="text-3xl font-bold text-foreground">
                ${(monthlySpend / 100).toFixed(2)}
              </div>
            </div>
            <div className="p-5 bg-gradient-stat rounded-xl hover-card">
              <div className="flex items-center gap-2.5 mb-3">
                <FileText className="h-5 w-5 text-accent" />
                <span className="text-sm text-muted-foreground font-semibold">Total Spent</span>
              </div>
              <div className="text-3xl font-bold text-foreground">
                ${(totalSpent / 100).toFixed(2)}
              </div>
            </div>
          </div>
      </div>

      {/* Payment History */}
      <div className="bg-gradient-card-accent rounded-xl overflow-hidden card-elevation">
        <div className="p-6 bg-gradient-to-r from-accent/10 to-primary/8">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-accent/20 flex items-center justify-center shadow-md shadow-accent/10">
              <Calendar className="h-5 w-5 icon-gradient-accent" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-foreground">Payment History</h2>
              <p className="text-sm text-muted-foreground font-medium mt-1">View and download past invoices</p>
            </div>
          </div>
        </div>
        <div className="p-6">
          {isLoading ? (
            <div className="flex items-center justify-center p-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          ) : payments.length > 0 ? (
            <div className="space-y-2">
              {payments.map((payment) => (
                <div key={payment.id} className="py-4 flex items-center justify-between hover:bg-primary/5 px-3 rounded-xl transition-all hover-card">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-gradient-primary/30 rounded-xl flex items-center justify-center">
                      <Calendar className="h-6 w-6 text-primary" />
                    </div>
                    <div>
                      <div className="text-sm font-bold text-foreground">Invoice #{payment.id.slice(0, 8)}</div>
                      <div className="text-xs text-muted-foreground font-medium mt-1">
                        {new Date(payment.created_at).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric'
                        })}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-base font-bold text-foreground">
                      ${(payment.amount_cents / 100).toFixed(2)}
                    </div>
                    <span
                      className={`inline-flex items-center px-3 py-1.5 rounded-full text-xs font-bold ${
                        payment.status === 'succeeded' 
                          ? 'bg-success/20 text-success' 
                          : 'bg-destructive/20 text-destructive'
                      }`}
                    >
                      {payment.status}
                    </span>
                    <button className="p-2.5 rounded-xl text-muted-foreground hover:text-primary hover:bg-primary/10 transition-all">
                      <Download className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-12 text-center bg-secondary/30 rounded-xl">
              <div className="w-16 h-16 bg-secondary/50 rounded-full flex items-center justify-center mx-auto mb-4">
                <CreditCard className="h-8 w-8 text-muted-foreground" />
              </div>
              <h3 className="text-xl font-bold text-foreground mb-2">No payment history</h3>
              <p className="text-sm text-muted-foreground">Your payments will appear here</p>
            </div>
          )}
        </div>
        </div>
      </div>

      {/* Upgrade Dialog */}
      {showUpgradeDialog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm">
          <div className="relative w-full max-w-4xl max-h-[90vh] overflow-y-auto bg-gradient-card-primary rounded-xl shadow-2xl card-elevation">
            <div className="p-6 bg-gradient-to-r from-primary/15 to-accent/12">
              <h2 className="text-2xl font-bold text-foreground">Upgrade Your Plan</h2>
              <p className="text-sm text-muted-foreground mt-1 font-medium">Choose a plan that fits your needs</p>
            </div>

            <div className="p-6 grid gap-4">
              {plans.filter(p => p.id !== 'free').map((plan) => (
                <label
                  key={plan.id}
                  className={`flex items-start p-5 rounded-xl cursor-pointer bg-card/70 hover:bg-primary/10 transition-all hover-card ${
                    selectedPlan === plan.id ? 'bg-primary/10 ring-2 ring-primary' : ''
                  }`}
                  htmlFor={plan.id}
                >
                  <input
                    type="radio"
                    id={plan.id}
                    name="plan"
                    value={plan.id}
                    checked={selectedPlan === plan.id}
                    onChange={() => setSelectedPlan(plan.id)}
                    className="mt-1 h-5 w-5 text-primary focus:ring-primary accent-primary"
                  />
                  <div className="ml-4 flex-1">
                    <div className="flex items-center justify-between mb-2">
                      <div className="font-bold text-xl text-foreground">{plan.name}</div>
                      <div className="text-3xl font-bold gradient-text-primary">
                        {plan.price ? `$${plan.price}/mo` : 'Contact us'}
                      </div>
                    </div>
                    <p className="text-sm text-muted-foreground mb-3 font-medium">
                      {typeof plan.credits === 'number' ? `${plan.credits} credits per month` : 'Unlimited credits'}
                    </p>
                    <ul className="space-y-2">
                      {plan.features.map((feature, idx) => (
                        <li key={idx} className="text-sm flex items-center gap-2 text-foreground font-medium">
                          <span className="text-success text-lg">✓</span>
                          {feature}
                        </li>
                      ))}
                    </ul>
                  </div>
                </label>
              ))}
            </div>

            <div className="p-6 flex justify-end space-x-3 bg-gradient-to-r from-secondary/5 to-muted/5">
              <button 
                onClick={() => setShowUpgradeDialog(false)} 
                className="px-6 py-3 bg-secondary/50 hover:bg-secondary text-foreground rounded-xl font-semibold transition-all"
              >
                Cancel
              </button>
              <button 
                onClick={handleUpgrade} 
                className="px-6 py-3 bg-gradient-primary hover:opacity-90 text-primary-foreground rounded-xl font-bold transition-all shadow-lg shadow-primary/20 hover:shadow-xl hover:shadow-primary/30"
              >
                {selectedPlan === 'enterprise' ? 'Contact Sales' : 'Upgrade Now'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

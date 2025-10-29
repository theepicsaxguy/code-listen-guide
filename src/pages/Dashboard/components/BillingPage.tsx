import React, { useState } from 'react';
import { CreditCard, Calendar, Download, Plus, FileText, DollarSign } from 'lucide-react';
import { useUser, usePaymentHistory } from '../hooks';
import type { Payment } from '../../../lib/types';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';

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

  const payments = (paymentHistory as Payment[]) || [];

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

  const handleUpgrade = () => {
    // TODO: Implement Stripe checkout integration
    console.log('Upgrading to:', selectedPlan);
    setShowUpgradeDialog(false);
    // This would typically create a Stripe checkout session
  };

  return (
    <div className="max-w-6xl space-y-6">
      {/* Current Plan Overview */}
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div>
              <CardTitle className="text-2xl">
                {currentPlan.name} Plan
              </CardTitle>
              <CardDescription>
                {user.subscription_status === 'active' ? 'Active subscription' : user.subscription_status}
              </CardDescription>
            </div>
            {user.subscription_tier !== 'enterprise' && (
              <Button onClick={() => setShowUpgradeDialog(true)}>
                <Plus className="mr-2 h-4 w-4" />
                Upgrade Plan
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Credits Remaining</span>
              <span className="font-medium">{user.credits_remaining}</span>
            </div>
            <div className="w-full bg-muted rounded-full h-3">
              <div
                className="bg-gradient-to-r from-primary to-primary/70 h-3 rounded-full transition-all duration-300"
                style={{ width: `${Math.min((user.credits_remaining / (typeof currentPlan.credits === 'number' ? currentPlan.credits : 100)) * 100, 100)}%` }}
              />
            </div>
            <p className="text-xs text-muted-foreground">
              {typeof currentPlan.credits === 'number' ? `${currentPlan.credits} credits per month` : 'Unlimited credits'}
            </p>
          </div>

          <Separator />

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 bg-muted/50 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <CreditCard className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm text-muted-foreground">Monthly Credits</span>
              </div>
              <div className="text-2xl font-bold">
                {typeof currentPlan.credits === 'number' ? currentPlan.credits : 'Unlimited'}
              </div>
            </div>
            <div className="p-4 bg-muted/50 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <DollarSign className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm text-muted-foreground">This Month</span>
              </div>
              <div className="text-2xl font-bold">
                ${(monthlySpend / 100).toFixed(2)}
              </div>
            </div>
            <div className="p-4 bg-muted/50 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <FileText className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm text-muted-foreground">Total Spent</span>
              </div>
              <div className="text-2xl font-bold">
                ${(totalSpent / 100).toFixed(2)}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Payment History */}
      <Card>
        <CardHeader>
          <CardTitle>Payment History</CardTitle>
          <CardDescription>View and download past invoices</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center p-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          ) : payments.length > 0 ? (
            <div className="divide-y divide-border">
              {payments.map((payment) => (
                <div key={payment.id} className="py-4 flex items-center justify-between hover:bg-muted/50 px-2 rounded transition-colors">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 bg-muted rounded-lg flex items-center justify-center">
                      <Calendar className="h-5 w-5 text-muted-foreground" />
                    </div>
                    <div>
                      <div className="text-sm font-medium">Invoice #{payment.id.slice(0, 8)}</div>
                      <div className="text-xs text-muted-foreground">
                        {new Date(payment.created_at).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric'
                        })}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-sm font-medium">
                      ${(payment.amount_cents / 100).toFixed(2)}
                    </div>
                    <Badge
                      variant={payment.status === 'succeeded' ? 'default' : 'secondary'}
                    >
                      {payment.status}
                    </Badge>
                    <Button variant="ghost" size="sm">
                      <Download className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-12 text-center">
              <CreditCard className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-medium mb-2">No payment history</h3>
              <p className="text-sm text-muted-foreground">Your payments will appear here</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Upgrade Dialog */}
      <Dialog open={showUpgradeDialog} onOpenChange={setShowUpgradeDialog}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Upgrade Your Plan</DialogTitle>
            <DialogDescription>
              Choose a plan that fits your needs
            </DialogDescription>
          </DialogHeader>

          <RadioGroup value={selectedPlan} onValueChange={setSelectedPlan} className="grid gap-4">
            {plans.filter(p => p.id !== 'free').map((plan) => (
              <Label
                key={plan.id}
                className="flex items-start p-4 border rounded-lg cursor-pointer hover:bg-muted/50 transition-colors"
                htmlFor={plan.id}
              >
                <RadioGroupItem value={plan.id} id={plan.id} className="mt-1" />
                <div className="ml-4 flex-1">
                  <div className="flex items-center justify-between mb-2">
                    <div className="font-semibold text-lg">{plan.name}</div>
                    <div className="text-2xl font-bold">
                      {plan.price ? `$${plan.price}/mo` : 'Contact us'}
                    </div>
                  </div>
                  <p className="text-sm text-muted-foreground mb-3">
                    {typeof plan.credits === 'number' ? `${plan.credits} credits per month` : 'Unlimited credits'}
                  </p>
                  <ul className="space-y-1">
                    {plan.features.map((feature, idx) => (
                      <li key={idx} className="text-sm flex items-center gap-2">
                        <span className="text-primary">✓</span>
                        {feature}
                      </li>
                    ))}
                  </ul>
                </div>
              </Label>
            ))}
          </RadioGroup>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowUpgradeDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleUpgrade}>
              {selectedPlan === 'enterprise' ? 'Contact Sales' : 'Upgrade Now'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

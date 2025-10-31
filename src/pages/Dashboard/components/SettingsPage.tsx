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
 <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
 </div>
 );
 }

 return (
 <div className="max-w-3xl space-y-6">
 <div className="bg-surface rounded-lg overflow-hidden ">
 <div className="p-6 bg-surface">
 <div className="flex items-center gap-3">
 <div className="w-10 h-10 rounded-lg bg-primary/20 flex items-center justify-center shadow-md shadow-primary/10">
 <Check className="h-5 w-5 icon-gradient" size={20} />
 </div>
 <h2 className="text-2xl font-bold text-foreground">Profile Settings</h2>
 </div>
 </div>
 <div className="p-6 space-y-6">
 <div>
 <label className="block text-sm font-semibold text-foreground mb-2.5">Full Name</label>
 <input
 type="text"
 value={name}
 onChange={(e) => setName(e.target.value)}
 className="w-full px-4 py-3 bg-card rounded-lg text-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:bg-primary/5 transition-all"
 />
 </div>
 <div>
 <label className="block text-sm font-semibold text-foreground mb-2.5">Email Address</label>
 <input
 type="email"
 value={email}
 onChange={(e) => setEmail(e.target.value)}
 className="w-full px-4 py-3 bg-card rounded-lg text-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:bg-primary/5 transition-all"
 />
 </div>
 <div className="flex items-center justify-between pt-6 bg-surface">
 <div>
 <div className="text-sm font-semibold text-foreground mb-2">Current Plan</div>
 <PlanBadge plan={user.subscription_tier} />
 </div>
 <div className="text-sm text-muted-foreground font-medium">
 Member since {new Date(user.created_at).toLocaleDateString()}
 </div>
 </div>
 </div>
 </div>
 <div className="bg-surface rounded-lg overflow-hidden ">
 <div className="p-6 bg-surface">
 <div className="flex items-center gap-3">
 <div className="w-10 h-10 rounded-lg bg-accent/20 flex items-center justify-center shadow-md shadow-accent/10">
 <Check className="h-5 w-5 icon-gradient-accent" size={20} />
 </div>
 <h2 className="text-2xl font-bold text-foreground">Notification Preferences</h2>
 </div>
 </div>
 <div className="p-6 space-y-5">
 <div className="flex items-center justify-between p-4 rounded-lg bg-card/70 hover:bg-primary/10 transition-all transition-colors">
 <div>
 <div className="text-sm font-bold text-foreground mb-1">Email Notifications</div>
 <div className="text-xs text-muted-foreground">Receive updates about your account</div>
 </div>
 <button
 onClick={() => setEmailNotifications(!emailNotifications)}
 className={`relative w-14 h-7 rounded-full transition-all shadow-lg border-2 ${
 emailNotifications 
 ? 'bg-primary shadow-primary/30 border-primary/50' 
 : 'bg-muted border-muted/40'
 }`}
 >
 <div className={`absolute top-0.5 left-0.5 w-6 h-6 rounded-full transition-transform shadow-md ${
 emailNotifications 
 ? 'translate-x-7 bg-primary-foreground' 
 : 'translate-x-0 bg-card'
 }`} />
 </button>
 </div>
 <div className="flex items-center justify-between p-4 rounded-lg bg-card/70 hover:bg-primary/10 transition-all transition-colors">
 <div>
 <div className="text-sm font-bold text-foreground mb-1">Processing Notifications</div>
 <div className="text-xs text-muted-foreground">Get notified when audiobooks are complete</div>
 </div>
 <button
 onClick={() => setProcessingNotifications(!processingNotifications)}
 className={`relative w-14 h-7 rounded-full transition-all shadow-lg border-2 ${
 processingNotifications 
 ? 'bg-accent shadow-accent/30 border-accent/50' 
 : 'bg-muted border-muted/40'
 }`}
 >
 <div className={`absolute top-0.5 left-0.5 w-6 h-6 rounded-full transition-transform shadow-md ${
 processingNotifications 
 ? 'translate-x-7 bg-accent-foreground' 
 : 'translate-x-0 bg-card'
 }`} />
 </button>
 </div>
 </div>
 </div>
 <div className="flex justify-end">
 <button
 onClick={handleSave}
 className="px-8 py-3 bg-primary hover:opacity-90 text-primary-foreground rounded-lg font-bold transition-all shadow-lg shadow-primary/20 hover:shadow-xl hover:shadow-primary/30 hover:-translate-y-0.5 flex items-center gap-2"
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

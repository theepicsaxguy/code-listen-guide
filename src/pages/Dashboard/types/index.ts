export interface AudiobookJob {
  id: string;
  repositoryName: string;
  repositoryUrl: string;
  status: 'processing' | 'completed' | 'failed';
  createdAt: string;
  completedAt?: string;
  duration: string;
  chapterCount: number;
  progress?: number;
  fileSize?: string;
  language?: string;
  frameworks?: string[];
  errorMessage?: string;
}

export interface Chapter {
  id: string;
  title: string;
  duration: string;
  timestamp: number;
  files: string[];
}

export interface AudiobookDetail extends AudiobookJob {
  chapters: Chapter[];
  description: string;
  totalFiles: number;
  linesOfCode: number;
}

export interface UserProfile {
  name: string;
  email: string;
  plan: 'free' | 'pro' | 'enterprise';
  createdAt: string;
  is_admin?: boolean;
}

export interface BillingInfo {
  plan: string;
  price: number;
  interval: 'month' | 'year';
  creditsUsed: number;
  creditsTotal: number;
  nextBillingDate: string;
  paymentMethod?: {
    type: 'card';
    last4: string;
    brand: string;
    expiryMonth: number;
    expiryYear: number;
  };
}

export interface Invoice {
  id: string;
  date: string;
  amount: number;
  status: string;
}

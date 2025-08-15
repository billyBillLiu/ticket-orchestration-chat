// API Configuration
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3080';
 
// Set the API base URL globally for the data-provider
if (typeof window !== 'undefined') {
  (window as any).__API_BASE_URL__ = API_BASE_URL;
} 
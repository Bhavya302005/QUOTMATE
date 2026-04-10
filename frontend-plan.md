# FRONTEND DEVELOPMENT PLAN
## Smart Business Document Generator
### 8-Week Implementation Guide

---

# DEVELOPER PROFILE

| Attribute | Details |
|-----------|---------|
| **Role** | Frontend Developer (Solo) |
| **Responsibilities** | React UI, Mobile-First Design, User Interactions |
| **Time Commitment** | 4-8 hours/week |
| **Key Focus** | Mobile responsiveness (primary device for users) |

---

# TECHNOLOGY STACK

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Framework** | React 18 | UI development |
| **Styling** | Tailwind CSS | Mobile-first responsive design |
| **State Management** | React Query + Context | Server state + Auth state |
| **Forms** | React Hook Form | Form handling & validation |
| **Routing** | React Router v6 | Navigation |
| **HTTP Client** | Axios | API calls |
| **Icons** | Lucide React | Icon library |
| **Notifications** | React Hot Toast | Toast messages |
| **Signature** | react-signature-canvas | Digital signatures |
| **Deployment** | Vercel | Hosting |

---

# DESIGN PRINCIPLES

## Mobile-First Approach
```
📱 Mobile (Primary)     → 💻 Tablet → 🖥️ Desktop
     375px+                  768px+      1024px+
```

## UI/UX Guidelines
1. **Touch-friendly** - Minimum 44px tap targets
2. **Thumb-zone optimized** - Important actions at bottom
3. **Minimal typing** - Use dropdowns, pickers where possible
4. **Fast feedback** - Loading states, instant validation
5. **Offline awareness** - Clear messaging when offline

---

# WEEK-BY-WEEK PLAN

---

## 📅 WEEK 1: Project Setup & Base Layout
**Hours Required:** 6-8 hours

### Tasks

| # | Task | Hours | Priority |
|---|------|-------|----------|
| 1 | Create React project with Vite | 0.5 | High |
| 2 | Setup Tailwind CSS | 0.5 | High |
| 3 | Install dependencies | 0.5 | High |
| 4 | Setup project folder structure | 1 | High |
| 5 | Create mobile-first base layout | 2 | High |
| 6 | Design Login & Register UI screens | 2 | High |
| 7 | Setup React Router | 0.5 | High |
| 8 | Create reusable Button & Input components | 1 | Medium |

### Project Setup Commands

```bash
# Create project with Vite
npm create vite@latest docgen-frontend -- --template react

# Navigate to project
cd docgen-frontend

# Install dependencies
npm install

# Install Tailwind CSS
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Install other dependencies
npm install react-router-dom axios @tanstack/react-query 
npm install react-hook-form react-hot-toast lucide-react
npm install react-signature-canvas
```

### Project Structure

```
src/
├── components/
│   ├── common/
│   │   ├── Button.jsx
│   │   ├── Input.jsx
│   │   ├── Card.jsx
│   │   ├── Modal.jsx
│   │   ├── LoadingSpinner.jsx
│   │   ├── ErrorMessage.jsx
│   │   └── EmptyState.jsx
│   │
│   ├── layout/
│   │   ├── AppLayout.jsx
│   │   ├── MobileNav.jsx
│   │   ├── Header.jsx
│   │   └── BottomTabBar.jsx
│   │
│   ├── auth/
│   │   ├── LoginForm.jsx
│   │   ├── RegisterForm.jsx
│   │   └── ProtectedRoute.jsx
│   │
│   ├── quotation/
│   │   ├── QuotationForm.jsx
│   │   ├── QuotationList.jsx
│   │   ├── QuotationPreview.jsx
│   │   ├── CustomerDetails.jsx
│   │   ├── LineItems.jsx
│   │   └── GSTSummary.jsx
│   │
│   ├── mom/
│   │   ├── MOMForm.jsx
│   │   ├── MOMList.jsx
│   │   ├── MOMPreview.jsx
│   │   ├── ActionItems.jsx
│   │   └── AISummary.jsx
│   │
│   ├── work-order/
│   │   ├── WorkOrderForm.jsx
│   │   ├── WorkOrderList.jsx
│   │   ├── WorkOrderPreview.jsx
│   │   ├── MaterialsList.jsx
│   │   ├── PhotoUpload.jsx
│   │   └── SignaturePad.jsx
│   │
│   └── ocr/
│       ├── ImageUpload.jsx
│       ├── CameraCapture.jsx
│       ├── OCRResult.jsx
│       └── ConfidenceIndicator.jsx
│
├── pages/
│   ├── LoginPage.jsx
│   ├── RegisterPage.jsx
│   ├── DashboardPage.jsx
│   ├── ProfilePage.jsx
│   ├── QuotationPage.jsx
│   ├── MOMPage.jsx
│   ├── WorkOrderPage.jsx
│   └── NotFoundPage.jsx
│
├── context/
│   └── AuthContext.jsx
│
├── hooks/
│   ├── useAuth.js
│   ├── useApi.js
│   └── useCamera.js
│
├── services/
│   └── api.js
│
├── utils/
│   ├── formatters.js
│   └── validators.js
│
├── styles/
│   └── index.css
│
├── App.jsx
└── main.jsx
```

### Tailwind Configuration

```javascript
// tailwind.config.js
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        },
        success: '#10b981',
        warning: '#f59e0b',
        error: '#ef4444',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
```

### Base Layout Component

```jsx
// src/components/layout/AppLayout.jsx
import { Outlet } from 'react-router-dom';
import Header from './Header';
import BottomTabBar from './BottomTabBar';

export default function AppLayout() {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header - Fixed at top */}
      <Header />
      
      {/* Main Content - Scrollable */}
      <main className="flex-1 overflow-y-auto pb-20 pt-16">
        <div className="max-w-lg mx-auto px-4 py-4">
          <Outlet />
        </div>
      </main>
      
      {/* Bottom Navigation - Fixed at bottom (Mobile) */}
      <BottomTabBar />
    </div>
  );
}
```

### Bottom Tab Bar (Mobile Navigation)

```jsx
// src/components/layout/BottomTabBar.jsx
import { NavLink } from 'react-router-dom';
import { Home, FileText, Users, ClipboardList, User } from 'lucide-react';

const tabs = [
  { to: '/dashboard', icon: Home, label: 'Home' },
  { to: '/quotations', icon: FileText, label: 'Quotes' },
  { to: '/moms', icon: Users, label: 'MOM' },
  { to: '/work-orders', icon: ClipboardList, label: 'Orders' },
  { to: '/profile', icon: User, label: 'Profile' },
];

export default function BottomTabBar() {
  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 md:hidden z-50">
      <div className="flex justify-around items-center h-16">
        {tabs.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex flex-col items-center justify-center w-full h-full text-xs
               ${isActive ? 'text-primary-600' : 'text-gray-500'}`
            }
          >
            <Icon className="w-6 h-6 mb-1" />
            <span>{label}</span>
          </NavLink>
        ))}
      </div>
    </nav>
  );
}
```

### Login Page UI

```jsx
// src/pages/LoginPage.jsx
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Mail, Lock, Eye, EyeOff } from 'lucide-react';
import Button from '../components/common/Button';
import Input from '../components/common/Input';

export default function LoginPage() {
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    // Login logic here
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-primary-600 to-primary-800 flex flex-col">
      {/* Logo Section */}
      <div className="flex-1 flex items-center justify-center pt-12 pb-8">
        <div className="text-center text-white">
          <div className="w-20 h-20 bg-white rounded-2xl mx-auto mb-4 flex items-center justify-center">
            <FileText className="w-10 h-10 text-primary-600" />
          </div>
          <h1 className="text-2xl font-bold">DocGen</h1>
          <p className="text-primary-100 text-sm mt-1">Smart Business Documents</p>
        </div>
      </div>

      {/* Login Form Card */}
      <div className="bg-white rounded-t-3xl px-6 py-8 min-h-[60vh]">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Welcome Back</h2>
        <p className="text-gray-500 mb-8">Sign in to continue</p>

        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Email Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="email"
                placeholder="Enter your email"
                className="w-full pl-11 pr-4 py-3 border border-gray-300 rounded-xl 
                         focus:ring-2 focus:ring-primary-500 focus:border-primary-500
                         text-base"
                required
              />
            </div>
          </div>

          {/* Password Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Password
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type={showPassword ? 'text' : 'password'}
                placeholder="Enter your password"
                className="w-full pl-11 pr-12 py-3 border border-gray-300 rounded-xl 
                         focus:ring-2 focus:ring-primary-500 focus:border-primary-500
                         text-base"
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400"
              >
                {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            </div>
          </div>

          {/* Forgot Password */}
          <div className="text-right">
            <a href="#" className="text-sm text-primary-600 font-medium">
              Forgot Password?
            </a>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-primary-600 text-white py-3.5 rounded-xl font-semibold
                     hover:bg-primary-700 transition-colors disabled:opacity-50
                     flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <>
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Signing in...
              </>
            ) : (
              'Sign In'
            )}
          </button>
        </form>

        {/* Register Link */}
        <p className="text-center mt-8 text-gray-600">
          Don't have an account?{' '}
          <Link to="/register" className="text-primary-600 font-semibold">
            Sign Up
          </Link>
        </p>
      </div>
    </div>
  );
}
```

### Deliverables
- [ ] React project running locally
- [ ] Tailwind CSS configured
- [ ] Mobile-first base layout created
- [ ] Login page UI complete
- [ ] Register page UI complete
- [ ] Bottom navigation working
- [ ] Routing setup complete

---

## 📅 WEEK 2: Authentication & State Management
**Hours Required:** 6-8 hours

### Tasks

| # | Task | Hours | Priority |
|---|------|-------|----------|
| 1 | Setup Axios instance with interceptors | 1 | High |
| 2 | Create AuthContext for state management | 1.5 | High |
| 3 | Implement login form with validation | 1.5 | High |
| 4 | Implement register form with validation | 1.5 | High |
| 5 | Create ProtectedRoute component | 0.5 | High |
| 6 | Build Profile page UI | 1 | Medium |
| 7 | Handle JWT storage & refresh | 1 | High |

### API Service Setup

```javascript
// src/services/api.js
import axios from 'axios';
import toast from 'react-hot-toast';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - Add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - Handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || 'Something went wrong';
    
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
      toast.error('Session expired. Please login again.');
    } else if (error.response?.status === 500) {
      toast.error('Server error. Please try again later.');
    }
    
    return Promise.reject(error);
  }
);

// Auth APIs
export const authAPI = {
  login: (data) => api.post('/auth/login', data),
  register: (data) => api.post('/auth/register', data),
  getProfile: () => api.get('/auth/profile'),
  updateProfile: (data) => api.put('/auth/profile', data),
};

// Quotation APIs
export const quotationAPI = {
  create: (data) => api.post('/quotations', data),
  list: (params) => api.get('/quotations', { params }),
  get: (id) => api.get(`/quotations/${id}`),
  update: (id, data) => api.put(`/quotations/${id}`, data),
  delete: (id) => api.delete(`/quotations/${id}`),
  fromOCR: (data) => api.post('/quotations/from-ocr', data),
  calculate: (data) => api.post('/quotations/calculate', data),
  finalize: (id) => api.post(`/quotations/${id}/finalize`),
  download: (id) => api.get(`/quotations/${id}/download`, { responseType: 'blob' }),
};

// OCR APIs
export const ocrAPI = {
  extract: (formData) => api.post('/ocr/extract', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
};

// MOM APIs
export const momAPI = {
  create: (data) => api.post('/moms', data),
  list: (params) => api.get('/moms', { params }),
  get: (id) => api.get(`/moms/${id}`),
  update: (id, data) => api.put(`/moms/${id}`, data),
  delete: (id) => api.delete(`/moms/${id}`),
  summarize: (data) => api.post('/moms/summarize', data),
  updateAction: (momId, actionId, data) => api.put(`/moms/${momId}/actions/${actionId}`, data),
  finalize: (id) => api.post(`/moms/${id}/finalize`),
};

// Work Order APIs
export const workOrderAPI = {
  create: (data) => api.post('/work-orders', data),
  list: (params) => api.get('/work-orders', { params }),
  get: (id) => api.get(`/work-orders/${id}`),
  update: (id, data) => api.put(`/work-orders/${id}`, data),
  delete: (id) => api.delete(`/work-orders/${id}`),
  uploadPhotos: (id, formData) => api.post(`/work-orders/${id}/photos`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  saveSignature: (id, data) => api.post(`/work-orders/${id}/signature`, data),
  finalize: (id) => api.post(`/work-orders/${id}/finalize`),
};

// Dashboard APIs
export const dashboardAPI = {
  getStats: () => api.get('/dashboard/stats'),
  search: (query) => api.get('/documents/search', { params: { q: query } }),
};

// Product APIs
export const productAPI = {
  create: (data) => api.post('/products', data),
  list: () => api.get('/products'),
  update: (id, data) => api.put(`/products/${id}`, data),
  delete: (id) => api.delete(`/products/${id}`),
};

export default api;
```

### Auth Context

```jsx
// src/context/AuthContext.jsx
import { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Check auth on mount
  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      setIsLoading(false);
      return;
    }

    try {
      const response = await authAPI.getProfile();
      setUser(response.data);
      setIsAuthenticated(true);
    } catch (error) {
      localStorage.removeItem('access_token');
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email, password) => {
    const response = await authAPI.login({ email, password });
    const { access_token, user } = response.data;
    
    localStorage.setItem('access_token', access_token);
    setUser(user);
    setIsAuthenticated(true);
    
    return response.data;
  };

  const register = async (userData) => {
    const response = await authAPI.register(userData);
    return response.data;
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    setUser(null);
    setIsAuthenticated(false);
  };

  const updateProfile = async (data) => {
    const response = await authAPI.updateProfile(data);
    setUser(response.data);
    return response.data;
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated,
        login,
        register,
        logout,
        updateProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
```

### Protected Route Component

```jsx
// src/components/auth/ProtectedRoute.jsx
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import LoadingSpinner from '../common/LoadingSpinner';

export default function ProtectedRoute({ children }) {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
}
```

### Deliverables
- [ ] Axios configured with interceptors
- [ ] AuthContext managing auth state
- [ ] Login form with validation working
- [ ] Register form with validation working
- [ ] Protected routes implemented
- [ ] Profile page showing user data
- [ ] JWT properly stored and sent

---

## 📅 WEEK 3: OCR & Image Upload Components
**Hours Required:** 6-8 hours

### Tasks

| # | Task | Hours | Priority |
|---|------|-------|----------|
| 1 | Build camera capture component | 2 | High |
| 2 | Build gallery image picker | 1 | High |
| 3 | Create image preview with crop option | 1.5 | Medium |
| 4 | Build upload progress indicator | 0.5 | High |
| 5 | Create OCR result display component | 1.5 | High |
| 6 | Build confidence score indicator | 0.5 | Medium |
| 7 | Handle OCR errors gracefully | 1 | High |

### Camera/Image Capture Component

```jsx
// src/components/ocr/ImageUpload.jsx
import { useState, useRef } from 'react';
import { Camera, Upload, X, RotateCcw } from 'lucide-react';
import toast from 'react-hot-toast';

export default function ImageUpload({ onImageSelect, onExtract, isLoading }) {
  const [preview, setPreview] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const fileInputRef = useRef(null);
  const cameraInputRef = useRef(null);

  const handleFileSelect = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file
    if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
      toast.error('Please select a JPEG, PNG, or WEBP image');
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      toast.error('Image must be less than 10MB');
      return;
    }

    setSelectedFile(file);
    
    // Create preview
    const reader = new FileReader();
    reader.onload = (e) => setPreview(e.target.result);
    reader.readAsDataURL(file);
  };

  const handleExtract = async () => {
    if (!selectedFile) return;
    
    const formData = new FormData();
    formData.append('file', selectedFile);
    
    try {
      await onExtract(formData);
    } catch (error) {
      toast.error('Failed to extract text. Please try again.');
    }
  };

  const clearImage = () => {
    setPreview(null);
    setSelectedFile(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
    if (cameraInputRef.current) cameraInputRef.current.value = '';
  };

  return (
    <div className="space-y-4">
      {!preview ? (
        // Upload Options
        <div className="grid grid-cols-2 gap-4">
          {/* Camera Option */}
          <button
            onClick={() => cameraInputRef.current?.click()}
            className="flex flex-col items-center justify-center p-6 border-2 border-dashed 
                     border-gray-300 rounded-xl hover:border-primary-500 hover:bg-primary-50
                     transition-colors"
          >
            <Camera className="w-10 h-10 text-gray-400 mb-2" />
            <span className="text-sm font-medium text-gray-600">Take Photo</span>
          </button>
          <input
            ref={cameraInputRef}
            type="file"
            accept="image/*"
            capture="environment"
            onChange={handleFileSelect}
            className="hidden"
          />

          {/* Gallery Option */}
          <button
            onClick={() => fileInputRef.current?.click()}
            className="flex flex-col items-center justify-center p-6 border-2 border-dashed 
                     border-gray-300 rounded-xl hover:border-primary-500 hover:bg-primary-50
                     transition-colors"
          >
            <Upload className="w-10 h-10 text-gray-400 mb-2" />
            <span className="text-sm font-medium text-gray-600">Upload Image</span>
          </button>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/jpeg,image/png,image/webp"
            onChange={handleFileSelect}
            className="hidden"
          />
        </div>
      ) : (
        // Image Preview
        <div className="relative">
          <img
            src={preview}
            alt="Selected"
            className="w-full h-64 object-contain bg-gray-100 rounded-xl"
          />
          
          {/* Clear Button */}
          <button
            onClick={clearImage}
            className="absolute top-2 right-2 p-2 bg-red-500 text-white rounded-full
                     shadow-lg hover:bg-red-600"
          >
            <X className="w-5 h-5" />
          </button>
          
          {/* Retake Button */}
          <button
            onClick={clearImage}
            className="absolute bottom-2 left-2 flex items-center gap-1 px-3 py-1.5 
                     bg-white text-gray-700 rounded-lg shadow text-sm font-medium"
          >
            <RotateCcw className="w-4 h-4" />
            Retake
          </button>
        </div>
      )}

      {/* Extract Button */}
      {preview && (
        <button
          onClick={handleExtract}
          disabled={isLoading}
          className="w-full bg-primary-600 text-white py-3.5 rounded-xl font-semibold
                   hover:bg-primary-700 transition-colors disabled:opacity-50
                   flex items-center justify-center gap-2"
        >
          {isLoading ? (
            <>
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Extracting Text...
            </>
          ) : (
            'Extract Text from Image'
          )}
        </button>
      )}

      {/* Help Text */}
      <p className="text-xs text-gray-500 text-center">
        For best results, ensure the image is well-lit and text is clearly visible
      </p>
    </div>
  );
}
```

### OCR Result Component

```jsx
// src/components/ocr/OCRResult.jsx
import { CheckCircle, AlertTriangle, Edit2 } from 'lucide-react';

export default function OCRResult({ 
  text, 
  confidence, 
  onEdit, 
  onAccept,
  mappedFields 
}) {
  const isHighConfidence = confidence >= 75;

  return (
    <div className="space-y-4">
      {/* Confidence Indicator */}
      <div className={`flex items-center gap-2 p-3 rounded-lg ${
        isHighConfidence ? 'bg-green-50 text-green-700' : 'bg-yellow-50 text-yellow-700'
      }`}>
        {isHighConfidence ? (
          <CheckCircle className="w-5 h-5" />
        ) : (
          <AlertTriangle className="w-5 h-5" />
        )}
        <span className="text-sm font-medium">
          {isHighConfidence 
            ? `High confidence (${confidence}%) - Text extracted successfully`
            : `Low confidence (${confidence}%) - Please review and edit`
          }
        </span>
      </div>

      {/* Extracted Text */}
      <div className="border border-gray-200 rounded-xl p-4 bg-gray-50">
        <div className="flex items-center justify-between mb-2">
          <h4 className="text-sm font-medium text-gray-700">Extracted Text</h4>
          <button
            onClick={onEdit}
            className="flex items-center gap-1 text-sm text-primary-600 font-medium"
          >
            <Edit2 className="w-4 h-4" />
            Edit
          </button>
        </div>
        <p className="text-sm text-gray-600 whitespace-pre-wrap max-h-40 overflow-y-auto">
          {text || 'No text extracted'}
        </p>
      </div>

      {/* Mapped Fields Preview */}
      {mappedFields && (
        <div className="border border-gray-200 rounded-xl p-4">
          <h4 className="text-sm font-medium text-gray-700 mb-3">
            Detected Fields
          </h4>
          <div className="space-y-2">
            {mappedFields.customer_name && (
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Customer:</span>
                <span className="font-medium">{mappedFields.customer_name}</span>
              </div>
            )}
            {mappedFields.customer_phone && (
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Phone:</span>
                <span className="font-medium">{mappedFields.customer_phone}</span>
              </div>
            )}
            {mappedFields.items?.length > 0 && (
              <div className="text-sm">
                <span className="text-gray-500">Items Found:</span>
                <span className="font-medium ml-2">{mappedFields.items.length}</span>
              </div>
            )}
          </div>
          
          {/* Fields needing review */}
          {mappedFields.confidence_flags?.length > 0 && (
            <div className="mt-3 pt-3 border-t border-gray-200">
              <p className="text-xs text-yellow-600">
                ⚠️ Please review: {mappedFields.confidence_flags.join(', ')}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex gap-3">
        <button
          onClick={onEdit}
          className="flex-1 py-3 border border-gray-300 rounded-xl font-medium
                   text-gray-700 hover:bg-gray-50"
        >
          Edit Manually
        </button>
        <button
          onClick={onAccept}
          className="flex-1 py-3 bg-primary-600 text-white rounded-xl font-medium
                   hover:bg-primary-700"
        >
          Continue
        </button>
      </div>
    </div>
  );
}
```

### Deliverables
- [ ] Camera capture working on mobile
- [ ] Gallery upload working
- [ ] Image preview showing
- [ ] Upload progress displayed
- [ ] OCR results displayed properly
- [ ] Confidence indicator working
- [ ] Error states handled

---

## 📅 WEEK 4: Quotation Module - Part 1
**Hours Required:** 6-8 hours

### Tasks

| # | Task | Hours | Priority |
|---|------|-------|----------|
| 1 | Create quotation form layout | 2 | High |
| 2 | Build customer details section | 1 | High |
| 3 | Build dynamic line items component | 2.5 | High |
| 4 | Implement auto-calculation display | 1 | High |
| 5 | Connect to backend APIs | 1.5 | High |

### Quotation Form Component

```jsx
// src/components/quotation/QuotationForm.jsx
import { useState, useEffect } from 'react';
import { useForm, useFieldArray } from 'react-hook-form';
import { Plus, Trash2, Calculator } from 'lucide-react';
import { quotationAPI, productAPI } from '../../services/api';
import toast from 'react-hot-toast';
import CustomerDetails from './CustomerDetails';
import GSTSummary from './GSTSummary';

export default function QuotationForm({ initialData, ocrData, onSuccess }) {
  const [isCalculating, setIsCalculating] = useState(false);
  const [totals, setTotals] = useState(null);
  const [products, setProducts] = useState([]);

  const { register, control, handleSubmit, watch, setValue, formState: { errors } } = useForm({
    defaultValues: initialData || {
      customer_name: ocrData?.customer_name || '',
      customer_phone: ocrData?.customer_phone || '',
      customer_email: '',
      customer_address: '',
      customer_gst: '',
      items: ocrData?.items || [{ description: '', quantity: 1, unit_price: 0, unit: 'nos', gst_rate: 18 }],
      discount_percent: 0,
      is_igst: false,
      valid_until: '',
      terms_conditions: '',
    }
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'items'
  });

  const watchItems = watch('items');
  const watchDiscount = watch('discount_percent');
  const watchIsIgst = watch('is_igst');

  // Load products for dropdown
  useEffect(() => {
    loadProducts();
  }, []);

  // Auto-calculate when items change
  useEffect(() => {
    if (watchItems?.length > 0) {
      calculateTotals();
    }
  }, [watchItems, watchDiscount, watchIsIgst]);

  const loadProducts = async () => {
    try {
      const response = await productAPI.list();
      setProducts(response.data);
    } catch (error) {
      console.error('Failed to load products');
    }
  };

  const calculateTotals = async () => {
    const validItems = watchItems.filter(item => 
      item.description && item.quantity > 0 && item.unit_price > 0
    );
    
    if (validItems.length === 0) {
      setTotals(null);
      return;
    }

    setIsCalculating(true);
    try {
      const response = await quotationAPI.calculate({
        items: validItems,
        discount_percent: parseFloat(watchDiscount) || 0,
        is_igst: watchIsIgst
      });
      setTotals(response.data);
    } catch (error) {
      console.error('Calculation error');
    } finally {
      setIsCalculating(false);
    }
  };

  const onSubmit = async (data) => {
    try {
      const response = await quotationAPI.create(data);
      toast.success('Quotation created successfully!');
      onSuccess?.(response.data);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create quotation');
    }
  };

  const addProductFromInventory = (product) => {
    append({
      description: product.name,
      quantity: 1,
      unit_price: product.default_price,
      unit: product.unit,
      gst_rate: product.gst_rate,
      product_id: product.id,
      is_free_text: false
    });
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {/* Customer Details Section */}
      <CustomerDetails register={register} errors={errors} />

      {/* Line Items Section */}
      <div className="bg-white rounded-xl border border-gray-200 p-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-gray-900">Items</h3>
          <button
            type="button"
            onClick={() => append({ description: '', quantity: 1, unit_price: 0, unit: 'nos', gst_rate: 18, is_free_text: true })}
            className="flex items-center gap-1 text-sm text-primary-600 font-medium"
          >
            <Plus className="w-4 h-4" />
            Add Item
          </button>
        </div>

        {/* Product Quick Add (if products exist) */}
        {products.length > 0 && (
          <div className="mb-4">
            <label className="block text-xs text-gray-500 mb-2">Quick Add from Inventory</label>
            <select
              onChange={(e) => {
                const product = products.find(p => p.id === e.target.value);
                if (product) addProductFromInventory(product);
                e.target.value = '';
              }}
              className="w-full p-2 border border-gray-300 rounded-lg text-sm"
            >
              <option value="">Select a product...</option>
              {products.map(p => (
                <option key={p.id} value={p.id}>{p.name} - ₹{p.default_price}</option>
              ))}
            </select>
          </div>
        )}

        {/* Items List */}
        <div className="space-y-4">
          {fields.map((field, index) => (
            <div key={field.id} className="p-3 bg-gray-50 rounded-lg">
              <div className="flex justify-between items-start mb-2">
                <span className="text-xs font-medium text-gray-500">Item {index + 1}</span>
                {fields.length > 1 && (
                  <button
                    type="button"
                    onClick={() => remove(index)}
                    className="text-red-500 p-1"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                )}
              </div>

              {/* Description */}
              <input
                {...register(`items.${index}.description`, { required: 'Required' })}
                placeholder="Item description"
                className="w-full p-2.5 border border-gray-300 rounded-lg mb-2 text-sm"
              />

              {/* Quantity, Unit, Price Row */}
              <div className="grid grid-cols-4 gap-2">
                <div>
                  <label className="text-xs text-gray-500">Qty</label>
                  <input
                    type="number"
                    step="0.01"
                    {...register(`items.${index}.quantity`, { required: true, min: 0.01 })}
                    className="w-full p-2 border border-gray-300 rounded-lg text-sm"
                  />
                </div>
                <div>
                  <label className="text-xs text-gray-500">Unit</label>
                  <select
                    {...register(`items.${index}.unit`)}
                    className="w-full p-2 border border-gray-300 rounded-lg text-sm"
                  >
                    <option value="nos">Nos</option>
                    <option value="kg">Kg</option>
                    <option value="ltr">Ltr</option>
                    <option value="pcs">Pcs</option>
                    <option value="box">Box</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs text-gray-500">Rate (₹)</label>
                  <input
                    type="number"
                    step="0.01"
                    {...register(`items.${index}.unit_price`, { required: true, min: 0 })}
                    className="w-full p-2 border border-gray-300 rounded-lg text-sm"
                  />
                </div>
                <div>
                  <label className="text-xs text-gray-500">GST %</label>
                  <select
                    {...register(`items.${index}.gst_rate`)}
                    className="w-full p-2 border border-gray-300 rounded-lg text-sm"
                  >
                    <option value="0">0%</option>
                    <option value="5">5%</option>
                    <option value="12">12%</option>
                    <option value="18">18%</option>
                    <option value="28">28%</option>
                  </select>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Discount & GST Type */}
      <div className="bg-white rounded-xl border border-gray-200 p-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Discount %
            </label>
            <input
              type="number"
              step="0.01"
              max="100"
              {...register('discount_percent')}
              className="w-full p-2.5 border border-gray-300 rounded-lg"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              GST Type
            </label>
            <select
              {...register('is_igst')}
              className="w-full p-2.5 border border-gray-300 rounded-lg"
            >
              <option value={false}>CGST + SGST (Intra-State)</option>
              <option value={true}>IGST (Inter-State)</option>
            </select>
          </div>
        </div>
      </div>

      {/* GST Summary */}
      {totals && <GSTSummary totals={totals} isCalculating={isCalculating} />}

      {/* Additional Details */}
      <div className="bg-white rounded-xl border border-gray-200 p-4 space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Valid Until
          </label>
          <input
            type="date"
            {...register('valid_until')}
            className="w-full p-2.5 border border-gray-300 rounded-lg"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Terms & Conditions
          </label>
          <textarea
            {...register('terms_conditions')}
            rows={3}
            placeholder="Payment terms, delivery conditions, etc."
            className="w-full p-2.5 border border-gray-300 rounded-lg text-sm"
          />
        </div>
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        className="w-full bg-primary-600 text-white py-3.5 rounded-xl font-semibold
                 hover:bg-primary-700 transition-colors"
      >
        Create Quotation
      </button>
    </form>
  );
}
```

### GST Summary Component

```jsx
// src/components/quotation/GSTSummary.jsx
import { Calculator } from 'lucide-react';

export default function GSTSummary({ totals, isCalculating }) {
  if (isCalculating) {
    return (
      <div className="bg-gray-50 rounded-xl p-4 flex items-center justify-center gap-2 text-gray-500">
        <Calculator className="w-5 h-5 animate-pulse" />
        <span>Calculating...</span>
      </div>
    );
  }

  if (!totals) return null;

  return (
    <div className="bg-gradient-to-br from-primary-50 to-blue-50 rounded-xl p-4 border border-primary-100">
      <h4 className="font-semibold text-gray-900 mb-3">Amount Summary</h4>
      
      <div className="space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-gray-600">Subtotal</span>
          <span className="font-medium">₹ {totals.subtotal.toFixed(2)}</span>
        </div>
        
        {totals.discount_amount > 0 && (
          <div className="flex justify-between text-green-600">
            <span>Discount ({totals.discount_percent}%)</span>
            <span>- ₹ {totals.discount_amount.toFixed(2)}</span>
          </div>
        )}
        
        {totals.cgst_amount > 0 && (
          <>
            <div className="flex justify-between">
              <span className="text-gray-600">CGST ({totals.cgst_rate?.toFixed(1)}%)</span>
              <span>₹ {totals.cgst_amount.toFixed(2)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">SGST ({totals.sgst_rate?.toFixed(1)}%)</span>
              <span>₹ {totals.sgst_amount.toFixed(2)}</span>
            </div>
          </>
        )}
        
        {totals.igst_amount > 0 && (
          <div className="flex justify-between">
            <span className="text-gray-600">IGST ({totals.igst_rate?.toFixed(1)}%)</span>
            <span>₹ {totals.igst_amount.toFixed(2)}</span>
          </div>
        )}
        
        <div className="border-t border-primary-200 pt-2 mt-2">
          <div className="flex justify-between text-lg font-bold text-primary-700">
            <span>Grand Total</span>
            <span>₹ {totals.grand_total.toFixed(2)}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
```

### Deliverables
- [ ] Quotation form layout complete
- [ ] Customer details section working
- [ ] Dynamic line items (add/remove)
- [ ] Auto-calculation showing totals
- [ ] GST summary displaying correctly
- [ ] Product quick-add from inventory

---

## 📅 WEEK 5: Quotation Module - Part 2
**Hours Required:** 6-8 hours

### Tasks

| # | Task | Hours | Priority |
|---|------|-------|----------|
| 1 | Build quotation preview screen | 2 | High |
| 2 | Implement PDF download functionality | 1 | High |
| 3 | Create quotation list view | 2 | High |
| 4 | Add search and filter | 1 | Medium |
| 5 | Connect OCR → Form flow | 1.5 | High |
| 6 | Polish and test complete flow | 0.5 | High |

### Quotation List Component

```jsx
// src/components/quotation/QuotationList.jsx
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { FileText, Download, Eye, Search, Plus, Filter } from 'lucide-react';
import { quotationAPI } from '../../services/api';
import LoadingSpinner from '../common/LoadingSpinner';
import EmptyState from '../common/EmptyState';

export default function QuotationList() {
  const [quotations, setQuotations] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('all'); // all, draft, finalized

  useEffect(() => {
    loadQuotations();
  }, [filter]);

  const loadQuotations = async () => {
    setIsLoading(true);
    try {
      const response = await quotationAPI.list({ 
        status: filter !== 'all' ? filter : undefined 
      });
      setQuotations(response.data);
    } catch (error) {
      console.error('Failed to load quotations');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownload = async (id, docNumber) => {
    try {
      const response = await quotationAPI.download(id);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.download = `Quotation-${docNumber}.pdf`;
      link.click();
    } catch (error) {
      console.error('Download failed');
    }
  };

  const filteredQuotations = quotations.filter(q =>
    q.customer_name?.toLowerCase().includes(search.toLowerCase()) ||
    q.document_number?.toLowerCase().includes(search.toLowerCase())
  );

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    });
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0
    }).format(amount);
  };

  if (isLoading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-gray-900">Quotations</h1>
        <Link
          to="/quotations/new"
          className="flex items-center gap-1 bg-primary-600 text-white px-4 py-2 
                   rounded-lg text-sm font-medium"
        >
          <Plus className="w-4 h-4" />
          New
        </Link>
      </div>

      {/* Search & Filter */}
      <div className="flex gap-2">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search quotations..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg text-sm"
          />
        </div>
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="px-3 py-2.5 border border-gray-300 rounded-lg text-sm"
        >
          <option value="all">All</option>
          <option value="draft">Draft</option>
          <option value="finalized">Finalized</option>
        </select>
      </div>

      {/* Quotation Cards */}
      {filteredQuotations.length === 0 ? (
        <EmptyState
          icon={FileText}
          title="No quotations yet"
          description="Create your first quotation to get started"
          actionLabel="Create Quotation"
          actionTo="/quotations/new"
        />
      ) : (
        <div className="space-y-3">
          {filteredQuotations.map((quotation) => (
            <div
              key={quotation.id}
              className="bg-white rounded-xl border border-gray-200 p-4"
            >
              <div className="flex items-start justify-between mb-2">
                <div>
                  <h3 className="font-semibold text-gray-900">
                    {quotation.customer_name}
                  </h3>
                  <p className="text-xs text-gray-500">
                    {quotation.document_number} • {formatDate(quotation.created_at)}
                  </p>
                </div>
                <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                  quotation.status === 'finalized' 
                    ? 'bg-green-100 text-green-700'
                    : 'bg-yellow-100 text-yellow-700'
                }`}>
                  {quotation.status}
                </span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-lg font-bold text-primary-600">
                  {formatCurrency(quotation.grand_total)}
                </span>
                
                <div className="flex items-center gap-2">
                  <Link
                    to={`/quotations/${quotation.id}`}
                    className="p-2 text-gray-500 hover:text-primary-600 hover:bg-gray-100 rounded-lg"
                  >
                    <Eye className="w-5 h-5" />
                  </Link>
                  {quotation.status === 'finalized' && (
                    <button
                      onClick={() => handleDownload(quotation.id, quotation.document_number)}
                      className="p-2 text-gray-500 hover:text-primary-600 hover:bg-gray-100 rounded-lg"
                    >
                      <Download className="w-5 h-5" />
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

### Quotation Page (Complete Flow)

```jsx
// src/pages/QuotationPage.jsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Camera, Edit } from 'lucide-react';
import ImageUpload from '../components/ocr/ImageUpload';
import OCRResult from '../components/ocr/OCRResult';
import QuotationForm from '../components/quotation/QuotationForm';
import { ocrAPI, quotationAPI } from '../services/api';
import toast from 'react-hot-toast';

const STEPS = {
  CHOOSE_INPUT: 'choose_input',
  OCR_UPLOAD: 'ocr_upload',
  OCR_RESULT: 'ocr_result',
  FORM: 'form'
};

export default function QuotationPage() {
  const navigate = useNavigate();
  const [step, setStep] = useState(STEPS.CHOOSE_INPUT);
  const [isLoading, setIsLoading] = useState(false);
  const [ocrResult, setOcrResult] = useState(null);
  const [mappedData, setMappedData] = useState(null);

  const handleOCRExtract = async (formData) => {
    setIsLoading(true);
    try {
      // First, extract text
      const ocrResponse = await ocrAPI.extract(formData);
      setOcrResult(ocrResponse.data);

      // Then, map to quotation fields
      const mapResponse = await quotationAPI.fromOCR({
        text: ocrResponse.data.extracted_text
      });
      setMappedData(mapResponse.data);

      setStep(STEPS.OCR_RESULT);
    } catch (error) {
      toast.error('Failed to process image. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuccess = (quotation) => {
    navigate(`/quotations/${quotation.id}`);
  };

  const renderStep = () => {
    switch (step) {
      case STEPS.CHOOSE_INPUT:
        return (
          <div className="space-y-6">
            <div className="text-center py-6">
              <h2 className="text-xl font-bold text-gray-900 mb-2">
                Create Quotation
              </h2>
              <p className="text-gray-500">
                How would you like to create your quotation?
              </p>
            </div>

            <div className="space-y-3">
              <button
                onClick={() => setStep(STEPS.OCR_UPLOAD)}
                className="w-full flex items-center gap-4 p-4 bg-white border-2 border-gray-200 
                         rounded-xl hover:border-primary-500 hover:bg-primary-50 transition-colors"
              >
                <div className="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center">
                  <Camera className="w-6 h-6 text-primary-600" />
                </div>
                <div className="text-left">
                  <h3 className="font-semibold text-gray-900">Scan Handwritten Notes</h3>
                  <p className="text-sm text-gray-500">Take a photo or upload an image</p>
                </div>
              </button>

              <button
                onClick={() => setStep(STEPS.FORM)}
                className="w-full flex items-center gap-4 p-4 bg-white border-2 border-gray-200 
                         rounded-xl hover:border-primary-500 hover:bg-primary-50 transition-colors"
              >
                <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
                  <Edit className="w-6 h-6 text-green-600" />
                </div>
                <div className="text-left">
                  <h3 className="font-semibold text-gray-900">Manual Entry</h3>
                  <p className="text-sm text-gray-500">Fill in the details manually</p>
                </div>
              </button>
            </div>
          </div>
        );

      case STEPS.OCR_UPLOAD:
        return (
          <div className="space-y-4">
            <button
              onClick={() => setStep(STEPS.CHOOSE_INPUT)}
              className="flex items-center gap-2 text-gray-600"
            >
              <ArrowLeft className="w-5 h-5" />
              Back
            </button>

            <h2 className="text-xl font-bold text-gray-900">
              Upload Handwritten Notes
            </h2>

            <ImageUpload
              onExtract={handleOCRExtract}
              isLoading={isLoading}
            />
          </div>
        );

      case STEPS.OCR_RESULT:
        return (
          <div className="space-y-4">
            <button
              onClick={() => setStep(STEPS.OCR_UPLOAD)}
              className="flex items-center gap-2 text-gray-600"
            >
              <ArrowLeft className="w-5 h-5" />
              Back
            </button>

            <h2 className="text-xl font-bold text-gray-900">
              Review Extracted Text
            </h2>

            <OCRResult
              text={ocrResult?.extracted_text}
              confidence={ocrResult?.confidence}
              mappedFields={mappedData}
              onEdit={() => setStep(STEPS.FORM)}
              onAccept={() => setStep(STEPS.FORM)}
            />
          </div>
        );

      case STEPS.FORM:
        return (
          <div className="space-y-4">
            <button
              onClick={() => setStep(STEPS.CHOOSE_INPUT)}
              className="flex items-center gap-2 text-gray-600"
            >
              <ArrowLeft className="w-5 h-5" />
              Back
            </button>

            <h2 className="text-xl font-bold text-gray-900">
              Quotation Details
            </h2>

            <QuotationForm
              ocrData={mappedData}
              onSuccess={handleSuccess}
            />
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="pb-8">
      {renderStep()}
    </div>
  );
}
```

### Deliverables
- [ ] Quotation preview screen complete
- [ ] PDF download working
- [ ] Quotation list with cards
- [ ] Search and filter functional
- [ ] Complete OCR → Form flow working
- [ ] End-to-end quotation creation tested

---

## 📅 WEEK 6: MOM Module with AI Integration
**Hours Required:** 6-8 hours

### Tasks

| # | Task | Hours | Priority |
|---|------|-------|----------|
| 1 | Create MOM form UI | 2 | High |
| 2 | Build meeting notes input (large textarea) | 1 | High |
| 3 | Create AI summarize button with loading state | 1 | High |
| 4 | Build editable summary display | 1.5 | High |
| 5 | Create action items management UI | 2 | High |
| 6 | Connect to AI backend | 0.5 | High |

### MOM Form with AI

```jsx
// src/components/mom/MOMForm.jsx
import { useState } from 'react';
import { useForm, useFieldArray } from 'react-hook-form';
import { Sparkles, Plus, Trash2, User, Calendar, AlertCircle } from 'lucide-react';
import { momAPI } from '../../services/api';
import toast from 'react-hot-toast';

export default function MOMForm({ ocrText, onSuccess }) {
  const [isAiLoading, setIsAiLoading] = useState(false);
  const [aiProcessingTime, setAiProcessingTime] = useState(null);

  const { register, control, handleSubmit, setValue, watch, formState: { errors } } = useForm({
    defaultValues: {
      meeting_title: '',
      meeting_date: new Date().toISOString().split('T')[0],
      meeting_time: '',
      location: '',
      attendees: [''],
      raw_notes: ocrText || '',
      ai_summary: '',
      discussion_points: [''],
      decisions: [''],
      action_items: [],
      next_meeting_date: ''
    }
  });

  const { fields: attendeeFields, append: appendAttendee, remove: removeAttendee } = useFieldArray({
    control,
    name: 'attendees'
  });

  const { fields: discussionFields, append: appendDiscussion, remove: removeDiscussion } = useFieldArray({
    control,
    name: 'discussion_points'
  });

  const { fields: decisionFields, append: appendDecision, remove: removeDecision } = useFieldArray({
    control,
    name: 'decisions'
  });

  const { fields: actionFields, append: appendAction, remove: removeAction } = useFieldArray({
    control,
    name: 'action_items'
  });

  const rawNotes = watch('raw_notes');

  const handleAISummarize = async () => {
    if (!rawNotes || rawNotes.trim().length < 50) {
      toast.error('Please enter at least 50 characters of meeting notes');
      return;
    }

    setIsAiLoading(true);
    try {
      const response = await momAPI.summarize({ raw_notes: rawNotes });
      const { data, processing_time } = response.data;

      // Populate form with AI results
      if (data.meeting_title) setValue('meeting_title', data.meeting_title);
      if (data.summary) setValue('ai_summary', data.summary);
      
      // Discussion points
      if (data.key_discussion_points?.length > 0) {
        setValue('discussion_points', data.key_discussion_points);
      }
      
      // Decisions
      if (data.decisions_made?.length > 0) {
        setValue('decisions', data.decisions_made);
      }
      
      // Action items
      if (data.action_items?.length > 0) {
        setValue('action_items', data.action_items.map(item => ({
          task_description: item.task,
          assigned_to: item.assigned_to || '',
          deadline: item.deadline !== 'TBD' ? item.deadline : '',
          priority: item.priority || 'medium',
          status: 'pending'
        })));
      }

      // Attendees
      if (data.attendees_mentioned?.length > 0) {
        setValue('attendees', data.attendees_mentioned);
      }

      setAiProcessingTime(processing_time);
      toast.success('AI summarization complete!');

    } catch (error) {
      toast.error('AI summarization failed. Please try again.');
    } finally {
      setIsAiLoading(false);
    }
  };

  const onSubmit = async (data) => {
    try {
      // Clean up empty arrays
      data.attendees = data.attendees.filter(a => a.trim());
      data.discussion_points = data.discussion_points.filter(d => d.trim());
      data.decisions = data.decisions.filter(d => d.trim());

      const response = await momAPI.create(data);
      toast.success('MOM created successfully!');
      onSuccess?.(response.data);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create MOM');
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {/* Meeting Basic Info */}
      <div className="bg-white rounded-xl border border-gray-200 p-4 space-y-4">
        <h3 className="font-semibold text-gray-900">Meeting Details</h3>
        
        <input
          {...register('meeting_title')}
          placeholder="Meeting Title"
          className="w-full p-3 border border-gray-300 rounded-lg"
        />

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-xs text-gray-500">Date</label>
            <input
              type="date"
              {...register('meeting_date')}
              className="w-full p-2.5 border border-gray-300 rounded-lg"
            />
          </div>
          <div>
            <label className="text-xs text-gray-500">Time</label>
            <input
              type="time"
              {...register('meeting_time')}
              className="w-full p-2.5 border border-gray-300 rounded-lg"
            />
          </div>
        </div>

        <input
          {...register('location')}
          placeholder="Location (optional)"
          className="w-full p-3 border border-gray-300 rounded-lg"
        />
      </div>

      {/* Attendees */}
      <div className="bg-white rounded-xl border border-gray-200 p-4">
        <div className="flex justify-between items-center mb-3">
          <h3 className="font-semibold text-gray-900">Attendees</h3>
          <button
            type="button"
            onClick={() => appendAttendee('')}
            className="text-sm text-primary-600 font-medium"
          >
            <Plus className="w-4 h-4 inline" /> Add
          </button>
        </div>
        <div className="space-y-2">
          {attendeeFields.map((field, index) => (
            <div key={field.id} className="flex gap-2">
              <input
                {...register(`attendees.${index}`)}
                placeholder="Attendee name"
                className="flex-1 p-2.5 border border-gray-300 rounded-lg text-sm"
              />
              {attendeeFields.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeAttendee(index)}
                  className="p-2 text-red-500"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Raw Meeting Notes + AI Button */}
      <div className="bg-white rounded-xl border border-gray-200 p-4">
        <div className="flex justify-between items-center mb-3">
          <h3 className="font-semibold text-gray-900">Meeting Notes</h3>
          <span className="text-xs text-gray-500">
            {rawNotes?.length || 0} characters
          </span>
        </div>

        <textarea
          {...register('raw_notes', { required: 'Meeting notes are required' })}
          rows={8}
          placeholder="Paste or type your meeting notes here...

Example:
- Discussed Q4 targets with the team
- John will prepare the sales report by Friday
- Decided to postpone the product launch to March
- Next meeting scheduled for Monday 10 AM"
          className="w-full p-3 border border-gray-300 rounded-lg text-sm resize-none"
        />
        {errors.raw_notes && (
          <p className="text-red-500 text-xs mt-1">{errors.raw_notes.message}</p>
        )}

        {/* AI Summarize Button */}
        <button
          type="button"
          onClick={handleAISummarize}
          disabled={isAiLoading || !rawNotes || rawNotes.length < 50}
          className="mt-3 w-full flex items-center justify-center gap-2 py-3 
                   bg-gradient-to-r from-purple-600 to-indigo-600 text-white 
                   rounded-xl font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isAiLoading ? (
            <>
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              AI is analyzing... (5-7 sec)
            </>
          ) : (
            <>
              <Sparkles className="w-5 h-5" />
              Summarize with AI
            </>
          )}
        </button>

        {aiProcessingTime && (
          <p className="text-xs text-center text-gray-500 mt-2">
            Processed in {aiProcessingTime}s using NVIDIA Llama
          </p>
        )}
      </div>

      {/* AI Generated Summary */}
      <div className="bg-white rounded-xl border border-gray-200 p-4">
        <h3 className="font-semibold text-gray-900 mb-3">Summary</h3>
        <textarea
          {...register('ai_summary')}
          rows={3}
          placeholder="AI-generated summary will appear here, or write your own..."
          className="w-full p-3 border border-gray-300 rounded-lg text-sm resize-none"
        />
      </div>

      {/* Discussion Points */}
      <div className="bg-white rounded-xl border border-gray-200 p-4">
        <div className="flex justify-between items-center mb-3">
          <h3 className="font-semibold text-gray-900">Discussion Points</h3>
          <button
            type="button"
            onClick={() => appendDiscussion('')}
            className="text-sm text-primary-600 font-medium"
          >
            <Plus className="w-4 h-4 inline" /> Add
          </button>
        </div>
        <div className="space-y-2">
          {discussionFields.map((field, index) => (
            <div key={field.id} className="flex gap-2">
              <input
                {...register(`discussion_points.${index}`)}
                placeholder={`Discussion point ${index + 1}`}
                className="flex-1 p-2.5 border border-gray-300 rounded-lg text-sm"
              />
              <button
                type="button"
                onClick={() => removeDiscussion(index)}
                className="p-2 text-red-500"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Action Items */}
      <div className="bg-white rounded-xl border border-gray-200 p-4">
        <div className="flex justify-between items-center mb-3">
          <h3 className="font-semibold text-gray-900">Action Items</h3>
          <button
            type="button"
            onClick={() => appendAction({
              task_description: '',
              assigned_to: '',
              deadline: '',
              priority: 'medium',
              status: 'pending'
            })}
            className="text-sm text-primary-600 font-medium"
          >
            <Plus className="w-4 h-4 inline" /> Add
          </button>
        </div>

        <div className="space-y-3">
          {actionFields.map((field, index) => (
            <div key={field.id} className="p-3 bg-gray-50 rounded-lg">
              <div className="flex justify-between mb-2">
                <span className="text-xs font-medium text-gray-500">Action {index + 1}</span>
                <button
                  type="button"
                  onClick={() => removeAction(index)}
                  className="text-red-500"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>

              <input
                {...register(`action_items.${index}.task_description`)}
                placeholder="Task description"
                className="w-full p-2.5 border border-gray-300 rounded-lg text-sm mb-2"
              />

              <div className="grid grid-cols-3 gap-2">
                <input
                  {...register(`action_items.${index}.assigned_to`)}
                  placeholder="Assigned to"
                  className="p-2 border border-gray-300 rounded-lg text-sm"
                />
                <input
                  type="date"
                  {...register(`action_items.${index}.deadline`)}
                  className="p-2 border border-gray-300 rounded-lg text-sm"
                />
                <select
                  {...register(`action_items.${index}.priority`)}
                  className="p-2 border border-gray-300 rounded-lg text-sm"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
              </div>
            </div>
          ))}

          {actionFields.length === 0 && (
            <p className="text-sm text-gray-500 text-center py-4">
              No action items yet. Click "Add" or use AI to extract them.
            </p>
          )}
        </div>
      </div>

      {/* Submit */}
      <button
        type="submit"
        className="w-full bg-primary-600 text-white py-3.5 rounded-xl font-semibold
                 hover:bg-primary-700 transition-colors"
      >
        Create Minutes of Meeting
      </button>
    </form>
  );
}
```

### Deliverables
- [ ] MOM form UI complete
- [ ] Large textarea for meeting notes
- [ ] AI summarize button with loading state
- [ ] Editable AI-generated content
- [ ] Action items with status/priority
- [ ] AI integration working (5-7 sec response)

---

## 📅 WEEK 7: Work Order Module
**Hours Required:** 6-8 hours

### Tasks

| # | Task | Hours | Priority |
|---|------|-------|----------|
| 1 | Create work order form UI | 2 | High |
| 2 | Build materials list management | 1.5 | High |
| 3 | Implement before/after photo upload | 1.5 | High |
| 4 | Create digital signature pad | 1.5 | High |
| 5 | Build work order preview | 1 | Medium |
| 6 | Connect all APIs | 0.5 | High |

### Digital Signature Component

```jsx
// src/components/work-order/SignaturePad.jsx
import { useRef, useState } from 'react';
import SignatureCanvas from 'react-signature-canvas';
import { Trash2, Check } from 'lucide-react';

export default function SignaturePad({ onSave, savedSignature }) {
  const sigRef = useRef(null);
  const [isEmpty, setIsEmpty] = useState(true);

  const handleClear = () => {
    sigRef.current?.clear();
    setIsEmpty(true);
  };

  const handleSave = () => {
    if (sigRef.current?.isEmpty()) {
      return;
    }
    const dataUrl = sigRef.current.toDataURL('image/png');
    onSave(dataUrl);
  };

  if (savedSignature) {
    return (
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700">
          Customer Signature
        </label>
        <div className="border border-gray-300 rounded-lg p-2 bg-gray-50">
          <img
            src={savedSignature}
            alt="Customer signature"
            className="max-h-24 mx-auto"
          />
        </div>
        <button
          type="button"
          onClick={() => onSave(null)}
          className="text-sm text-red-600 font-medium"
        >
          Clear and re-sign
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">
        Customer Signature
      </label>
      <div className="border-2 border-dashed border-gray-300 rounded-lg bg-white">
        <SignatureCanvas
          ref={sigRef}
          canvasProps={{
            className: 'w-full h-32',
          }}
          onBegin={() => setIsEmpty(false)}
        />
      </div>
      <div className="flex gap-2">
        <button
          type="button"
          onClick={handleClear}
          className="flex-1 flex items-center justify-center gap-1 py-2 border border-gray-300 
                   rounded-lg text-sm text-gray-600"
        >
          <Trash2 className="w-4 h-4" />
          Clear
        </button>
        <button
          type="button"
          onClick={handleSave}
          disabled={isEmpty}
          className="flex-1 flex items-center justify-center gap-1 py-2 bg-primary-600 
                   text-white rounded-lg text-sm font-medium disabled:opacity-50"
        >
          <Check className="w-4 h-4" />
          Save Signature
        </button>
      </div>
    </div>
  );
}
```

### Deliverables
- [ ] Work order form UI complete
- [ ] Materials list (add/remove)
- [ ] Before/after photo upload
- [ ] Digital signature capture
- [ ] Labor cost calculation displayed
- [ ] Work order preview screen

---

## 📅 WEEK 8: Dashboard, Polish & Deployment
**Hours Required:** 8 hours

### Tasks

| # | Task | Hours | Priority |
|---|------|-------|----------|
| 1 | Build dashboard with stats | 2 | High |
| 2 | Create document search UI | 1 | Medium |
| 3 | Final UI polish and consistency | 2 | High |
| 4 | Mobile responsiveness testing | 1 | High |
| 5 | Deploy to Vercel | 1 | High |
| 6 | Bug fixes and testing | 1 | High |

### Dashboard Component

```jsx
// src/pages/DashboardPage.jsx
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { FileText, Users, ClipboardList, Plus, TrendingUp, Clock } from 'lucide-react';
import { dashboardAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import LoadingSpinner from '../components/common/LoadingSpinner';

export default function DashboardPage() {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const response = await dashboardAPI.getStats();
      setStats(response.data);
    } catch (error) {
      console.error('Failed to load stats');
    } finally {
      setIsLoading(false);
    }
  };

  const quickActions = [
    { to: '/quotations/new', icon: FileText, label: 'New Quotation', color: 'bg-blue-500' },
    { to: '/moms/new', icon: Users, label: 'New MOM', color: 'bg-purple-500' },
    { to: '/work-orders/new', icon: ClipboardList, label: 'New Work Order', color: 'bg-orange-500' },
  ];

  if (isLoading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-primary-600 to-primary-700 rounded-2xl p-6 text-white">
        <h1 className="text-xl font-bold mb-1">
          Hello, {user?.full_name?.split(' ')[0] || 'there'}! 👋
        </h1>
        <p className="text-primary-100 text-sm">
          {user?.company_name || 'Welcome to DocGen'}
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 gap-3">
        <div className="bg-white rounded-xl p-4 border border-gray-200">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <FileText className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats?.quotations || 0}</p>
              <p className="text-xs text-gray-500">Quotations</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-4 border border-gray-200">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <Users className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats?.moms || 0}</p>
              <p className="text-xs text-gray-500">MOMs</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-4 border border-gray-200">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
              <ClipboardList className="w-5 h-5 text-orange-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats?.work_orders || 0}</p>
              <p className="text-xs text-gray-500">Work Orders</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-4 border border-gray-200">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
              <Clock className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{stats?.pending_action_items || 0}</p>
              <p className="text-xs text-gray-500">Pending Actions</p>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-3">Quick Actions</h2>
        <div className="grid grid-cols-3 gap-3">
          {quickActions.map(({ to, icon: Icon, label, color }) => (
            <Link
              key={to}
              to={to}
              className="flex flex-col items-center p-4 bg-white rounded-xl border border-gray-200
                       hover:shadow-md transition-shadow"
            >
              <div className={`w-12 h-12 ${color} rounded-xl flex items-center justify-center mb-2`}>
                <Icon className="w-6 h-6 text-white" />
              </div>
              <span className="text-xs font-medium text-gray-700 text-center">{label}</span>
            </Link>
          ))}
        </div>
      </div>

      {/* Recent Documents */}
      {stats?.recent_documents?.length > 0 && (
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-3">Recent Documents</h2>
          <div className="space-y-2">
            {stats.recent_documents.map((doc) => (
              <Link
                key={doc.id}
                to={`/${doc.type}s/${doc.id}`}
                className="flex items-center justify-between p-3 bg-white rounded-xl border 
                         border-gray-200 hover:border-primary-300"
              >
                <div className="flex items-center gap-3">
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                    doc.type === 'quotation' ? 'bg-blue-100' :
                    doc.type === 'mom' ? 'bg-purple-100' : 'bg-orange-100'
                  }`}>
                    {doc.type === 'quotation' ? <FileText className="w-4 h-4 text-blue-600" /> :
                     doc.type === 'mom' ? <Users className="w-4 h-4 text-purple-600" /> :
                     <ClipboardList className="w-4 h-4 text-orange-600" />}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">{doc.title || doc.type}</p>
                    <p className="text-xs text-gray-500">
                      {new Date(doc.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                <span className={`text-xs px-2 py-1 rounded-full ${
                  doc.status === 'finalized' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
                }`}>
                  {doc.status}
                </span>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
```

### Vercel Deployment

```bash
# 1. Install Vercel CLI
npm install -g vercel

# 2. Login
vercel login

# 3. Create .env.production
echo "VITE_API_URL=https://your-backend.railway.app/api" > .env.production

# 4. Deploy
vercel

# 5. Set environment variables in Vercel dashboard
# VITE_API_URL = https://your-backend-url.railway.app/api

# 6. Deploy to production
vercel --prod
```

### Deliverables
- [ ] Dashboard showing stats
- [ ] Quick actions working
- [ ] Recent documents displayed
- [ ] All pages mobile responsive
- [ ] Deployed to Vercel
- [ ] All features tested on mobile

---

# WEEKLY CHECKLIST SUMMARY

| Week | Focus | Key Deliverables | Hours |
|------|-------|------------------|-------|
| 1 | Setup | React, Tailwind, Layout, Auth UI | 6-8 |
| 2 | Auth | Login, Register, Context, Protected Routes | 6-8 |
| 3 | OCR UI | Camera, Upload, OCR Result Display | 6-8 |
| 4 | Quotation P1 | Form, Line Items, GST Display | 6-8 |
| 5 | Quotation P2 | Preview, List, PDF Download, Full Flow | 6-8 |
| 6 | MOM | Form, AI Button, Action Items | 6-8 |
| 7 | Work Order | Form, Photos, Signature | 6-8 |
| 8 | Deploy | Dashboard, Polish, Vercel | 8 |

**Total Frontend Hours: 54-66 hours**

---

# MOBILE-FIRST CHECKLIST

Before deployment, verify on mobile:
- [ ] All tap targets are at least 44px
- [ ] Forms are easy to fill on mobile keyboard
- [ ] Images load quickly (compressed)
- [ ] Bottom navigation is accessible
- [ ] Camera/upload works on iOS and Android
- [ ] Signature pad works on touch screens
- [ ] PDF download works on mobile browsers
- [ ] No horizontal scrolling on any page

---

# RESOURCES

- **React Docs:** https://react.dev
- **Tailwind CSS:** https://tailwindcss.com
- **React Hook Form:** https://react-hook-form.com
- **Lucide Icons:** https://lucide.dev
- **Vercel:** https://vercel.com/docs

---

**Document Version:** 1.0  
**Last Updated:** January 2025  
**Developer:** Frontend Lead
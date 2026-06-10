import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/auth/ProtectedRoute';
import AppLayout from './components/layout/AppLayout.jsx';
import ErrorBoundary from './components/common/ErrorBoundary.jsx';
import LoadingSpinner from './components/common/LoadingSpinner.jsx';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // Data is considered fresh for 5 minutes
      refetchOnWindowFocus: false, // Don't refetch on window focus to avoid unnecessary requests
    },
  },
});

// Lazy-loaded page components (route-level code splitting)
const LoginPage = lazy(() => import('./pages/LoginPage.jsx'));
const RegisterPage = lazy(() => import('./pages/RegisterPage.jsx'));
const DashboardPage = lazy(() => import('./pages/DashboardPage.jsx'));
const QuotationPage = lazy(() => import('./pages/QuotationPage.jsx'));
const MOMPage = lazy(() => import('./pages/MOMPage.jsx'));
const WorkOrderPage = lazy(() => import('./pages/WorkOrderPage.jsx'));
const ProfilePage = lazy(() => import('./pages/ProfilePage.jsx'));
const NotFoundPage = lazy(() => import('./pages/NotFoundPage.jsx'));

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <Toaster
            position="top-center"
            toastOptions={{
              duration: 4000,
              className:
                '!bg-black !text-white !! ! ! !border !border-white !shadow-none',
            }}
          />
          <ErrorBoundary>
            <Suspense
              fallback={
                <div className="flex min-h-screen items-center justify-center bg-surface">
                  <LoadingSpinner />
                </div>
              }
            >
              <Routes>
                {/* Public routes */}
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />

                {/* Protected Routes */}
                <Route element={
                  <ProtectedRoute>
                    <AppLayout />
                  </ProtectedRoute>
                }>
                  <Route path="/" element={<Navigate to="/dashboard" replace />} />
                  <Route path="/dashboard" element={<DashboardPage />} />
                  <Route path="/quotations/*" element={<QuotationPage />} />
                  <Route path="/moms/*" element={<MOMPage />} />
                  <Route path="/work-orders/*" element={<WorkOrderPage />} />
                  <Route path="/profile" element={<ProfilePage />} />
                </Route>

                {/* 404 */}
                <Route path="*" element={<NotFoundPage />} />
              </Routes>
            </Suspense>
          </ErrorBoundary>
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;

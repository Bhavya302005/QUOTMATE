import { Link, Navigate } from 'react-router-dom';
import { FileText } from 'lucide-react';
import RegisterForm from '../components/auth/RegisterForm';
import { useAuth } from '../context/AuthContext';

export default function RegisterPage() {
  const { isAuthenticated, isLoading } = useAuth();

  if (!isLoading && isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <div className="relative flex min-h-[100dvh] flex-col items-center justify-center bg-surface selection:bg-black selection:text-white">
      <div className="z-10 flex min-h-[100dvh] w-full max-w-md flex-col justify-center px-6 py-12">
        <div className="mb-10 text-center">
          <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center border-2 border-black bg-black text-white">
            <FileText className="h-8 w-8" strokeWidth={1.75} />
          </div>
          <h1 className="text-3xl font-light  tracking-tighter text-on-surface">QuotMate</h1>
          <p className="mt-3 inline-block border-y border-black py-1   ">
            Registration
          </p>
        </div>

        <div className="border border-black bg-surface-white px-8 py-10">
          <RegisterForm />
          <div className="mt-8 border-t border-black pt-6">
            <p className="text-center    text-on-surface">
              Already registered?{' '}
              <Link to="/login" className="border-b border-black hover:bg-black hover:text-white">
                Sign in
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

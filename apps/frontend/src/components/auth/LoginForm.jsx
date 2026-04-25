import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useLocation, useNavigate } from 'react-router-dom';
import { Mail, Lock, Eye, EyeOff } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { getApiErrorMessage } from '../../services/api';
import Button from '../common/Button';
import Input from '../common/Input';
import toast from 'react-hot-toast';

export default function LoginForm() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm();

  const onSubmit = async (data) => {
    setIsLoading(true);
    try {
      await login(data.email, data.password);
      const redirectTo = location.state?.from?.pathname || '/dashboard';
      navigate(redirectTo, { replace: true });
    } catch (error) {
      const statusCode = error?.response?.status;
      const detail = error?.response?.data?.detail;

      if (statusCode === 401 && typeof detail === 'string' && detail.toLowerCase().includes('incorrect email or password')) {
        toast.error(detail);
      } else if (statusCode === 401) {
        toast.error('Session expired. Please login again.');
      } else if (!error?.response) {
        toast.error('Network error. Please check your connection and try again.');
      } else {
        toast.error(getApiErrorMessage(error, 'Login failed'));
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
      <Input
        label="Email"
        type="email"
        placeholder="Enter your email"
        icon={Mail}
        error={errors.email?.message}
        registration={register('email', {
          required: 'Email is required',
          pattern: {
            value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
            message: 'Invalid email address',
          },
        })}
      />

      <div className="relative">
        <Input
          label="Password"
          type={showPassword ? 'text' : 'password'}
          placeholder="Enter your password"
          icon={Lock}
          inputClassName="pr-12"
          error={errors.password?.message}
          registration={register('password', {
            required: 'Password is required',
            minLength: {
              value: 6,
              message: 'Password must be at least 6 characters',
            },
          })}
        />
        <button
          type="button"
          onClick={() => setShowPassword(!showPassword)}
          className="absolute right-3 top-[34px] text-outline-muted hover:text-on-surface"
        >
          {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
        </button>
      </div>

      <div className="text-right">
        <a
          href="#"
          className="   text-on-surface underline decoration-black underline-offset-4 hover:bg-black hover:text-white hover:no-underline"
        >
          Forgot password?
        </a>
      </div>

      <Button
        type="submit"
        variant="primary"
        fullWidth
        isLoading={isLoading}
      >
        Sign In
      </Button>
    </form>
  );
}

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { Mail, Lock, User, Building, Eye, EyeOff, Phone, Hash } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { getApiErrorMessage } from '../../services/api';
import Button from '../common/Button';
import Input from '../common/Input';
import toast from 'react-hot-toast';

export default function RegisterForm() {
  const { register: registerUser, login } = useAuth();
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm();

  const password = watch('password');

  const onSubmit = async (data) => {
    setIsLoading(true);
    try {
      await registerUser({
        full_name: data.full_name,
        company_name: data.company_name,
        phone: data.phone,
        gst_number: data.gst_number,
        email: data.email,
        password: data.password,
      });
      await login(data.email, data.password);
      toast.success('Registration successful. Logged in to your new account.');
      navigate('/dashboard', { replace: true });
    } catch (error) {
      toast.error(getApiErrorMessage(error, 'Registration failed'));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
      <Input
        label="Full Name"
        type="text"
        placeholder="Enter your full name"
        icon={User}
        error={errors.full_name?.message}
        registration={register('full_name', {
          required: 'Full Name is required',
          minLength: {
            value: 2,
            message: 'Name must be at least 2 characters',
          },
        })}
      />

      <Input
        label="Company Name"
        type="text"
        placeholder="Enter your company name"
        icon={Building}
        error={errors.company_name?.message}
        registration={register('company_name', {
          required: 'Company Name is required',
        })}
      />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <Input
          label="Phone Number"
          type="tel"
          placeholder="Phone number"
          icon={Phone}
          error={errors.phone?.message}
          registration={register('phone', {
            required: 'Phone number is required',
          })}
        />

        <Input
          label="GST Number (Optional)"
          type="text"
          placeholder="15-char GST"
          icon={Hash}
          error={errors.gst_number?.message}
          registration={register('gst_number', {
            validate: v => !v || v.length === 15 || 'Must be exactly 15 characters',
          })}
        />
      </div>

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
          placeholder="Create a password"
          icon={Lock}
          inputClassName="pr-12"
          error={errors.password?.message}
          registration={register('password', {
            required: 'Password is required',
            minLength: {
              value: 8,
              message: 'Password must be at least 8 characters',
            },
            validate: {
              hasLetter: (value) =>
                /[a-zA-Z]/.test(value) || 'Password must contain at least one letter',
              hasNumber: (value) =>
                /\d/.test(value) || 'Password must contain at least one number',
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

      <div className="relative">
        <Input
          label="Confirm Password"
          type={showPassword ? 'text' : 'password'}
          placeholder="Confirm your password"
          icon={Lock}
          inputClassName="pr-12"
          error={errors.confirmPassword?.message}
          registration={register('confirmPassword', {
            required: 'Please confirm your password',
            validate: (value) => value === password || 'Passwords do not match',
          })}
        />
      </div>

      <Button
        type="submit"
        variant="primary"
        fullWidth
        isLoading={isLoading}
      >
        Sign Up
      </Button>
    </form>
  );
}

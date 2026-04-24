import { useEffect, useRef, useState } from 'react';
import { useForm } from 'react-hook-form';
import { User, Mail, Phone, Building2, MapPin, ShieldCheck, ImagePlus } from 'lucide-react';
import toast from 'react-hot-toast';
import { useAuth } from '../context/AuthContext';
import { getApiErrorMessage } from '../services/api';
import Button from '../components/common/Button';
import Input from '../components/common/Input';

export default function ProfilePage() {
  const { user, updateProfile, uploadLogo } = useAuth();
  const [isUploadingLogo, setIsUploadingLogo] = useState(false);
  const logoInputRef = useRef(null);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm({
    defaultValues: {
      email: '',
      full_name: '',
      company_name: '',
      phone: '',
      address: '',
      gst_number: '',
      company_logo_url: '',
      default_terms_conditions: '',
    },
  });

  useEffect(() => {
    if (!user) return;
    reset({
      email: user.email || '',
      full_name: user.full_name || '',
      company_name: user.company_name || '',
      phone: user.phone || '',
      address: user.address || '',
      gst_number: user.gst_number || '',
      company_logo_url: user.company_logo_url || '',
      default_terms_conditions: user.default_terms_conditions || '',
    });
  }, [user, reset]);

  const onSubmit = async (data) => {
    try {
      await updateProfile(data);
      toast.success('Profile updated');
    } catch (error) {
      toast.error(getApiErrorMessage(error, 'Failed to update profile'));
    }
  };

  const handleLogoFileChange = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setIsUploadingLogo(true);
    try {
      await uploadLogo(file);
      toast.success('Logo uploaded');
    } catch (error) {
      toast.error(getApiErrorMessage(error, 'Failed to upload logo'));
    } finally {
      setIsUploadingLogo(false);
      event.target.value = '';
    }
  };

  return (
    <div className="relative min-h-[80vh] space-y-8 pb-20">
      <div className="flex items-center justify-between border-b border-black pb-4">
        <h1 className="text-2xl font-light uppercase tracking-tighter text-on-surface md:text-3xl">PROFILE</h1>
      </div>

      <div className="overflow-hidden border border-black bg-surface-white">
        <div className="p-6 sm:p-8">
          <div className="mb-8 flex items-center gap-4 border-b border-black pb-6">
            <div className="shrink-0 border-2 border-black bg-black p-3 text-white">
              <ShieldCheck className="h-7 w-7" strokeWidth={1.75} />
            </div>
            <div>
              <p className="font-mono text-[10px] uppercase tracking-widest text-on-surface">ACCOUNT</p>
              <p className="mt-1 font-mono text-[10px] uppercase tracking-widest text-outline-muted">
                BUSINESS PROFILE & BRANDING
              </p>
            </div>
          </div>

          <div className="mb-8 border border-outline-variant p-5">
            <p className="mb-4 stitch-label">Company logo</p>
            <div className="flex flex-col items-start gap-4 sm:flex-row sm:items-center sm:gap-6">
              <div className="flex h-24 w-24 shrink-0 items-center justify-center overflow-hidden border border-black bg-white sm:h-28 sm:w-28">
                {user?.company_logo_url ? (
                  <img
                    src={user.company_logo_url}
                    alt="Company logo"
                    className="h-full w-full object-contain p-2"
                    width="128"
                    height="128"
                  />
                ) : (
                  <Building2 className="h-10 w-10 text-on-surface" strokeWidth={1.75} />
                )}
              </div>
              <div className="flex flex-col gap-3">
                <div>
                  <p className="text-xs font-normal  tracking-tight text-on-surface">Upload</p>
                  <p className="mt-1    text-outline-muted">
                    JPG, PNG, WEBP, GIF up to 5MB
                  </p>
                </div>
                <input
                  ref={logoInputRef}
                  type="file"
                  accept="image/*"
                  className="hidden"
                  onChange={handleLogoFileChange}
                />
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => logoInputRef.current?.click()}
                  isLoading={isUploadingLogo}
                  className="w-fit"
                >
                  <ImagePlus className="mr-2 h-4 w-4" strokeWidth={2} />
                  Upload
                </Button>
              </div>
            </div>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
              <div className="space-y-5">
                <Input
                  label="Full name"
                  icon={User}
                  error={errors.full_name?.message}
                  registration={register('full_name', {
                    required: 'Full name is required',
                    minLength: { value: 2, message: 'Minimum 2 characters' },
                  })}
                />
                <Input
                  label="Email"
                  type="email"
                  icon={Mail}
                  error={errors.email?.message}
                  registration={register('email', {
                    required: 'Email is required',
                    pattern: {
                      value: /\S+@\S+\.\S+/,
                      message: 'Invalid email address',
                    },
                  })}
                />
                <Input
                  label="Company name"
                  icon={Building2}
                  error={errors.company_name?.message}
                  registration={register('company_name')}
                />
              </div>
              <div className="space-y-5">
                <Input
                  label="Phone"
                  icon={Phone}
                  error={errors.phone?.message}
                  registration={register('phone')}
                />
                <Input
                  label="GST number"
                  icon={ShieldCheck}
                  error={errors.gst_number?.message}
                  helperText="15 characters if applicable"
                  registration={register('gst_number', {
                    validate: (value) => {
                      if (!value) return true;
                      return value.length === 15 || 'GST number must be 15 characters';
                    },
                  })}
                />
                <Input
                  label="Address"
                  icon={MapPin}
                  error={errors.address?.message}
                  registration={register('address')}
                />
              </div>
              <div className="md:col-span-2 space-y-5">
                <div>
                  <label className="mb-1.5 block stitch-label">Default terms &amp; conditions</label>
                  <textarea
                    rows={4}
                    className="stitch-input min-h-[6rem] w-full"
                    placeholder="Enter terms and conditions that will automatically pre-fill on new quotations..."
                    {...register('default_terms_conditions')}
                  />
                  {errors.default_terms_conditions && (
                    <p className="mt-1 text-xs text-red-500">{errors.default_terms_conditions.message}</p>
                  )}
                </div>
              </div>
            </div>
            <div className="border-t border-black pt-6">
              <Button type="submit" fullWidth isLoading={isSubmitting}>
                Save profile
              </Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

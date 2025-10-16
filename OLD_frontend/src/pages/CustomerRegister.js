import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { useAuth } from '../contexts/AuthContext';
import { UserIcon, EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

const CustomerRegister = () => {
  const { register, handleSubmit, watch, formState: { errors, isSubmitting } } = useForm();
  const { registerCustomer } = useAuth();
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  
  const isBusiness = watch('is_business', false);

  const onSubmit = async (data) => {
    const result = await registerCustomer({
      ...data,
      is_business: data.is_business || false
    });
    
    if (result.success) {
      toast.success('Registration successful! Please login with your credentials.');
      navigate('/login');
    } else {
      if (typeof result.error === 'object') {
        Object.entries(result.error).forEach(([field, messages]) => {
          const message = Array.isArray(messages) ? messages[0] : messages;
          toast.error(`${field}: ${message}`);
        });
      } else {
        toast.error(result.error);
      }
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <div className="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-primary-100">
            <UserIcon className="h-8 w-8 text-primary-600" />
          </div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Register as Customer
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Already have an account?{' '}
            <Link to="/login" className="font-medium text-primary-600 hover:text-primary-500">
              Sign in here
            </Link>
          </p>
        </div>
        
        <form className="mt-8 space-y-6" onSubmit={handleSubmit(onSubmit)}>
          <div className="space-y-4">
            {/* Account Type */}
            <div>
              <label className="form-label">Account Type</label>
              <div className="flex space-x-4">
                <label className="flex items-center">
                  <input
                    type="radio"
                    value={false}
                    className="h-4 w-4 text-primary-600"
                    {...register('is_business')}
                  />
                  <span className="ml-2 text-sm text-gray-700">Individual</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="radio"
                    value={true}
                    className="h-4 w-4 text-primary-600"
                    {...register('is_business')}
                  />
                  <span className="ml-2 text-sm text-gray-700">Business</span>
                </label>
              </div>
            </div>

            {/* Username */}
            <div>
              <label htmlFor="username" className="form-label">Username</label>
              <input
                id="username"
                type="text"
                className="form-input"
                placeholder="Choose a username"
                {...register('username', { 
                  required: 'Username is required',
                  minLength: { value: 3, message: 'Username must be at least 3 characters' }
                })}
              />
              {errors.username && (
                <p className="mt-1 text-sm text-red-600">{errors.username.message}</p>
              )}
            </div>

            {/* Email */}
            <div>
              <label htmlFor="email" className="form-label">Email</label>
              <input
                id="email"
                type="email"
                className="form-input"
                placeholder="your@email.com"
                {...register('email', { 
                  required: 'Email is required',
                  pattern: {
                    value: /^\S+@\S+$/i,
                    message: 'Invalid email address'
                  }
                })}
              />
              {errors.email && (
                <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
              )}
            </div>

            {/* Password */}
            <div>
              <label htmlFor="password" className="form-label">Password</label>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  className="form-input pr-10"
                  placeholder="Create a password"
                  {...register('password', { 
                    required: 'Password is required',
                    minLength: { value: 8, message: 'Password must be at least 8 characters' }
                  })}
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? (
                    <EyeSlashIcon className="h-5 w-5 text-gray-400" />
                  ) : (
                    <EyeIcon className="h-5 w-5 text-gray-400" />
                  )}
                </button>
              </div>
              {errors.password && (
                <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
              )}
            </div>

            {/* First Name */}
            <div>
              <label htmlFor="first_name" className="form-label">First Name</label>
              <input
                id="first_name"
                type="text"
                className="form-input"
                placeholder="Your first name"
                {...register('first_name', { required: 'First name is required' })}
              />
              {errors.first_name && (
                <p className="mt-1 text-sm text-red-600">{errors.first_name.message}</p>
              )}
            </div>

            {/* Last Name */}
            <div>
              <label htmlFor="last_name" className="form-label">Last Name</label>
              <input
                id="last_name"
                type="text"
                className="form-input"
                placeholder="Your last name"
                {...register('last_name', { required: 'Last name is required' })}
              />
              {errors.last_name && (
                <p className="mt-1 text-sm text-red-600">{errors.last_name.message}</p>
              )}
            </div>

            {/* Phone Number */}
            <div>
              <label htmlFor="phone_number" className="form-label">Phone Number</label>
              <input
                id="phone_number"
                type="tel"
                className="form-input"
                placeholder="(555) 123-4567"
                {...register('phone_number', { required: 'Phone number is required' })}
              />
              {errors.phone_number && (
                <p className="mt-1 text-sm text-red-600">{errors.phone_number.message}</p>
              )}
            </div>

            {/* Address */}
            <div>
              <label htmlFor="address" className="form-label">Address</label>
              <textarea
                id="address"
                rows={3}
                className="form-input"
                placeholder="Your full address"
                {...register('address', { required: 'Address is required' })}
              />
              {errors.address && (
                <p className="mt-1 text-sm text-red-600">{errors.address.message}</p>
              )}
            </div>

            {/* Company Name (if business) */}
            {isBusiness && (
              <div>
                <label htmlFor="company_name" className="form-label">Company Name</label>
                <input
                  id="company_name"
                  type="text"
                  className="form-input"
                  placeholder="Your company name"
                  {...register('company_name', { 
                    required: isBusiness ? 'Company name is required for business accounts' : false 
                  })}
                />
                {errors.company_name && (
                  <p className="mt-1 text-sm text-red-600">{errors.company_name.message}</p>
                )}
              </div>
            )}

            {/* Preferred Pickup Address */}
            <div>
              <label htmlFor="preferred_pickup_address" className="form-label">
                Preferred Pickup Address (Optional)
              </label>
              <textarea
                id="preferred_pickup_address"
                rows={2}
                className="form-input"
                placeholder="Alternative pickup address (if different from main address)"
                {...register('preferred_pickup_address')}
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={isSubmitting}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
            >
              {isSubmitting ? 'Creating Account...' : 'Create Account'}
            </button>
          </div>

          <div className="text-center">
            <Link
              to="/register/driver"
              className="text-sm text-gray-600 hover:text-gray-500"
            >
              Register as a driver instead?
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CustomerRegister;
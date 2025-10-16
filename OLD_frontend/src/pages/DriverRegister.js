import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { useAuth } from '../contexts/AuthContext';
import { TruckIcon, EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

const DriverRegister = () => {
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm();
  const { registerDriver } = useAuth();
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);

  const onSubmit = async (data) => {
    const result = await registerDriver(data);
    
    if (result.success) {
      toast.success('Driver registration successful! Please login with your credentials.');
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
          <div className="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-green-100">
            <TruckIcon className="h-8 w-8 text-green-600" />
          </div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Register as Driver
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
            {/* Personal Information */}
            <div className="border-b border-gray-200 pb-4">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Personal Information</h3>
              
              {/* Username */}
              <div className="mb-4">
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
              <div className="mb-4">
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
              <div className="mb-4">
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
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label htmlFor="first_name" className="form-label">First Name</label>
                  <input
                    id="first_name"
                    type="text"
                    className="form-input"
                    placeholder="First name"
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
                    placeholder="Last name"
                    {...register('last_name', { required: 'Last name is required' })}
                  />
                  {errors.last_name && (
                    <p className="mt-1 text-sm text-red-600">{errors.last_name.message}</p>
                  )}
                </div>
              </div>

              {/* Display Name (auto-filled) */}
              <div className="mb-4">
                <label htmlFor="name" className="form-label">Display Name</label>
                <input
                  id="name"
                  type="text"
                  className="form-input"
                  placeholder="Your full name"
                  {...register('name', { required: 'Display name is required' })}
                />
                {errors.name && (
                  <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
                )}
              </div>

              {/* Phone Number */}
              <div className="mb-4">
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

              {/* License Number */}
              <div>
                <label htmlFor="license_number" className="form-label">Driver's License Number</label>
                <input
                  id="license_number"
                  type="text"
                  className="form-input"
                  placeholder="DL123456789"
                  {...register('license_number', { required: 'License number is required' })}
                />
                {errors.license_number && (
                  <p className="mt-1 text-sm text-red-600">{errors.license_number.message}</p>
                )}
              </div>
            </div>

            {/* Vehicle Information */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Vehicle Information</h3>
              
              {/* Vehicle License Plate */}
              <div className="mb-4">
                <label htmlFor="vehicle_license_plate" className="form-label">Vehicle License Plate</label>
                <input
                  id="vehicle_license_plate"
                  type="text"
                  className="form-input"
                  placeholder="ABC123"
                  {...register('vehicle_license_plate', { required: 'Vehicle license plate is required' })}
                />
                {errors.vehicle_license_plate && (
                  <p className="mt-1 text-sm text-red-600">{errors.vehicle_license_plate.message}</p>
                )}
              </div>

              {/* Vehicle Model */}
              <div className="mb-4">
                <label htmlFor="vehicle_model" className="form-label">Vehicle Model</label>
                <input
                  id="vehicle_model"
                  type="text"
                  className="form-input"
                  placeholder="Ford Transit, Mercedes Sprinter, etc."
                  {...register('vehicle_model', { required: 'Vehicle model is required' })}
                />
                {errors.vehicle_model && (
                  <p className="mt-1 text-sm text-red-600">{errors.vehicle_model.message}</p>
                )}
              </div>

              {/* Vehicle Capacity */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label htmlFor="vehicle_capacity" className="form-label">Capacity</label>
                  <input
                    id="vehicle_capacity"
                    type="number"
                    min="1"
                    max="50000"
                    className="form-input"
                    placeholder="1000"
                    {...register('vehicle_capacity', { 
                      required: 'Vehicle capacity is required',
                      min: { value: 1, message: 'Capacity must be at least 1' },
                      max: { value: 50000, message: 'Capacity must be less than 50,000' }
                    })}
                  />
                  {errors.vehicle_capacity && (
                    <p className="mt-1 text-sm text-red-600">{errors.vehicle_capacity.message}</p>
                  )}
                </div>

                <div>
                  <label htmlFor="vehicle_capacity_unit" className="form-label">Unit</label>
                  <select
                    id="vehicle_capacity_unit"
                    className="form-input"
                    {...register('vehicle_capacity_unit', { required: 'Capacity unit is required' })}
                  >
                    <option value="kg">Kilograms (kg)</option>
                    <option value="lb">Pounds (lb)</option>
                  </select>
                  {errors.vehicle_capacity_unit && (
                    <p className="mt-1 text-sm text-red-600">{errors.vehicle_capacity_unit.message}</p>
                  )}
                </div>
              </div>
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={isSubmitting}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
            >
              {isSubmitting ? 'Registering...' : 'Register as Driver'}
            </button>
          </div>

          <div className="text-center">
            <Link
              to="/register/customer"
              className="text-sm text-gray-600 hover:text-gray-500"
            >
              Register as a customer instead?
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
};

export default DriverRegister;
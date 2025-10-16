import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useAuth } from '../contexts/AuthContext';
import { deliveryService } from '../services/apiService';
import { TruckIcon, MapPinIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

const RequestDelivery = () => {
  const { register, handleSubmit, watch, setValue, formState: { errors, isSubmitting } } = useForm();
  const { user } = useAuth();
  const [customerProfile, setCustomerProfile] = useState(null);

  // Watch checkbox values for real-time updates
  const samePickupAsCustomer = watch('same_pickup_as_customer', false);
  const usePreferredPickup = watch('use_preferred_pickup', false);
  const sameDropoffAsCustomer = watch('same_dropoff_as_customer', false);

  useEffect(() => {
    // Load customer profile for address auto-fill
    if (user) {
      setCustomerProfile(user);
    }
  }, [user]);

  // Auto-fill pickup location when checkbox changes
  useEffect(() => {
    if (customerProfile) {
      if (samePickupAsCustomer) {
        setValue('pickup_location', customerProfile.address);
      } else if (usePreferredPickup && customerProfile.preferred_pickup_address) {
        setValue('pickup_location', customerProfile.preferred_pickup_address);
      } else if (!samePickupAsCustomer && !usePreferredPickup) {
        setValue('pickup_location', '');
      }
    }
  }, [samePickupAsCustomer, usePreferredPickup, customerProfile, setValue]);

  // Auto-fill dropoff location when checkbox changes
  useEffect(() => {
    if (customerProfile && sameDropoffAsCustomer) {
      setValue('dropoff_location', customerProfile.address);
    } else if (!sameDropoffAsCustomer) {
      setValue('dropoff_location', '');
    }
  }, [sameDropoffAsCustomer, customerProfile, setValue]);

  const onSubmit = async (data) => {
    try {
      const result = await deliveryService.requestDelivery(data);
      toast.success('Delivery requested successfully!');
      // Reset form
      setValue('pickup_location', '');
      setValue('dropoff_location', '');
      setValue('same_pickup_as_customer', false);
      setValue('use_preferred_pickup', false);
      setValue('same_dropoff_as_customer', false);
      setValue('item_description', '');
      setValue('delivery_date', '');
      setValue('delivery_time', '');
      setValue('special_instructions', '');
    } catch (error) {
      console.error('Delivery request failed:', error);
      if (error.response?.data) {
        const errors = error.response.data;
        Object.entries(errors).forEach(([field, messages]) => {
          const message = Array.isArray(messages) ? messages[0] : messages;
          toast.error(`${field}: ${message}`);
        });
      } else {
        toast.error('Failed to request delivery. Please try again.');
      }
    }
  };

  // Get tomorrow's date as minimum date
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  const minDate = tomorrow.toISOString().split('T')[0];

  return (
    <div className="max-w-2xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      <div className="card p-6">
        <div className="flex items-center mb-6">
          <TruckIcon className="h-8 w-8 text-primary-600 mr-3" />
          <h1 className="text-2xl font-bold text-gray-900">Request Delivery</h1>
        </div>

        {customerProfile && (
          <div className="mb-6 p-4 bg-blue-50 rounded-lg">
            <h3 className="text-sm font-medium text-blue-800 mb-2">Your Profile</h3>
            <p className="text-sm text-blue-700">
              <strong>Address:</strong> {customerProfile.address}
            </p>
            {customerProfile.preferred_pickup_address && (
              <p className="text-sm text-blue-700 mt-1">
                <strong>Preferred Pickup:</strong> {customerProfile.preferred_pickup_address}
              </p>
            )}
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* Pickup Location Section */}
          <div className="space-y-4">
            <div className="flex items-center">
              <MapPinIcon className="h-5 w-5 text-green-600 mr-2" />
              <h3 className="text-lg font-medium text-gray-900">Pickup Location</h3>
            </div>

            {/* Pickup Checkboxes */}
            <div className="space-y-2">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  {...register('same_pickup_as_customer')}
                />
                <span className="ml-2 text-sm text-gray-700">
                  ✅ Pickup location is same as my address
                </span>
              </label>

              {customerProfile?.preferred_pickup_address && (
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                    disabled={samePickupAsCustomer}
                    {...register('use_preferred_pickup')}
                  />
                  <span className={`ml-2 text-sm ${samePickupAsCustomer ? 'text-gray-400' : 'text-gray-700'}`}>
                    📍 Use my preferred pickup address
                  </span>
                </label>
              )}
            </div>

            {/* Pickup Address Field */}
            <div>
              <label htmlFor="pickup_location" className="form-label">
                Pickup Address
              </label>
              <textarea
                id="pickup_location"
                rows={3}
                className={`form-input ${(samePickupAsCustomer || usePreferredPickup) ? 'bg-gray-100' : ''}`}
                placeholder="Enter pickup address or use checkboxes above"
                readOnly={samePickupAsCustomer || usePreferredPickup}
                {...register('pickup_location', { 
                  required: !samePickupAsCustomer && !usePreferredPickup ? 'Pickup location is required' : false 
                })}
              />
              {errors.pickup_location && (
                <p className="mt-1 text-sm text-red-600">{errors.pickup_location.message}</p>
              )}
            </div>
          </div>

          {/* Dropoff Location Section */}
          <div className="space-y-4">
            <div className="flex items-center">
              <MapPinIcon className="h-5 w-5 text-red-600 mr-2" />
              <h3 className="text-lg font-medium text-gray-900">Dropoff Location</h3>
            </div>

            {/* Dropoff Checkbox */}
            <div>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  {...register('same_dropoff_as_customer')}
                />
                <span className="ml-2 text-sm text-gray-700">
                  ✅ Dropoff location is same as my address
                </span>
              </label>
            </div>

            {/* Dropoff Address Field */}
            <div>
              <label htmlFor="dropoff_location" className="form-label">
                Dropoff Address
              </label>
              <textarea
                id="dropoff_location"
                rows={3}
                className={`form-input ${sameDropoffAsCustomer ? 'bg-gray-100' : ''}`}
                placeholder="Enter dropoff address or use checkbox above"
                readOnly={sameDropoffAsCustomer}
                {...register('dropoff_location', { 
                  required: !sameDropoffAsCustomer ? 'Dropoff location is required' : false 
                })}
              />
              {errors.dropoff_location && (
                <p className="mt-1 text-sm text-red-600">{errors.dropoff_location.message}</p>
              )}
            </div>
          </div>

          {/* Delivery Details */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900">Delivery Details</h3>

            {/* Item Description */}
            <div>
              <label htmlFor="item_description" className="form-label">
                Item Description
              </label>
              <input
                id="item_description"
                type="text"
                className="form-input"
                placeholder="e.g., Furniture, Electronics, Documents"
                {...register('item_description', { required: 'Item description is required' })}
              />
              {errors.item_description && (
                <p className="mt-1 text-sm text-red-600">{errors.item_description.message}</p>
              )}
            </div>

            {/* Delivery Date & Time */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="delivery_date" className="form-label">
                  Preferred Delivery Date
                </label>
                <input
                  id="delivery_date"
                  type="date"
                  min={minDate}
                  className="form-input"
                  {...register('delivery_date', { required: 'Delivery date is required' })}
                />
                {errors.delivery_date && (
                  <p className="mt-1 text-sm text-red-600">{errors.delivery_date.message}</p>
                )}
              </div>

              <div>
                <label htmlFor="delivery_time" className="form-label">
                  Preferred Time
                </label>
                <input
                  id="delivery_time"
                  type="time"
                  className="form-input"
                  {...register('delivery_time', { required: 'Delivery time is required' })}
                />
                {errors.delivery_time && (
                  <p className="mt-1 text-sm text-red-600">{errors.delivery_time.message}</p>
                )}
              </div>
            </div>

            {/* Special Instructions */}
            <div>
              <label htmlFor="special_instructions" className="form-label">
                Special Instructions (Optional)
              </label>
              <textarea
                id="special_instructions"
                rows={3}
                className="form-input"
                placeholder="Any special handling instructions, access codes, etc."
                {...register('special_instructions')}
              />
            </div>
          </div>

          {/* Submit Button */}
          <div className="pt-4">
            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full btn-primary disabled:opacity-50"
            >
              {isSubmitting ? 'Requesting Delivery...' : 'Request Delivery'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default RequestDelivery;
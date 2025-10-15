import React, { useState, useEffect } from 'react';
import { deliveryService } from '../services/apiService';
import { 
  TruckIcon,
  MapPinIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  FunnelIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

const MyDeliveries = () => {
  const [deliveries, setDeliveries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    loadDeliveries();
  }, []);

  const loadDeliveries = async () => {
    try {
      const response = await deliveryService.getMyDeliveries();
      setDeliveries(response.results || response || []);
    } catch (error) {
      console.error('Failed to load deliveries:', error);
      toast.error('Failed to load deliveries');
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'Pending':
        return <ClockIcon className="h-5 w-5 text-yellow-600" />;
      case 'En Route':
        return <TruckIcon className="h-5 w-5 text-blue-600" />;
      case 'Completed':
        return <CheckCircleIcon className="h-5 w-5 text-green-600" />;
      case 'Cancelled':
        return <XCircleIcon className="h-5 w-5 text-red-600" />;
      default:
        return <ClockIcon className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'En Route':
        return 'bg-blue-100 text-blue-800';
      case 'Completed':
        return 'bg-green-100 text-green-800';
      case 'Cancelled':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const filteredDeliveries = deliveries.filter(delivery => {
    if (filter === 'all') return true;
    return delivery.status.toLowerCase().replace(' ', '-') === filter;
  });

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">My Deliveries</h1>
        <p className="mt-2 text-gray-600">
          Track and manage all your delivery requests.
        </p>
      </div>

      {/* Filter Bar */}
      <div className="mb-6 flex items-center space-x-4">
        <FunnelIcon className="h-5 w-5 text-gray-400" />
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="form-input w-auto"
        >
          <option value="all">All Deliveries</option>
          <option value="pending">Pending</option>
          <option value="en-route">En Route</option>
          <option value="completed">Completed</option>
          <option value="cancelled">Cancelled</option>
        </select>
        <span className="text-sm text-gray-500">
          {filteredDeliveries.length} of {deliveries.length} deliveries
        </span>
      </div>

      {/* Deliveries List */}
      {filteredDeliveries.length === 0 ? (
        <div className="card p-8 text-center">
          <TruckIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">
            {filter === 'all' ? 'No deliveries yet' : `No ${filter} deliveries`}
          </h3>
          <p className="mt-1 text-sm text-gray-500">
            {filter === 'all' 
              ? 'Get started by requesting your first delivery.'
              : 'Try changing the filter to see other deliveries.'
            }
          </p>
          {filter === 'all' && (
            <div className="mt-6">
              <a
                href="/request-delivery"
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
              >
                <TruckIcon className="h-5 w-5 mr-2" />
                Request Delivery
              </a>
            </div>
          )}
        </div>
      ) : (
        <div className="space-y-4">
          {filteredDeliveries.map((delivery) => (
            <div key={delivery.id} className="card p-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  {/* Status and ID */}
                  <div className="flex items-center mb-4">
                    {getStatusIcon(delivery.status)}
                    <span className={`ml-2 px-3 py-1 text-sm font-medium rounded-full ${getStatusColor(delivery.status)}`}>
                      {delivery.status}
                    </span>
                    <span className="ml-4 text-lg font-semibold text-gray-900">
                      Delivery #{delivery.id}
                    </span>
                  </div>

                  {/* Locations */}
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-4">
                    <div>
                      <div className="flex items-start mb-2">
                        <MapPinIcon className="h-5 w-5 text-green-600 mt-0.5 mr-2 flex-shrink-0" />
                        <div>
                          <div className="font-medium text-gray-900">Pickup Location</div>
                          <div className="text-sm text-gray-600 mt-1">
                            {delivery.pickup_location}
                          </div>
                          {delivery.same_pickup_as_customer && (
                            <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-green-100 text-green-800 mt-1">
                              Same as my address
                            </span>
                          )}
                        </div>
                      </div>
                    </div>

                    <div>
                      <div className="flex items-start mb-2">
                        <MapPinIcon className="h-5 w-5 text-red-600 mt-0.5 mr-2 flex-shrink-0" />
                        <div>
                          <div className="font-medium text-gray-900">Dropoff Location</div>
                          <div className="text-sm text-gray-600 mt-1">
                            {delivery.dropoff_location}
                          </div>
                          {delivery.same_dropoff_as_customer && (
                            <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800 mt-1">
                              Same as my address
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Delivery Details */}
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-4">
                    <div>
                      <div className="font-medium text-gray-900 text-sm">Item</div>
                      <div className="text-gray-600 text-sm">{delivery.item_description}</div>
                    </div>
                    
                    <div className="flex items-center">
                      <ClockIcon className="h-4 w-4 text-gray-400 mr-2" />
                      <div>
                        <div className="font-medium text-gray-900 text-sm">Scheduled</div>
                        <div className="text-gray-600 text-sm">
                          {delivery.delivery_date} at {delivery.delivery_time}
                        </div>
                      </div>
                    </div>

                    <div>
                      <div className="font-medium text-gray-900 text-sm">Requested</div>
                      <div className="text-gray-600 text-sm">
                        {new Date(delivery.created_at).toLocaleDateString()}
                      </div>
                    </div>
                  </div>

                  {/* Special Instructions */}
                  {delivery.special_instructions && (
                    <div className="bg-gray-50 p-3 rounded-lg">
                      <div className="font-medium text-gray-900 text-sm mb-1">
                        Special Instructions
                      </div>
                      <div className="text-gray-600 text-sm">
                        {delivery.special_instructions}
                      </div>
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div className="ml-6 flex-shrink-0">
                  {delivery.status === 'Pending' && (
                    <button className="text-sm text-red-600 hover:text-red-500">
                      Cancel
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
};

export default MyDeliveries;
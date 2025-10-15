import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { deliveryService } from '../services/apiService';
import { 
  TruckIcon, 
  ClipboardDocumentListIcon,
  MapPinIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

const Dashboard = () => {
  const { user } = useAuth();
  const [deliveries, setDeliveries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    total: 0,
    pending: 0,
    enRoute: 0,
    completed: 0
  });

  useEffect(() => {
    loadDeliveries();
  }, []);

  const loadDeliveries = async () => {
    try {
      const response = await deliveryService.getMyDeliveries();
      setDeliveries(response.results || response || []);
      
      // Calculate stats
      const deliveriesArray = response.results || response || [];
      const newStats = {
        total: deliveriesArray.length,
        pending: deliveriesArray.filter(d => d.status === 'Pending').length,
        enRoute: deliveriesArray.filter(d => d.status === 'En Route').length,
        completed: deliveriesArray.filter(d => d.status === 'Completed').length
      };
      setStats(newStats);
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

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      {/* Welcome Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Welcome back, {user?.display_name || user?.username}!
        </h1>
        <p className="mt-2 text-gray-600">
          Here's an overview of your delivery activities.
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="card p-6">
          <div className="flex items-center">
            <ClipboardDocumentListIcon className="h-8 w-8 text-gray-600" />
            <div className="ml-4">
              <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
              <p className="text-sm text-gray-600">Total Deliveries</p>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center">
            <ClockIcon className="h-8 w-8 text-yellow-600" />
            <div className="ml-4">
              <p className="text-2xl font-bold text-gray-900">{stats.pending}</p>
              <p className="text-sm text-gray-600">Pending</p>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center">
            <TruckIcon className="h-8 w-8 text-blue-600" />
            <div className="ml-4">
              <p className="text-2xl font-bold text-gray-900">{stats.enRoute}</p>
              <p className="text-sm text-gray-600">En Route</p>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center">
            <CheckCircleIcon className="h-8 w-8 text-green-600" />
            <div className="ml-4">
              <p className="text-2xl font-bold text-gray-900">{stats.completed}</p>
              <p className="text-sm text-gray-600">Completed</p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Deliveries */}
      <div className="card">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">Recent Deliveries</h2>
        </div>
        
        {deliveries.length === 0 ? (
          <div className="p-8 text-center">
            <TruckIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No deliveries yet</h3>
            <p className="mt-1 text-sm text-gray-500">
              Get started by requesting your first delivery.
            </p>
            <div className="mt-6">
              <a
                href="/request-delivery"
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700"
              >
                <TruckIcon className="h-5 w-5 mr-2" />
                Request Delivery
              </a>
            </div>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {deliveries.slice(0, 5).map((delivery) => (
              <div key={delivery.id} className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center">
                      {getStatusIcon(delivery.status)}
                      <span className={`ml-2 px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(delivery.status)}`}>
                        {delivery.status}
                      </span>
                      <span className="ml-3 text-sm text-gray-500">
                        Delivery #{delivery.id}
                      </span>
                    </div>
                    
                    <div className="mt-3 space-y-2">
                      <div className="flex items-start">
                        <MapPinIcon className="h-4 w-4 text-green-600 mt-0.5 mr-2 flex-shrink-0" />
                        <div className="text-sm">
                          <span className="font-medium text-gray-900">From:</span>
                          <span className="ml-1 text-gray-600">{delivery.pickup_location}</span>
                        </div>
                      </div>
                      
                      <div className="flex items-start">
                        <MapPinIcon className="h-4 w-4 text-red-600 mt-0.5 mr-2 flex-shrink-0" />
                        <div className="text-sm">
                          <span className="font-medium text-gray-900">To:</span>
                          <span className="ml-1 text-gray-600">{delivery.dropoff_location}</span>
                        </div>
                      </div>
                      
                      <div className="flex items-center">
                        <ClockIcon className="h-4 w-4 text-gray-400 mr-2" />
                        <span className="text-sm text-gray-600">
                          {delivery.delivery_date} at {delivery.delivery_time}
                        </span>
                      </div>
                      
                      <div className="text-sm">
                        <span className="font-medium text-gray-900">Item:</span>
                        <span className="ml-1 text-gray-600">{delivery.item_description}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="text-right text-sm text-gray-500">
                    {new Date(delivery.created_at).toLocaleDateString()}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
        
        {deliveries.length > 5 && (
          <div className="px-6 py-4 border-t border-gray-200">
            <a
              href="/my-deliveries"
              className="text-sm text-primary-600 hover:text-primary-500 font-medium"
            >
              View all deliveries →
            </a>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
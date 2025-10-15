# Delivery App Frontend

React frontend for the Delivery App backend API. Provides a complete user interface for customers to register, request deliveries, and track their packages.

## Features

- **Customer Registration & Authentication**: JWT-based login/register system
- **Driver Self-Registration**: Drivers can register with vehicle information
- **Smart Delivery Request Form**: Auto-fills addresses based on user preferences
- **Dashboard**: View delivery statistics and recent deliveries
- **My Deliveries**: Track all delivery requests with filtering
- **Responsive Design**: Works on desktop and mobile devices
- **Real-time Updates**: Live form validation and status updates

## Tech Stack

- React 18 with Hooks
- React Router for navigation
- React Hook Form for form management
- Axios for API communication
- Tailwind CSS for styling
- Heroicons for icons
- React Hot Toast for notifications

## Prerequisites

Before running the frontend, ensure:

1. **Backend is running**: Django backend should be running on `http://localhost:8000`
2. **Node.js installed**: Version 16 or higher
3. **Backend API accessible**: All required endpoints should be available

## Installation & Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Install additional required packages**:
   ```bash
   npm install react-hot-toast @heroicons/react
   ```

4. **Start development server**:
   ```bash
   npm start
   ```

5. **Access the application**:
   - Open `http://localhost:3000` in your browser
   - Backend proxy is configured to forward API calls to `http://localhost:8000`

## Project Structure

```
frontend/
├── public/
│   └── index.html              # Main HTML template
├── src/
│   ├── components/
│   │   ├── Navbar.js           # Navigation component
│   │   └── ProtectedRoute.js   # Route protection
│   ├── contexts/
│   │   └── AuthContext.js      # Authentication context
│   ├── pages/
│   │   ├── Login.js            # Login form
│   │   ├── CustomerRegister.js # Customer registration
│   │   ├── DriverRegister.js   # Driver registration  
│   │   ├── Dashboard.js        # Main dashboard
│   │   ├── RequestDelivery.js  # Delivery request form
│   │   └── MyDeliveries.js     # Delivery tracking
│   ├── services/
│   │   ├── api.js              # Axios configuration
│   │   └── apiService.js       # API service functions
│   ├── App.js                  # Main app component
│   ├── index.js                # React entry point
│   └── index.css               # Global styles
├── package.json                # Dependencies and scripts
├── tailwind.config.js          # Tailwind configuration
└── postcss.config.js           # PostCSS configuration
```

## Available Scripts

- `npm start`: Runs the app in development mode
- `npm run build`: Builds the app for production
- `npm test`: Launches the test runner
- `npm run eject`: Ejects from Create React App (one-way operation)

## Authentication Flow

1. **Registration**: Users register as customers or drivers
2. **Login**: JWT tokens are issued and stored in localStorage
3. **Automatic Refresh**: Tokens are automatically refreshed before expiration
4. **Protected Routes**: Private pages require authentication
5. **Logout**: Clears tokens and redirects to login

## API Integration

The frontend communicates with the Django backend through:

- **Base URL**: `http://localhost:8000/api/`
- **Proxy Configuration**: Development server proxies API calls
- **JWT Authentication**: Tokens included in request headers
- **Error Handling**: Automatic token refresh and error display

## Key Features

### Smart Delivery Form
- Checkboxes for "Same as my address" options
- Auto-fills pickup/dropoff locations
- Real-time form validation
- Preferred pickup address support

### Dashboard
- Delivery statistics cards
- Recent deliveries overview
- Quick action buttons
- Responsive grid layout

### My Deliveries
- Filter by delivery status
- Detailed delivery information
- Visual status indicators
- Cancel pending deliveries

## Configuration

### Backend Integration
The `package.json` includes a proxy configuration:
```json
"proxy": "http://localhost:8000"
```

This forwards all API requests to the Django backend during development.

### Tailwind CSS
Custom primary colors and utility classes are configured in `tailwind.config.js`.

### Environment Variables
For production, you may need to configure:
- `REACT_APP_API_URL`: Backend API base URL
- `REACT_APP_API_TIMEOUT`: Request timeout (default: 10000ms)

## Deployment

### Development
```bash
npm start
```
Runs on `http://localhost:3000` with hot reload.

### Production Build
```bash
npm run build
```
Creates optimized production build in `build/` folder.

### Production Deployment
1. Build the application: `npm run build`
2. Serve the `build/` folder with a web server
3. Configure API URL for production backend
4. Ensure CORS is properly configured on backend

## Troubleshooting

### Common Issues

1. **API Connection Errors**:
   - Ensure Django backend is running on port 8000
   - Check CORS configuration in Django settings
   - Verify proxy configuration in package.json

2. **Authentication Issues**:
   - Clear localStorage and try logging in again
   - Check JWT token expiration settings
   - Verify backend authentication endpoints

3. **Styling Issues**:
   - Ensure Tailwind CSS is properly installed
   - Check PostCSS configuration
   - Verify custom CSS classes in tailwind.config.js

4. **Routing Issues**:
   - Check React Router configuration
   - Verify protected route implementation
   - Ensure all routes are properly defined

## Development Notes

- The frontend assumes the Django backend is running with all required endpoints
- JWT tokens are stored in localStorage with automatic refresh
- Form validation uses React Hook Form with real-time validation
- All API calls include proper error handling and loading states
- Components are designed to be responsive and accessible

## Next Steps

To extend the application:

1. Add real-time delivery tracking with WebSockets
2. Implement push notifications for delivery updates
3. Add delivery rating and feedback system
4. Create admin dashboard for delivery management
5. Add payment integration for delivery services
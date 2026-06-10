# from rest_framework import viewsets
# from .models import Delivery
# from .serializers import DeliverySerializer

# class DeliveryViewSet(viewsets.ModelViewSet):
#     queryset = Delivery.objects.all()
#     serializer_class = DeliverySerializer

# Updated to include JWT authentication and permissions
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import Delivery, Driver, Vehicle, DriverVehicle, DeliveryAssignment, Customer
from .driver_utils import get_driver_for_user, get_current_assignment, get_driver_vehicle
from .vehicle_utils import deactivate_vehicle, reactivate_vehicle, vehicle_has_history
from .auth_logging import log_registration_validation_failure
from .serializers import (DeliverySerializer, DriverSerializer, VehicleSerializer, DriverVehicleSerializer, 
                         DeliveryAssignmentSerializer, DriverWithVehicleSerializer, CustomerSerializer, 
                         CustomerRegistrationSerializer, DeliveryCreateSerializer, DriverRegistrationSerializer,
                         DriverMeSerializer, DriverOwnedVehicleSerializer)

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Customers can only see their own profile, staff can see all
        if self.request.user.is_staff:
            return Customer.objects.all()
        return Customer.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'], permission_classes=[])
    def register(self, request):
        """Public endpoint for customer registration"""
        serializer = CustomerRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.save()
            return Response({
                'message': 'Customer registered successfully',
                'customer': CustomerSerializer(customer).data
            }, status=status.HTTP_201_CREATED)
        log_registration_validation_failure(request, 'customer', serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's customer profile"""
        try:
            customer = request.user.customer_profile
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        except Customer.DoesNotExist:
            return Response({'error': 'Customer profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def my_deliveries(self, request):
        """Get current customer's deliveries"""
        try:
            customer = request.user.customer_profile
            deliveries = customer.deliveries.all().order_by('-created_at')
            serializer = DeliverySerializer(deliveries, many=True)
            return Response(serializer.data)
        except Customer.DoesNotExist:
            return Response({'error': 'Customer profile not found'}, status=status.HTTP_404_NOT_FOUND)


class DeliveryViewSet(viewsets.ModelViewSet):
    queryset = Delivery.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create' and not self.request.user.is_staff:
            return DeliveryCreateSerializer
        return DeliverySerializer
    
    def get_queryset(self):
        # Customers can only see their own deliveries, staff can see all
        if self.request.user.is_staff:
            return Delivery.objects.all()
        try:
            customer = self.request.user.customer_profile
            return Delivery.objects.filter(customer=customer)
        except Customer.DoesNotExist:
            return Delivery.objects.none()
    
    @action(detail=False, methods=['post'])
    def request_delivery(self, request):
        """Customer endpoint to request a new delivery"""
        try:
            customer = request.user.customer_profile
        except Customer.DoesNotExist:
            return Response({'error': 'Customer profile required to request deliveries'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        serializer = DeliveryCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            delivery = serializer.save()
            return Response({
                'message': 'Delivery requested successfully',
                'delivery': DeliverySerializer(delivery).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Driver.objects.all()
        return Driver.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied('Only staff can create drivers via this endpoint. Use /drivers/register/.')
        return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied('Only staff can delete drivers.')
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get', 'patch'])
    def me(self, request):
        """Get or update the authenticated user's driver profile."""
        driver = get_driver_for_user(request.user)
        if not driver:
            return Response({'error': 'Driver profile not found'}, status=status.HTTP_404_NOT_FOUND)
        if request.method == 'GET':
            return Response(DriverMeSerializer(driver).data)
        serializer = DriverMeSerializer(driver, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(DriverMeSerializer(driver).data)

    @action(detail=False, methods=['get', 'patch'], url_path='me/vehicle')
    def me_vehicle(self, request):
        """Get or update the vehicle currently assigned to the authenticated driver."""
        driver = get_driver_for_user(request.user)
        if not driver:
            return Response({'error': 'Driver profile not found'}, status=status.HTTP_404_NOT_FOUND)
        vehicle = get_driver_vehicle(driver)
        if not vehicle:
            return Response({'error': 'No vehicle assigned to this driver'}, status=status.HTTP_404_NOT_FOUND)
        if request.method == 'GET':
            return Response(DriverOwnedVehicleSerializer(vehicle).data)
        assignment = get_current_assignment(driver)
        if not assignment or assignment.vehicle_id != vehicle.id:
            if not vehicle.active:
                return Response(
                    {'error': 'Vehicle is inactive. Contact admin to reactivate before editing.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        serializer = DriverOwnedVehicleSerializer(vehicle, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        vehicle.refresh_from_db()
        return Response(DriverOwnedVehicleSerializer(vehicle).data)

    @action(detail=False, methods=['post'], url_path='me/vehicle/deactivate')
    def me_vehicle_deactivate(self, request):
        """Driver marks their currently assigned vehicle inactive (sold, repair, etc.)."""
        driver = get_driver_for_user(request.user)
        if not driver:
            return Response({'error': 'Driver profile not found'}, status=status.HTTP_404_NOT_FOUND)

        vehicle = get_driver_vehicle(driver)
        if not vehicle:
            return Response({'error': 'No vehicle assigned to this driver'}, status=status.HTTP_404_NOT_FOUND)
        if not vehicle.active:
            return Response(
                {
                    'detail': 'Vehicle is already inactive.',
                    'id': vehicle.id,
                    'active': False,
                    'deactivated': True,
                },
                status=status.HTTP_200_OK,
            )

        deactivate_vehicle(vehicle)
        return Response(
            {
                'detail': (
                    'Your vehicle has been marked inactive. '
                    'Contact admin to assign a new vehicle or reactivate this one.'
                ),
                'id': vehicle.id,
                'active': False,
                'deactivated': True,
            },
            status=status.HTTP_200_OK,
        )
    
    def list(self, request, *args, **kwargs):
        """Override list to include available vehicles for admin driver creation."""
        response = super().list(request, *args, **kwargs)
        if request.user.is_staff and isinstance(response.data, dict):
            available_vehicles = Vehicle.objects.filter(active=True).values(
                'id', 'license_plate', 'model', 'capacity'
            )
            response.data['available_vehicles'] = list(available_vehicles)
        return response
    
    @action(detail=False, methods=['get'])
    def creation_data(self, request):
        """Endpoint to get data needed for driver creation form"""
        available_vehicles = Vehicle.objects.filter(active=True).values(
            'id', 'license_plate', 'model', 'capacity', 'capacity_unit'
        )
        
        # Add capacity_display to each vehicle
        vehicles_with_display = []
        for vehicle in available_vehicles:
            vehicle_obj = Vehicle.objects.get(id=vehicle['id'])
            vehicle['capacity_display'] = vehicle_obj.capacity_display
            vehicles_with_display.append(vehicle)
        
        return Response({
            'available_vehicles': vehicles_with_display,
            'capacity_units': Vehicle.CAPACITY_UNIT_CHOICES,
            'help': {
                'vehicle_id': 'Optional: Select a vehicle to assign to this driver immediately',
                'assigned_from': 'Optional: Date when vehicle assignment starts (defaults to today)',
                'capacity_unit': 'Choose between kg (kilograms) or lb (pounds)'
            }
        })
    
    @action(detail=True, methods=['post'])
    def assign_vehicle(self, request, pk=None):
        """Assign or reassign a vehicle to an existing driver"""
        driver = self.get_object()
        vehicle_id = request.data.get('vehicle_id')
        assigned_from = request.data.get('assigned_from')
        
        if not vehicle_id:
            return Response({'error': 'vehicle_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from django.utils import timezone
            
            vehicle = Vehicle.objects.get(id=vehicle_id, active=True)
            assigned_from = assigned_from or timezone.now().date()
            
            # End current assignments
            current_assignments = DriverVehicle.objects.filter(
                driver=driver,
                assigned_to__isnull=True
            )
            for assignment in current_assignments:
                assignment.assigned_to = timezone.now().date()
                assignment.save()
            
            # Create new assignment
            new_assignment = DriverVehicle.objects.create(
                driver=driver,
                vehicle=vehicle,
                assigned_from=assigned_from
            )
            
            serializer = DriverVehicleSerializer(new_assignment)
            return Response({
                'message': f'Vehicle {vehicle.license_plate} assigned to {driver.first_name} {driver.last_name}',
                'assignment': serializer.data
            })
            
        except Vehicle.DoesNotExist:
            return Response({'error': 'Vehicle not found or inactive'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'])
    def create_with_vehicle(self, request):
        """Create a new driver with immediate vehicle assignment"""
        serializer = DriverWithVehicleSerializer(data=request.data)
        if serializer.is_valid():
            driver = serializer.save()
            
            # Return the created driver with current vehicle info
            driver_serializer = DriverSerializer(driver)
            return Response({
                'message': f'Driver {driver.first_name} {driver.last_name} created and assigned vehicle successfully',
                'driver': driver_serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[])
    def register(self, request):
        """Driver self-registration endpoint"""
        serializer = DriverRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                driver = serializer.save()
                
                # Return success with driver info (no sensitive data)
                return Response({
                    'message': f'Driver {driver.first_name} {driver.last_name} registered successfully',
                    'driver_id': driver.id,
                    'name': f'{driver.first_name} {driver.last_name}'
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response({
                    'error': 'Registration failed',
                    'details': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        log_registration_validation_failure(request, 'driver', serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated]

    def _require_staff(self, request):
        if not request.user.is_staff:
            raise PermissionDenied('Only staff can modify vehicles.')

    def create(self, request, *args, **kwargs):
        self._require_staff(request)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self._require_staff(request)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        self._require_staff(request)
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        self._require_staff(request)
        vehicle = self.get_object()
        if vehicle_has_history(vehicle):
            deactivate_vehicle(vehicle)
            return Response(
                {
                    'detail': (
                        'Vehicle has driver or delivery assignment history; '
                        'marked inactive instead of deleted.'
                    ),
                    'id': vehicle.id,
                    'active': False,
                    'deactivated': True,
                },
                status=status.HTTP_200_OK,
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'], url_path='deactivate')
    def deactivate(self, request, pk=None):
        self._require_staff(request)
        vehicle = self.get_object()
        deactivate_vehicle(vehicle)
        return Response(
            {
                'detail': 'Vehicle marked inactive.',
                'id': vehicle.id,
                'active': False,
                'deactivated': True,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=['post'], url_path='reactivate')
    def reactivate(self, request, pk=None):
        self._require_staff(request)
        vehicle = self.get_object()
        reactivate_vehicle(vehicle)
        return Response(
            {
                'detail': (
                    'Vehicle reactivated. '
                    'Insurance/registration reverification will be required in a future release.'
                ),
                'id': vehicle.id,
                'active': True,
            },
            status=status.HTTP_200_OK,
        )
    
    def list(self, request, *args, **kwargs):
        """Override list to include capacity unit choices for forms"""
        response = super().list(request, *args, **kwargs)
        
        # Add capacity unit choices for frontend forms
        response.data['capacity_unit_choices'] = Vehicle.CAPACITY_UNIT_CHOICES
        
        return response
    
    @action(detail=False, methods=['get'])
    def form_data(self, request):
        """Endpoint to get data needed for vehicle creation/editing forms"""
        return Response({
            'capacity_unit_choices': Vehicle.CAPACITY_UNIT_CHOICES,
            'help': {
                'capacity': 'Enter the vehicle load capacity as a positive number',
                'capacity_unit': 'Choose the unit of measurement (kg for kilograms, lb for pounds)',
                'license_plate': 'Enter unique vehicle license plate',
                'model': 'Enter vehicle model name'
            }
        })


class DriverVehicleViewSet(viewsets.ModelViewSet):
    queryset = DriverVehicle.objects.all()
    serializer_class = DriverVehicleSerializer
    permission_classes = [IsAuthenticated]


class DeliveryAssignmentViewSet(viewsets.ModelViewSet):
    queryset = DeliveryAssignment.objects.all()
    serializer_class = DeliveryAssignmentSerializer
    permission_classes = [IsAuthenticated]
# from rest_framework import viewsets
# from .models import Delivery
# from .serializers import DeliverySerializer

# class DeliveryViewSet(viewsets.ModelViewSet):
#     queryset = Delivery.objects.all()
#     serializer_class = DeliverySerializer

# Updated to include JWT authentication and permissions
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.http import Http404
from .models import Delivery, Driver, Vehicle, DriverVehicle, DeliveryAssignment, Customer, LegalDocument
from .driver_utils import get_driver_for_user, get_driver_vehicle
from .vehicle_constants import MAX_VEHICLE_CAPACITY_KG, MAX_VEHICLE_CAPACITY_LB
from .vehicle_utils import deactivate_vehicle, reactivate_vehicle, vehicle_has_history
from .vehicle_update import serialize_vehicle_for_user, update_vehicle, user_can_read_vehicle
from .auth_logging import log_registration_validation_failure
from . import compliance_service
from .compliance_permissions import (
    CanManageDriverDocuments,
    CanManageVehicleDocuments,
    CanVerifyLegalDocument,
    IsStaffOrDocumentOwner,
)
from .serializers import (DeliverySerializer, DriverSerializer, VehicleSerializer, DriverVehicleSerializer, 
                         DeliveryAssignmentSerializer, DriverWithVehicleSerializer, CustomerSerializer, 
                         CustomerRegistrationSerializer, DeliveryCreateSerializer, DriverRegistrationSerializer,
                         DriverMeSerializer, DriverOwnedVehicleSerializer, LegalDocumentSerializer,
                         LegalDocumentCreateSerializer, LegalDocumentVerifySerializer,
                         LegalDocumentRejectSerializer, PresignedUploadSerializer)

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
        vehicle = update_vehicle(request.user, vehicle, request.data, partial=True)
        return Response(serialize_vehicle_for_user(request.user, vehicle))

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

    @action(
        detail=True,
        methods=['get', 'post'],
        url_path='documents',
        permission_classes=[IsAuthenticated, CanManageDriverDocuments],
    )
    def documents(self, request, pk=None):
        driver = self.get_object()
        if request.method == 'GET':
            docs = compliance_service.list_documents_for_driver(driver)
            return Response(LegalDocumentSerializer(docs, many=True).data)
        serializer = LegalDocumentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        document = compliance_service.create_document(
            request.user,
            driver=driver,
            data=serializer.validated_data,
        )
        return Response(
            LegalDocumentSerializer(document).data,
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=False,
        methods=['get'],
        url_path='me/compliance-status',
    )
    def me_compliance_status(self, request):
        driver = get_driver_for_user(request.user)
        if not driver:
            return Response({'error': 'Driver profile not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(compliance_service.get_compliance_summary(driver))


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

    def retrieve(self, request, *args, **kwargs):
        vehicle = self.get_object()
        if not user_can_read_vehicle(request.user, vehicle):
            raise Http404()
        return Response(serialize_vehicle_for_user(request.user, vehicle))

    def update(self, request, *args, **kwargs):
        vehicle = self.get_object()
        vehicle = update_vehicle(request.user, vehicle, request.data, partial=False)
        return Response(serialize_vehicle_for_user(request.user, vehicle))

    def partial_update(self, request, *args, **kwargs):
        vehicle = self.get_object()
        vehicle = update_vehicle(request.user, vehicle, request.data, partial=True)
        return Response(serialize_vehicle_for_user(request.user, vehicle))

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
                'capacity': f'Enter load capacity (max {MAX_VEHICLE_CAPACITY_KG} kg or {MAX_VEHICLE_CAPACITY_LB} lb)',
                'capacity_unit': 'Choose the unit of measurement (kg for kilograms, lb for pounds)',
                'license_plate': 'Enter unique vehicle license plate',
                'model': 'Enter vehicle model name'
            }
        })

    @action(
        detail=True,
        methods=['get', 'post'],
        url_path='documents',
        permission_classes=[IsAuthenticated, CanManageVehicleDocuments],
    )
    def documents(self, request, pk=None):
        vehicle = self.get_object()
        if request.method == 'GET':
            docs = compliance_service.list_documents_for_vehicle(vehicle)
            return Response(LegalDocumentSerializer(docs, many=True).data)
        serializer = LegalDocumentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        document = compliance_service.create_document(
            request.user,
            vehicle=vehicle,
            data=serializer.validated_data,
        )
        return Response(
            LegalDocumentSerializer(document).data,
            status=status.HTTP_201_CREATED,
        )


class DriverVehicleViewSet(viewsets.ModelViewSet):
    queryset = DriverVehicle.objects.all()
    serializer_class = DriverVehicleSerializer
    permission_classes = [IsAuthenticated]


class DeliveryAssignmentViewSet(viewsets.ModelViewSet):
    queryset = DeliveryAssignment.objects.all()
    serializer_class = DeliveryAssignmentSerializer
    permission_classes = [IsAuthenticated]


class LegalDocumentViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = LegalDocument.objects.all()
    serializer_class = LegalDocumentSerializer
    permission_classes = [IsAuthenticated, IsStaffOrDocumentOwner]
    http_method_names = ['get', 'patch', 'post', 'head', 'options']

    def get_object(self):
        document = compliance_service.get_document_or_404(self.kwargs['pk'])
        self.check_object_permissions(self.request, document)
        return document

    def partial_update(self, request, *args, **kwargs):
        document = self.get_object()
        document = compliance_service.update_document(request.user, document, request.data)
        return Response(LegalDocumentSerializer(document).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, CanVerifyLegalDocument])
    def verify(self, request, pk=None):
        document = self.get_object()
        serializer = LegalDocumentVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        document = compliance_service.mark_verified(
            request.user,
            document.id,
            notes=serializer.validated_data.get('notes'),
        )
        return Response(LegalDocumentSerializer(document).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, CanVerifyLegalDocument])
    def reject(self, request, pk=None):
        document = self.get_object()
        serializer = LegalDocumentRejectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        document = compliance_service.mark_rejected(
            request.user,
            document.id,
            reason=serializer.validated_data['rejection_reason'],
        )
        return Response(LegalDocumentSerializer(document).data)

    @action(detail=False, methods=['post'], url_path='presigned-upload')
    def presigned_upload(self, request):
        serializer = PresignedUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        from rest_framework.exceptions import ValidationError as DRFValidationError
        try:
            result = compliance_service.get_presigned_upload_url(
                request.user,
                file_name=serializer.validated_data['file_name'],
                content_type=serializer.validated_data['content_type'],
                file_size=serializer.validated_data.get('file_size'),
            )
        except DRFValidationError as exc:
            return Response(exc.detail, status=status.HTTP_400_BAD_REQUEST)
        return Response(result)

    @action(detail=True, methods=['get'], url_path='download')
    def download(self, request, pk=None):
        document = self.get_object()
        from rest_framework.exceptions import ValidationError as DRFValidationError
        try:
            result = compliance_service.get_presigned_download_url(request.user, document)
        except DRFValidationError as exc:
            return Response(exc.detail, status=status.HTTP_400_BAD_REQUEST)
        return Response(result)
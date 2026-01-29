# Driver-Vehicle Logic Rules

## 1. Driver-Vehicle Relationship
- **Driver can own 0 to 5 vehicles**
  - A driver may register up to 5 vehicles.
  - 0 vehicles: Driver has no delivery vehicle (cannot be assigned deliveries).
  - 1 vehicle: This is the default delivery vehicle.
  - 2-5 vehicles: Driver owns multiple delivery vehicles (all must have valid VIN, insurance, and be marked 'Active').
- **Only 1 default delivery vehicle per driver**
  - If a driver owns multiple vehicles, only one can be selected as the default delivery vehicle at any time.
  - The default vehicle is used for automatic delivery assignments.

## 2. Vehicle-Driver Relationship
- **Vehicle can have 0 or 1 driver**
  - A vehicle may be unassigned (no driver) or assigned to a single driver at a time.

## 3. Registration and Assignment Rules
- **Driver can register more than 1 vehicle**
  - Each vehicle must have valid VIN, insurance, and be marked 'Active'.
  - Driver can select which vehicle is the default delivery vehicle.
- **Default Vehicle Selection**
  - Only one vehicle per driver can be set as default at a time.
  - Changing the default vehicle will unset the previous default.

## 4. Delivery Assignment Logic
- **Deliveries are assigned to the driver's default delivery vehicle**
  - If no default vehicle is set, driver cannot be assigned deliveries.

---

**See also:**
- `delivery/models.py` for implementation of driver-vehicle assignment logic
- `delivery/serializers.py` for validation of vehicle ownership and default selection
- `delivery/views.py` for endpoints to register vehicles and set default vehicle

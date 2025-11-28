# ManBus API Documentation

**Base URL:** `http://localhost:5000`

**Authentication:** Most endpoints require a JWT token sent via cookies (set automatically on login/register)

---

## Table of Contents
1. [Authentication API](#authentication-api)
2. [User API](#user-api)
3. [Bus API](#bus-api)
4. [Driver API](#driver-api)
5. [Route API](#route-api)
6. [Stop API](#stop-api)
7. [Health Check](#health-check)

---

## Authentication API

Base URL: `/api/auth`

### 1. Register User
**POST** `/api/auth/register`

Creates a new user account and returns authentication token via cookie.

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "confirm_password": "SecurePass123!",
  "name": "John Doe",
  "phone": "12345678901"
}
```

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit

**Response (201):**
```json
{
  "status": "success",
  "message": "User registered successfully",
  "data": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "name": "John Doe",
    "phone": "12345678901",
    "role": "User"
  }
}
```

**Note:** Authentication token is automatically set as a secure HTTP-only cookie.

---

### 2. Login
**POST** `/api/auth/login`

Authenticates user and returns token via cookie.

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```

**Response (200):**
```json
{
  "status": "success",
  "message": "Login successful",
  "data": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "name": "John Doe",
    "phone": "12345678901",
    "role": "User"
  }
}
```

**Note:** Authentication token is automatically set as a secure HTTP-only cookie.

---

### 3. Logout
**POST** `/api/auth/logout`

Logs out the user by blacklisting the authentication token and clearing cookies.

**Headers:** Requires authentication cookie

**Response (200):**
```json
{
  "status": "success",
  "message": "Logout successful"
}
```

**Note:** The authentication cookie is automatically cleared upon successful logout.

---

## User API

Base URL: `/api/users`

### 1. Create User (Admin Only)
**POST** `/api/users/`

**Headers:** Requires authentication + admin privileges

**Request Body:**
```json
{
  "username": "jane_doe",
  "email": "jane@example.com",
  "password": "SecurePass123!",
  "name": "Jane Doe",
  "phone": "09876543210",
  "admin": false
}
```

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit

**Response (201):**
```json
{
  "status": "success",
  "message": "User created successfully",
  "data": {
    "id": 2,
    "username": "jane_doe",
    "email": "jane@example.com",
    "name": "Jane Doe",
    "phone": "09876543210",
    "role": "User"
  }
}
```

---

### 2. Get Current User
**GET** `/api/users/`

**Headers:** Requires authentication

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "name": "John Doe",
    "phone": "12345678901",
    "role": "User",
    "updated_at": "2025-01-15T10:30:00",
    "deleted_at": null
  }
}
```

---

### 3. Get All Users (Admin Only)
**GET** `/api/users/all`

**Headers:** Requires authentication + admin privileges

**Query Parameters:**
- `cursor` (optional): User ID from last result for cursor-based pagination
- `limit` (optional): Number of results (default: 20, max: 100)
- `role` (optional): Filter by role (User, Driver, Admin)
- `include_deleted` (optional): Include soft-deleted users (true/false)

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "users": [
      {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "name": "John Doe",
        "phone": "12345678901",
        "role": "User"
      }
    ],
    "has_more": true,
    "next_cursor": 1,
    "count": 20
  }
}
```

**Note:** Uses cursor-based pagination for better performance with large datasets.

---

### 4. Update User
**PUT** `/api/users/`

**Headers:** Requires authentication

**Request Body:**
```json
{
  "username": "john_updated",
  "email": "john_new@example.com",
  "name": "John Updated",
  "phone": "11111111111"
}
```

**Response (200):**
```json
{
  "status": "success",
  "message": "User updated successfully"
}
```

**Note:** Users can only update their own information unless they are an admin.

---

### 5. Delete User (Admin Only)
**DELETE** `/api/users/by/{user_id}`

**Headers:** Requires authentication + admin privileges

**Response (200):**
```json
{
  "status": "success",
  "message": "User deleted successfully"
}
```

**Note:** This is a soft delete. The user is marked as deleted but not removed from the database.

---

### 6. Restore User (Admin Only)
**POST** `/api/users/restore/by/{user_id}`

**Headers:** Requires authentication + admin privileges

**Response (200):**
```json
{
  "status": "success",
  "message": "User restored successfully",
  "data": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "name": "John Doe"
  }
}
```

---

### 7. Search Users (Admin Only)
**GET** `/api/users/search`

**Headers:** Requires authentication + admin privileges

**Query Parameters:**
- `query` (optional): Search term for username/email/name

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "username": "john_doe",
      "email": "john@example.com",
      "name": "John Doe",
      "phone": "12345678901",
      "role": "User"
    }
  ]
}
```

---

## Bus API

Base URL: `/api/buses`

### 1. Create Bus (Admin Only)
**POST** `/api/buses/`

**Headers:** Requires authentication + admin privileges

**Request Body:**
```json
{
  "plate_number": "ABC-1234",
  "name": "Bus 101",
  "model": "Mercedes-Benz Sprinter",
  "status": "Active",
  "route_id": 1
}
```

**Response (201):**
```json
{
  "status": "success",
  "message": "Bus created successfully",
  "data": {
    "bus_id": 1,
    "plate_number": "ABC-1234",
    "name": "Bus 101",
    "model": "Mercedes-Benz Sprinter",
    "status": "Active",
    "route_id": 1
  }
}
```

---

### 2. Get Bus by ID
**GET** `/api/buses/{bus_id}`

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "bus_id": 1,
    "plate_number": "ABC-1234",
    "name": "Bus 101",
    "model": "Mercedes-Benz Sprinter",
    "status": "Active",
    "route_id": 1,
    "route_name": "Route 1",
    "current_location": {
      "latitude": 21.0285,
      "longitude": 105.8542
    }
  }
}
```

---

### 3. Get Bus by Plate Number
**GET** `/api/buses/plate/{plate_number}`

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "bus_id": 1,
    "plate_number": "ABC-1234",
    "name": "Bus 101"
  }
}
```

---

### 4. Get All Active Buses
**GET** `/api/buses/active`

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "bus_id": 1,
      "plate_number": "ABC-1234",
      "status": "Active"
    }
  ]
}
```

---

### 5. Get All Buses
**GET** `/api/buses/`

**Query Parameters:**
- `include_inactive` (optional): Include non-active buses (true/false)

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "bus_id": 1,
      "plate_number": "ABC-1234",
      "status": "Active"
    }
  ]
}
```

---

### 6. Get Buses by Route
**GET** `/api/buses/route/{route_id}`

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "bus_id": 1,
      "plate_number": "ABC-1234",
      "route_id": 1
    }
  ]
}
```


---

### 7. Find Nearest Buses
**GET** `/api/buses/nearest`

**Query Parameters:**
- `latitude` (required): Latitude coordinate
- `longitude` (required): Longitude coordinate
- `route_id` (optional): Filter by route
- `limit` (optional): Max results (default: 5)

**Example:** `/api/buses/nearest?latitude=21.0285&longitude=105.8542&limit=3`

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "bus_id": 1,
      "plate_number": "ABC-1234",
      "distance_meters": 150.5,
      "current_location": {
        "latitude": 21.0285,
        "longitude": 105.8542
      }
    }
  ]
}
```

---

### 8. Get Active Bus Count
**GET** `/api/buses/count/active`

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "count": 25
  }
}
```

---

### 9. Update Bus (Admin Only)
**PUT** `/api/buses/{bus_id}`

**Headers:** Requires authentication + admin privileges

**Request Body:**
```json
{
  "name": "Bus 101 Updated",
  "model": "Mercedes-Benz Sprinter 2024",
  "status": "Maintenance"
}
```

**Response (200):**
```json
{
  "status": "success",
  "message": "Bus updated successfully",
  "data": {
    "bus_id": 1,
    "name": "Bus 101 Updated",
    "status": "Maintenance"
  }
}
```

---

### 10. Update Bus Status (Admin Only)
**PUT** `/api/buses/{bus_id}/status`

**Headers:** Requires authentication + admin privileges

**Request Body:**
```json
{
  "status": "Maintenance"
}
```

**Response (200):**
```json
{
  "status": "success",
  "message": "Bus status updated successfully"
}
```

---

### 11. Update Bus Location
**PUT** `/api/buses/{bus_id}/location`

**Headers:** Requires authentication (drivers or admin)

**Request Body:**
```json
{
  "location": {
    "latitude": 21.0285,
    "longitude": 105.8542
  }
}
```

**Response (200):**
```json
{
  "status": "success",
  "message": "Bus location updated successfully"
}
```

---

### 12. Assign Bus to Route (Admin Only)
**PUT** `/api/buses/{bus_id}/assign-route`

**Headers:** Requires authentication + admin privileges

**Request Body:**
```json
{
  "route_id": 2
}
```

**Response (200):**
```json
{
  "status": "success",
  "message": "Bus assigned to route successfully"
}
```

---

### 13. Check if Bus is On Route
**GET** `/api/buses/{bus_id}/on-route`

**Query Parameters:**
- `tolerance_meters` (optional): Distance tolerance (default: 100)

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "is_on_route": true
  }
}
```

---

### 14. Get Bus Location Details
**GET** `/api/buses/{bus_id}/location-details`

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "bus_id": 1,
    "current_location": {
      "latitude": 21.0285,
      "longitude": 105.8542
    },
    "distance_from_route": 50.5,
    "last_updated": "2025-01-15T14:30:00"
  }
}
```

---

### 15. Delete Bus (Admin Only)
**DELETE** `/api/buses/{bus_id}`

**Headers:** Requires authentication + admin privileges

**Response (200):**
```json
{
  "status": "success",
  "message": "Bus deleted successfully"
}
```

---

## Driver API

Base URL: `/api/drivers`

### 1. Create Driver (Admin Only)
**POST** `/api/drivers/`

**Headers:** Requires authentication + admin privileges

**Request Body:**
```json
{
  "user_id": 5,
  "license_number": "DL-123456789",
  "bus_id": 1
}
```

**Response (201):**
```json
{
  "status": "success",
  "message": "Driver created successfully",
  "data": {
    "id": 1,
    "user_id": 5,
    "license_number": "DL-123456789",
    "bus_id": 1,
    "status": "Active"
  }
}
```

---

### 2. Get Driver by ID
**GET** `/api/drivers/{driver_id}`

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "user_id": 5,
    "license_number": "DL-123456789",
    "bus_id": 1,
    "status": "Active"
  }
}
```

---

### 3. Get Driver by User ID
**GET** `/api/drivers/user/{user_id}`

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "user_id": 5,
    "license_number": "DL-123456789",
    "bus_id": 1,
    "bus_plate": "ABC-1234",
    "route_id": 1,
    "route_name": "Route 1"
  }
}
```

---

### 4. Get Driver by Bus ID
**GET** `/api/drivers/bus/{bus_id}`

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "user_id": 5,
    "username": "john_driver",
    "license_number": "DL-123456789",
    "bus_id": 1
  }
}
```

---

### 5. Get All Active Drivers
**GET** `/api/drivers/active`

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "user_id": 5,
      "username": "john_driver",
      "license_number": "DL-123456789",
      "bus_id": 1,
      "status": "Active"
    }
  ]
}
```

---

### 6. Get All Drivers
**GET** `/api/drivers/`

**Query Parameters:**
- `include_deleted_users` (optional): Include drivers with deleted user accounts (true/false)

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "user_id": 5,
      "license_number": "DL-123456789",
      "status": "Active"
    }
  ]
}
```

---

### 7. Get Drivers on Route
**GET** `/api/drivers/route/{route_id}`

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "user_id": 5,
      "username": "john_driver",
      "bus_id": 1,
      "route_id": 1
    }
  ]
}
```

---

### 8. Check if User is Driver
**GET** `/api/drivers/check/{user_id}`

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "is_driver": true
  }
}
```

---

### 9. Get Driver Count
**GET** `/api/drivers/count`

**Query Parameters:**
- `status` (optional): Filter by status (Active/Inactive/Suspended)

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "count": 15
  }
}
```

---

### 10. Update Driver Status (Admin Only)
**PUT** `/api/drivers/{driver_id}/status`

**Headers:** Requires authentication + admin privileges

**Request Body:**
```json
{
  "status": "Suspended"
}
```

**Response (200):**
```json
{
  "status": "success",
  "message": "Driver status updated successfully"
}
```

---

### 11. Update Driver License (Admin Only)
**PUT** `/api/drivers/{driver_id}/license`

**Headers:** Requires authentication + admin privileges

**Request Body:**
```json
{
  "license_number": "DL-987654321"
}
```

**Response (200):**
```json
{
  "status": "success",
  "message": "Driver license updated successfully"
}
```

---

### 12. Assign Driver to Bus (Admin Only)
**PUT** `/api/drivers/{driver_id}/assign-bus`

**Headers:** Requires authentication + admin privileges

**Request Body:**
```json
{
  "bus_id": 2
}
```

**Response (200):**
```json
{
  "status": "success",
  "message": "Driver assigned to bus successfully"
}
```

---

### 13. Delete Driver (Admin Only)
**DELETE** `/api/drivers/{driver_id}`

**Headers:** Requires authentication + admin privileges

**Response (200):**
```json
{
  "status": "success",
  "message": "Driver deleted successfully"
}
```

---

## Route API

Base URL: `/api/routes`

### 1. Create Route (Admin Only)
**POST** `/api/routes/`

**Headers:** Requires authentication + admin privileges

**Request Body:**
```json
{
  "name": "Route 1 - City Center",
  "coordinates": [
    [21.0285, 105.8542],
    [21.0300, 105.8560],
    [21.0320, 105.8580]
  ]
}
```

**Response (201):**
```json
{
  "status": "success",
  "message": "Route created successfully",
  "data": {
    "id": 1,
    "name": "Route 1 - City Center",
    "updated_at": "2025-01-15T10:00:00"
  }
}
```

---

### 2. Get Route by ID
**GET** `/api/routes/{route_id}`

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "name": "Route 1 - City Center",
    "current_segment": 0,
    "updated_at": "2025-01-15T10:00:00"
  }
}
```

---

### 3. Get Route by Name
**GET** `/api/routes/name/{route_name}`

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "name": "Route 1 - City Center"
  }
}
```

---

### 4. Get All Routes
**GET** `/api/routes/`

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "name": "Route 1 - City Center",
      "stop_count": 10,
      "length_meters": 5000.5
    }
  ]
}
```

---

### 5. Get Route Stops
**GET** `/api/routes/{route_id}/stops`

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "stop_id": 1,
      "name": "Stop 1 - Main Square",
      "sequence": 1,
      "location": {
        "latitude": 21.0285,
        "longitude": 105.8542
      }
    }
  ]
}
```

---

### 6. Get Route Length
**GET** `/api/routes/{route_id}/length`

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "length": 5000.5
  }
}
```

---

### 7. Get Route GeoJSON
**GET** `/api/routes/{route_id}/geojson`

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "type": "LineString",
    "coordinates": [
      [105.8542, 21.0285],
      [105.8560, 21.0300]
    ]
  }
}
```

---

### 8. Find Routes Near Location
**GET** `/api/routes/near`

**Query Parameters:**
- `latitude` (required): Latitude coordinate
- `longitude` (required): Longitude coordinate
- `radius_meters` (optional): Search radius (default: 500, max: 10000)

**Example:** `/api/routes/near?latitude=21.0285&longitude=105.8542&radius_meters=1000`

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "name": "Route 1 - City Center",
      "distance_meters": 150.5
    }
  ]
}
```

---

### 9. Check if Point is On Route
**GET** `/api/routes/{route_id}/check-point`

**Query Parameters:**
- `latitude` (required): Latitude coordinate
- `longitude` (required): Longitude coordinate
- `tolerance_meters` (optional): Distance tolerance (default: 100)

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "is_on_route": true
  }
}
```

---

### 10. Update Route (Admin Only)
**PUT** `/api/routes/{route_id}`

**Headers:** Requires authentication + admin privileges

**Request Body:**
```json
{
  "name": "Route 1 - Updated Name",
  "coordinates": [
    [21.0285, 105.8542],
    [21.0300, 105.8560]
  ]
}
```

**Response (200):**
```json
{
  "status": "success",
  "message": "Route updated successfully",
  "data": {
    "id": 1,
    "name": "Route 1 - Updated Name"
  }
}
```

---

### 11. Update Route Geometry (Admin Only)
**PUT** `/api/routes/{route_id}/geometry`

**Headers:** Requires authentication + admin privileges

**Request Body:**
```json
{
  "coordinates": [
    [21.0285, 105.8542],
    [21.0300, 105.8560],
    [21.0320, 105.8580]
  ]
}
```

**Response (200):**
```json
{
  "status": "success",
  "message": "Route geometry updated successfully"
}
```

---

### 12. Add Stop to Route (Admin Only)
**POST** `/api/routes/{route_id}/stops/{stop_id}`

**Headers:** Requires authentication + admin privileges

**Request Body:**
```json
{
  "sequence": 5
}
```

**Response (200):**
```json
{
  "status": "success",
  "message": "Stop added to route successfully"
}
```

---

### 13. Remove Stop from Route (Admin Only)
**DELETE** `/api/routes/{route_id}/stops/{stop_id}`

**Headers:** Requires authentication + admin privileges

**Response (200):**
```json
{
  "status": "success",
  "message": "Stop removed from route successfully"
}
```

---

### 14. Reorder Route Stops (Admin Only)
**PUT** `/api/routes/{route_id}/stops/reorder`

**Headers:** Requires authentication + admin privileges

**Request Body:**
```json
{
  "stop_sequences": [
    {"stop_id": 1, "sequence": 1},
    {"stop_id": 2, "sequence": 2},
    {"stop_id": 3, "sequence": 3}
  ]
}
```

**Response (200):**
```json
{
  "status": "success",
  "message": "Stops reordered successfully"
}
```

---

### 15. Delete Route (Admin Only)
**DELETE** `/api/routes/{route_id}`

**Headers:** Requires authentication + admin privileges

**Response (200):**
```json
{
  "status": "success",
  "message": "Route deleted successfully"
}
```

---

## Stop API

Base URL: `/api/stops`

### 1. Create Stop (Admin Only)
**POST** `/api/stops/`

**Headers:** Requires authentication + admin privileges

**Request Body:**
```json
{
  "name": "Stop 1 - Main Square",
  "latitude": 21.0285,
  "longitude": 105.8542
}
```

**Response (201):**
```json
{
  "status": "success",
  "message": "Stop created successfully",
  "data": {
    "id": 1,
    "name": "Stop 1 - Main Square",
    "location": {
      "latitude": 21.0285,
      "longitude": 105.8542
    }
  }
}
```

---

### 2. Get Stop by ID
**GET** `/api/stops/{stop_id}`

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "name": "Stop 1 - Main Square",
    "location": {
      "latitude": 21.0285,
      "longitude": 105.8542
    }
  }
}
```

---

### 3. Get All Stops
**GET** `/api/stops/`

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "name": "Stop 1 - Main Square",
      "location": {
        "latitude": 21.0285,
        "longitude": 105.8542
      }
    }
  ]
}
```

---

### 4. Find Nearest Stops
**GET** `/api/stops/nearest`

**Query Parameters:**
- `latitude` (required): Latitude coordinate
- `longitude` (required): Longitude coordinate
- `radius_meters` (optional): Search radius (default: 1000)
- `limit` (optional): Max results (default: 10)

**Example:** `/api/stops/nearest?latitude=21.0285&longitude=105.8542&limit=5`

**Response (200):**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "name": "Stop 1 - Main Square",
      "distance_meters": 50.5,
      "location": {
        "latitude": 21.0285,
        "longitude": 105.8542
      }
    }
  ]
}
```

---

### 5. Update Stop (Admin Only)
**PUT** `/api/stops/{stop_id}`

**Headers:** Requires authentication + admin privileges

**Request Body:**
```json
{
  "name": "Stop 1 - Main Square Updated"
}
```

**Response (200):**
```json
{
  "status": "success",
  "message": "Stop updated successfully",
  "data": {
    "id": 1,
    "name": "Stop 1 - Main Square Updated"
  }
}
```

---

### 6. Delete Stop (Admin Only)
**DELETE** `/api/stops/{stop_id}`

**Headers:** Requires authentication + admin privileges

**Response (200):**
```json
{
  "status": "success",
  "message": "Stop deleted successfully"
}
```

---

## Health Check

### Health Check Endpoint
**GET** `/health`

Check if the API and database are operational.

**Response (200):**
```json
{
  "status": "healthy",
  "database": "connected"
}
```

**Response (503):**
```json
{
  "status": "unhealthy",
  "database": "disconnected",
  "error": "Connection timeout"
}
```

---

## Error Response Format

All error responses follow this format:

**400 Bad Request:**
```json
{
  "status": "fail",
  "message": "Validation error or business logic failure"
}
```

**401 Unauthorized:**
```json
{
  "status": "fail",
  "message": "Authentication required"
}
```

**403 Forbidden:**
```json
{
  "status": "fail",
  "message": "Admin privileges required"
}
```

**404 Not Found:**
```json
{
  "status": "fail",
  "message": "Resource not found"
}
```

**500 Internal Server Error:**
```json
{
  "status": "error",
  "message": "Internal server error: [error details]"
}
```

---

## Testing Notes

### Authentication Flow
1. Register or login to receive authentication cookie
2. Cookie is automatically included in subsequent requests
3. Logout to invalidate the token

### Testing Tools
- **Postman**: Import these endpoints and test systematically
- **cURL**: Use `--cookie-jar` and `--cookie` flags for auth
- **Thunder Client** (VS Code): Good for quick testing

### Example cURL Commands

**Register:**
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test_user","email":"test@example.com","password":"Test123!","name":"Test User","phone":"12345678901"}' \
  -c cookies.txt
```

**Login:**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}' \
  -c cookies.txt
```

**Authenticated Request:**
```bash
curl -X GET http://localhost:5000/api/buses/active \
  -b cookies.txt
```

---

## Summary

- **Total Endpoints**: 66
- **Authentication**: Cookie-based JWT (HTTP-only, secure cookies)
- **Base URL**: `http://localhost:5000`
- **API Prefix**: `/api`

## Key Features

- **Cursor-based Pagination**: Used in user listing for better performance with large datasets
- **Role-based Access Control**: User, Driver, and Admin roles
- **Soft Delete**: Users can be restored after deletion
- **Secure Authentication**: JWT tokens stored in HTTP-only cookies
- **Password Requirements**: Enforced password strength policies

All endpoints follow consistent patterns for request/response formats, error handling, and authentication.

# AIMS Frontend Design Analysis Report

## 1. DESIGN PATTERNS VIOLATIONS & IMPROVEMENTS

### 1.1 Singleton Pattern Issues

**Problem Areas:**
- `axiosInstance` in `config.ts` được tạo như global variable thay vì proper singleton
- Các service objects được export default nhưng không ensure single instance

**Files:** `config.ts`, `index.ts`, all service files

**Current Problems:**
```typescript
// config.ts - Không phải singleton pattern
const axiosInstance = createAxiosInstance(); // Global variable
export { axiosInstance };

// index.ts - Multiple instances có thể được tạo
const apiService = {
    auth: authService,
    products: productService,
    // ...
};
```

**Why Fix:**
- Multiple axios instances có thể được tạo với different configurations
- Memory overhead khi create multiple service instances
- Inconsistent configuration across application

**Solution:**
```typescript
class ApiClient {
    private static instance: ApiClient;
    private axiosInstance: AxiosInstance;
    
    private constructor() {
        this.axiosInstance = this.createAxiosInstance();
    }
    
    public static getInstance(): ApiClient {
        if (!ApiClient.instance) {
            ApiClient.instance = new ApiClient();
        }
        return ApiClient.instance;
    }
}
```

---

### 1.2 Template Method Pattern Missing

**Problem Areas:**
- All hooks có similar structure nhưng không dùng template method
- Context providers có duplicate initialization logic
- Service error handling có repetitive patterns

**Files:** All hook files (`useAuth.ts`, `useCart.ts`, etc.), Context files

**Current Problems:**
```typescript
// useAuth.ts, useCart.ts, useOrder.ts - Duplicate structure
export const useAuth = () => {
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    // Repetitive error handling logic in every method
    const login = useCallback(async (credentials) => {
        setLoading(true);
        setError(null);
        try {
            // API call logic
        } catch (err: any) {
            setLoading(false);
            setError(err.response?.data?.message || 'An error occurred...');
            throw err;
        }
    }, []);
};
```

**Why Fix:**
- Code duplication across all hooks
- Inconsistent error handling
- Hard to maintain when changing common behavior

**Solution:**
```typescript
abstract class BaseHook<T> {
    protected loading = useState<boolean>(false);
    protected error = useState<string | null>(null);
    
    protected async executeRequest<R>(
        apiCall: () => Promise<R>,
        successCallback?: (data: R) => void,
        errorMessage?: string
    ): Promise<R> {
        // Template method implementation
        this.setLoading(true);
        this.setError(null);
        try {
            const result = await apiCall();
            if (successCallback) successCallback(result);
            return result;
        } catch (err: any) {
            this.handleError(err, errorMessage);
            throw err;
        } finally {
            this.setLoading(false);
        }
    }
    
    protected abstract handleError(err: any, message?: string): void;
}
```

---

### 1.3 Strategy Pattern Missing

**Problem Areas:**
- Error handling strategies hardcoded in hooks
- Formatting logic in `formatters.ts` không dùng strategy pattern
- Route protection logic scattered

**Files:** `formatters.ts`, all hook files, `protectedRoute.tsx`

**Current Problems:**
```typescript
// formatters.ts - Hardcoded formatting strategies
export const formatPrice = (price: number, currency = 'VND'): string => {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency,
    }).format(price);
};

export const formatCurrency = (amount: number, currency: string = 'VND'): string => {
    if (currency === 'VND') {
        // Hardcoded VND logic
    }
    // Hardcoded other currency logic
};
```

**Why Fix:**
- Violates OCP when adding new currencies/formats
- Hard to test different formatting strategies
- Duplicate logic for similar formatting needs

**Solution:**
```typescript
interface FormattingStrategy {
    format(value: number): string;
}

class VNDFormattingStrategy implements FormattingStrategy {
    format(value: number): string {
        return new Intl.NumberFormat('vi-VN', {
            style: 'currency',
            currency: 'VND',
        }).format(value);
    }
}

class USDFormattingStrategy implements FormattingStrategy {
    format(value: number): string {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
        }).format(value);
    }
}
```

---

### 1.4 Factory Method Pattern Missing

**Problem Areas:**
- Service creation không có factory pattern
- Hook creation scattered across contexts
- Route creation hardcoded

**Files:** `index.ts`, Context files, route files

**Current Problems:**
```typescript
// index.ts - Direct service creation
const apiService = {
    auth: authService,
    products: productService,
    cart: cartService,
    orders: orderService,
    payments: paymentService,
};

// Contexts - Direct hook creation
export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const auth = useAuth(); // Direct instantiation
    return <AuthContext.Provider value={auth}>{children}</AuthContext.Provider>;
};
```

**Why Fix:**
- Violates OCP when adding new services
- Hard to mock services for testing
- No centralized service configuration

**Solution:**
```typescript
interface ServiceFactory {
    createAuthService(): IAuthService;
    createProductService(): IProductService;
    createCartService(): ICartService;
}

class ApiServiceFactory implements ServiceFactory {
    createAuthService(): IAuthService {
        return new AuthService(ApiClient.getInstance());
    }
    
    createProductService(): IProductService {
        return new ProductService(ApiClient.getInstance());
    }
}
```

---

### 1.5 Adapter Pattern Missing

**Problem Areas:**
- No adapter cho different API response formats
- Type conversion logic scattered
- External library integration không có adapter

**Files:** Service files, utility files

**Current Problems:**
```typescript
// Services directly work with axios responses
const response = await authService.login(credentials);
setUser(response.data.data ?? null); // Direct data manipulation
```

**Why Fix:**
- Tight coupling với axios response format
- Hard to change API client library
- Inconsistent data transformation

**Solution:**
```typescript
interface ApiAdapter<T> {
    adapt(response: any): T;
}

class AuthResponseAdapter implements ApiAdapter<User> {
    adapt(response: AxiosResponse): User {
        // Transform axios response to User type
        return {
            id: response.data.data.id,
            username: response.data.data.username,
            // ... other transformations
        };
    }
}
```

---

### 1.6 Observer Pattern Missing

**Problem Areas:**
- State changes không có proper notification system
- Error handling không có centralized observation
- Loading states không có global observation

**Files:** All hooks and contexts

**Current Problems:**
```typescript
// No centralized state observation
// Each component manages its own state without notification
```

**Why Fix:**
- Components không biết về state changes từ other components
- No centralized error/loading state management
- Hard to implement global features like loading indicators

**Solution:**
```typescript
interface Observer {
    update(event: string, data: any): void;
}

class StateManager {
    private observers: Map<string, Observer[]> = new Map();
    
    subscribe(event: string, observer: Observer): void {
        if (!this.observers.has(event)) {
            this.observers.set(event, []);
        }
        this.observers.get(event)!.push(observer);
    }
    
    notify(event: string, data: any): void {
        const observers = this.observers.get(event) || [];
        observers.forEach(observer => observer.update(event, data));
    }
}
```

---

## 2. SOLID PRINCIPLES VIOLATIONS

### 2.1 Single Responsibility Principle (SRP) Violations

**Problem Areas:**

#### formatters.ts
**Issues:** Handles multiple formatting concerns
```typescript
// formatters.ts - Multiple responsibilities
export const formatPrice = (price: number, currency = 'VND'): string => { ... }
export const formatDate = (dateString: string, ...): string => { ... }
export const formatFileSize = (bytes: number, decimals = 2): string => { ... }
export const formatPhoneNumber = (phone: string): string => { ... }
export const truncateText = (text: string, maxLength: number, ...): string => { ... }
export const formatCurrency = (amount: number, currency: string = 'VND'): string => { ... }
```

**Should be separated:**
- PriceFormatter class
- DateFormatter class  
- FileFormatter class
- TextFormatter class

#### config.ts
**Issues:** Handles configuration, axios setup, and interceptors
```typescript
// config.ts - Multiple responsibilities
const getApiUrl = (): string => { ... } // Configuration
const createAxiosInstance = (): AxiosInstance => { ... } // Instance creation  
// + Request interceptor logic
// + Response interceptor logic
```

#### All Hook files
**Issues:** Each hook handles state management, API calls, error handling, and data transformation

---

### 2.2 Open/Closed Principle (OCP) Violations

**Problem Areas:**

#### formatters.ts
```typescript
// Adding new currency requires modifying existing code
export const formatCurrency = (amount: number, currency: string = 'VND'): string => {
    if (currency === 'VND') {
        // VND logic
    }
    // Default logic - need to modify this when adding new currencies
};
```

#### Route Configuration
```typescript
// Adding new routes requires modifying route files
const clientRoutes = [
    // Need to modify this array when adding new routes
];
```

#### Service Objects
```typescript
// Adding new services requires modifying index.ts
const apiService = {
    auth: authService,
    products: productService,
    // Need to add new services here
};
```

---

### 2.3 Liskov Substitution Principle (LSP) Violations

**Problem Areas:**

#### Inconsistent Hook Interfaces
- Different hooks return different shapes
- Some hooks have methods that others don't
- Error handling behavior varies between hooks

---

### 2.4 Interface Segregation Principle (ISP) Violations

**Problem Areas:**

#### Large Context Interfaces
```typescript
// AuthContextType - Too many methods
interface AuthContextType {
    user: User | null;
    loading: boolean;
    error: string | null;
    register: (userData: RegisterUserDto) => Promise<any>;
    login: (credentials: LoginCredentials) => Promise<any>;
    logout: () => Promise<any>;
    forgotPassword: (email: string) => Promise<any>;
    resetPassword: (token: string, newPassword: string) => Promise<any>;
    getProfile: () => Promise<any>;
    updateProfile: (userData: Partial<User>) => Promise<any>;
    changePassword: (data: ChangePasswordDto) => Promise<any>;
    getAllUsers: () => Promise<any>; // Admin only
    blockUser: (userId: string) => Promise<any>; // Admin only
    setUserRoles: (userId: string, roles: string[]) => Promise<any>; // Admin only
}
```

**Should be segregated:**
- IUserAuthContext (login, logout, getProfile)
- IUserManagementContext (updateProfile, changePassword)
- IAdminContext (getAllUsers, blockUser, setUserRoles)

---

### 2.5 Dependency Inversion Principle (DIP) Violations

**Problem Areas:**

#### Direct Service Dependencies
```typescript
// Hooks depend on concrete service implementations
import authService from '@services/authService';

export const useAuth = () => {
    // Direct dependency on concrete authService
    const response = await authService.login(credentials);
};
```

#### Hard-coded Axios Instance
```typescript
// Services depend on concrete axios instance
import { axiosInstance } from '../config';

const authService = {
    login: (credentials: LoginCredentials) => 
        axiosInstance.post<ApiResponse>('/auth/login', credentials),
};
```

---

## 3. COUPLING & COHESION ISSUES

### 3.1 Tight Coupling Issues

#### Service-Hook Coupling
```typescript
// useAuth.ts tightly coupled to authService
import authService from '@services/authService';
// Direct import creates tight coupling
```

#### Context-Hook Coupling
```typescript
// AuthContext tightly coupled to useAuth
export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const auth = useAuth(); // Direct coupling
    return <AuthContext.Provider value={auth}>{children}</AuthContext.Provider>;
};
```

#### Configuration Coupling
```typescript
// Hard-coded configuration throughout files
const token = localStorage.getItem('auth'); // Direct localStorage coupling
```

### 3.2 Low Cohesion Issues

#### formatters.ts Mixed Concerns
- Price formatting
- Date formatting  
- File size formatting
- Phone number formatting
- Text truncation
- Currency formatting

#### config.ts Mixed Responsibilities
- Environment variable loading
- Axios instance creation
- Request interceptors
- Response interceptors
- Authentication logic

#### Hook Files Mixed Concerns
Each hook handles:
- State management
- API communication  
- Error handling
- Data transformation
- Loading states

---

## 4. SPECIFIC REFACTORING RECOMMENDATIONS

### High Priority Issues:

1. **Implement Singleton Pattern for ApiClient**
   - Ensure single axios instance across application
   - Centralized configuration management

2. **Extract Template Method for Hooks**
   - Common async operation pattern
   - Consistent error handling
   - Standardized loading states

3. **Implement Strategy Pattern for Formatters**
   - Separate formatting strategies
   - Easy to extend with new formats
   - Better testability

4. **Apply SRP to Large Files**
   - Break down formatters.ts
   - Separate config.ts concerns
   - Split large context interfaces

### Medium Priority Issues:

1. **Implement Factory Pattern for Services**
   - Centralized service creation
   - Better dependency management
   - Easier testing

2. **Add Adapter Pattern for API Integration**
   - Decouple from axios response format
   - Easier to change API clients
   - Consistent data transformation

3. **Apply DIP with Dependency Injection**
   - Inject services into hooks
   - Use interfaces instead of concrete classes
   - Better testability

### Low Priority Issues:

1. **Implement Observer Pattern for Global State**
   - Centralized state notifications
   - Better component communication
   - Global loading/error states

2. **Improve ISP with Interface Segregation**
   - Split large interfaces
   - Role-based context interfaces
   - More focused components

---

## 5. CONCLUSION

The current frontend codebase has several design issues that impact:

- **Maintainability**: Tight coupling and low cohesion make changes difficult
- **Testability**: Direct dependencies and mixed concerns hinder unit testing
- **Scalability**: Violating OCP makes adding features expensive
- **Code Quality**: SRP violations and duplicate code reduce readability

Addressing these issues will significantly improve:
- Developer productivity
- Code maintainability
- Application reliability
- Testing capabilities

The recommended refactoring should be done incrementally, starting with high-priority items that provide the most immediate benefit.
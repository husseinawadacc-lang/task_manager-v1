# Task Manager API — System Diagrams

This document contains all system diagrams.

---

# 1. System Architecture

```mermaid
flowchart TD

Client[Client / Browser]

API[FastAPI Routers]

Deps[Dependencies]

Services[Service Layer]

Storage[Storage Layer]

DB[(Database)]

Redis[(Redis Blacklist)]

Client --> API
API --> Deps
Deps --> Services
Services --> Storage
Storage --> DB
Services --> Redis


#2. Request Lifecycle 


sequenceDiagram

participant Client
participant Router
participant Dependency
participant Service
participant Storage
participant DB

Client->>Router: HTTP Request
Router->>Dependency: resolve dependencies
Dependency->>Service: call service
Service->>Storage: perform operation
Storage->>DB: query/insert/update
DB-->>Storage: result
Storage-->>Service: domain object
Service-->>Router: response data
Router-->>Client: HTTP Response

# 3. Authentication

sequenceDiagram

participant Client
participant API
participant AuthService
participant TokenService
participant Storage
participant DB

Client->>API: POST /auth/login
API->>AuthService: login(email,password)

AuthService->>Storage: get_user_by_email
Storage->>DB: SELECT user

AuthService->>AuthService: verify_password

AuthService->>TokenService: issue_tokens

TokenService->>Storage: store refresh token hash
Storage->>DB: INSERT refresh_token

TokenService-->>API: access + refresh tokens

API-->>Client: tokens

# 4.Access token validation

sequenceDiagram

participant Client
participant API
participant AuthDep
participant TokenService
participant Redis
participant AuthService

Client->>API: GET /tasks
API->>AuthDep: get_current_user

AuthDep->>TokenService: validate_access_token

TokenService->>Redis: check blacklist

Redis-->>TokenService: valid

TokenService-->>AuthDep: user_id

AuthDep->>AuthService: get_user_by_id

AuthService-->>API: user

API-->>Client: response

# 5. Refresh Token Rotation

sequenceDiagram

participant Client
participant API
participant TokenService
participant Storage
participant DB

Client->>API: POST /auth/refresh

API->>TokenService: refresh_tokens(token)

TokenService->>TokenService: hash_token

TokenService->>Storage: get_refresh_token

Storage->>DB: SELECT refresh_token

TokenService->>TokenService: check used/revoked

TokenService->>Storage: mark_refresh_token_used

TokenService->>Storage: create new refresh token

Storage->>DB: INSERT new token

TokenService-->>API: new access + refresh tokens

API-->>Client: tokens

# 6 . Refresh Token Reuse Attack

flowchart TD

Attacker[Reuse refresh token]

Check[Check token.used]

Family[Revoke token family]

AttackBlocked[Reject request]

Attacker --> Check
Check -->|true| Family
Family --> AttackBlocked

# 7 . Logout Flow

sequenceDiagram

participant Client
participant API
participant JWT
participant Redis
participant TokenService
participant Storage
participant DB

Client->>API: POST /auth/logout

API->>JWT: decode access token

JWT-->>API: jti + exp

API->>Redis: blacklist_token(jti)

API->>TokenService: revoke_token_family

TokenService->>Storage: revoke tokens

Storage->>DB: UPDATE refresh_tokens revoked=true

API-->>Client: 204

# 8 . Task Ownership Security

flowchart TD

UserRequest[User requests task]

LoadTask[Load task from DB]

CheckOwner[Check owner_id]

ReturnTask[Return task]

NotFound[Return 404]

UserRequest --> LoadTask
LoadTask --> CheckOwner

CheckOwner -->|owner match| ReturnTask
CheckOwner -->|not owner| NotFound

# 9. Pagination Flow 

flowchart TD

ClientRequest[GET /tasks]

ValidateLimit[Validate limit]

ValidateOffset[Validate offset]

QueryTasks[Query tasks]

CountTasks[Count tasks]

ReturnResponse[Return items + total]

ClientRequest --> ValidateLimit
ValidateLimit --> ValidateOffset
ValidateOffset --> QueryTasks
QueryTasks --> CountTasks
CountTasks --> ReturnResponse

# 10 . Token Lifecycle

flowchart LR

Login --> IssueAccess
IssueAccess --> IssueRefresh
IssueRefresh --> StoreHash

StoreHash --> UseAccess
UseAccess --> ValidateJWT

ValidateJWT --> RefreshFlow

RefreshFlow --> RotateToken

RotateToken --> NewTokens

NewTokens --> Logout

Logout --> BlacklistJWT
Logout --> RevokeRefresh

# 11 . Security Layers

flowchart TD

Auth[Authentication]

RBAC[Authorization]

Ownership[Ownership check]

Validation[Input validation]

RateLimit[Rate limiting]

Blacklist[JWT blacklist]

Auth --> RBAC
RBAC --> Ownership
Ownership --> Validation
Validation --> RateLimit
RateLimit --> Blacklist




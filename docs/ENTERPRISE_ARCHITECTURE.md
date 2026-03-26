# Enterprise Architecture Diagram

This diagram describes the complete architecture of the system.

```mermaid
flowchart TB

%% =========================
%% CLIENT LAYER
%% =========================

Client[Client<br>Browser / Mobile / Postman]

%% =========================
%% API LAYER
%% =========================

subgraph API_LAYER["API Layer (FastAPI)"]

RouterAuth[Auth Router]
RouterTasks[Tasks Router]

end

%% =========================
%% DEPENDENCY LAYER
%% =========================

subgraph DEPENDENCIES["Dependency Layer"]

AuthDep[get_current_user]
PermissionDep[require_permission]
ServiceDep[get_*_service]

end

%% =========================
%% SERVICE LAYER
%% =========================

subgraph SERVICES["Service Layer"]

AuthService
TaskService
TokenService
AuthorizationService

end

%% =========================
%% STORAGE LAYER
%% =========================

subgraph STORAGE["Storage Layer"]

BaseStorage
SQLAlchemyStorage
MemoryStorage

end

%% =========================
%% DATABASE
%% =========================

subgraph DATABASE["Database"]

Users[(Users Table)]
Tasks[(Tasks Table)]
RefreshTokens[(Refresh Tokens)]

end

%% =========================
%% CACHE
%% =========================

subgraph CACHE["Security Cache"]

Redis[(JWT Blacklist)]

end

%% =========================
%% DOMAIN
%% =========================

subgraph DOMAIN["Domain Models"]

User
Task

end


%% =========================
%% FLOWS
%% =========================

Client --> RouterAuth
Client --> RouterTasks

RouterAuth --> AuthDep
RouterTasks --> AuthDep

RouterTasks --> PermissionDep

AuthDep --> AuthService
PermissionDep --> AuthorizationService

RouterTasks --> ServiceDep

ServiceDep --> TaskService
ServiceDep --> TokenService

AuthService --> BaseStorage
TaskService --> BaseStorage
TokenService --> BaseStorage

BaseStorage --> SQLAlchemyStorage
BaseStorage --> MemoryStorage

SQLAlchemyStorage --> Users
SQLAlchemyStorage --> Tasks
SQLAlchemyStorage --> RefreshTokens

TokenService --> Redis

AuthService --> User
TaskService --> Task

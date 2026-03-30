
# AI Features

## Feature : AI Task Assistant

### Goals
convert raw user input into a structured task.

### Input 
- text :str

### Output 
- title: str
- description: str
- priority: str

### Flow

 ```mermaid
flowchart LR
    U[User] --> API[API]
    API --> AI[AI Service]
    AI --> RES[Response]
    RES --> DB[Database]
```

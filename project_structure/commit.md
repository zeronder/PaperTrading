# PaperTrading Project Flow

This document shows the main flow of the current PaperTrading project in a simple way.

## 1. Main Flow

```mermaid
flowchart TD

    A([Start])
    B[Setup Logging]
    C[Start Workers]
    D[Client Login]
    E[Create WebSocket]
    F[Connect WebSocket]
    G[Subscribe Stocks]
    H[Receive Tick]
    I[Create Tick Object]
    J[Dispatch Tick]

    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    H --> I
    I --> J

    J --> K[Strategy Queue]
    J --> L[Database Queue]

    K --> M[Strategy Worker]
    L --> N[Database Worker]

    M --> O[Future Strategy]
    N --> P[(SQLite Database)]

    classDef start fill:#2E7D32,color:#fff,stroke:#1B5E20,stroke-width:2px;
    classDef websocket fill:#1976D2,color:#fff,stroke:#0D47A1,stroke-width:2px;
    classDef tick fill:#8E24AA,color:#fff,stroke:#4A148C,stroke-width:2px;
    classDef queue fill:#F57C00,color:#fff,stroke:#E65100,stroke-width:2px;
    classDef worker fill:#00897B,color:#fff,stroke:#004D40,stroke-width:2px;
    classDef database fill:#455A64,color:#fff,stroke:#263238,stroke-width:2px;

    class A start;
    class B,C,D,E,F,G websocket;
    class H,I,J tick;
    class K,L queue;
    class M,N,O worker;
    class P database;
```

## 2. WebSocket Flow

```mermaid
flowchart TD

    A[Client Login]
    B[Create WebSocket]
    C[Connect]
    D[on_open]
    E[Subscribe Tokens]
    F[on_data]
    G[Tick]

    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G

    classDef blue fill:#1976D2,color:#fff,stroke:#0D47A1;
    classDef purple fill:#8E24AA,color:#fff,stroke:#4A148C;

    class A,B,C,D,E blue;
    class F,G purple;
```

## 3. Tick to Queue Flow

```mermaid
flowchart LR

    A[WebSocket Message]
    B[Tick Object]
    C[dispatch_tick]

    D[Strategy Queue]
    E[Database Queue]

    F[Strategy Worker]
    G[Database Worker]

    A --> B
    B --> C

    C --> D
    C --> E

    D --> F
    E --> G

    classDef tick fill:#8E24AA,color:#fff;
    classDef queue fill:#F57C00,color:#fff;
    classDef worker fill:#00897B,color:#fff;

    class A,B,C tick;
    class D,E queue;
    class F,G worker;
```

## 4. Database Flow

```mermaid
flowchart TD

    A[Database Queue]
    B[Database Worker]
    C[Collect 10 Ticks]
    D[Insert Ticks]
    E[(papertrading.db)]
    F[(ticks table)]

    A --> B
    B --> C
    C --> D
    D --> E
    E --> F

    classDef queue fill:#F57C00,color:#fff;
    classDef worker fill:#00897B,color:#fff;
    classDef database fill:#455A64,color:#fff;

    class A queue;
    class B,C,D worker;
    class E,F database;
```

## 5. Strategy Flow — Current Skeleton

```mermaid
flowchart TD

    A[Strategy Queue]
    B[Strategy Worker]
    C[Receive Tick]
    D[Strategy Processing]
    E[Signal]
    F[Paper Order]

    A --> B
    B --> C
    C --> D
    D --> E
    E --> F

    E -. planned .-> F

    classDef queue fill:#F57C00,color:#fff;
    classDef worker fill:#00897B,color:#fff;
    classDef planned fill:#78909C,color:#fff,stroke-dasharray:5 5;

    class A queue;
    class B,C,D worker;
    class E,F planned;
```

## 6. Project Modules

```mermaid
flowchart LR

    A[main.py]
    B[client.py]
    C[tick.py]
    D[database.py]
    E[logger.py]
    F[helper/login.py]
    G[settings/config.py]
    H[settings/default.py]

    A --> B
    A --> C
    A --> D
    A --> E

    B --> F
    B --> G

    F --> G

    A --> H

    classDef main fill:#1976D2,color:#fff;
    classDef module fill:#8E24AA,color:#fff;
    classDef setting fill:#6A1B9A,color:#fff;

    class A main;
    class B,C,D,E,F module;
    class G,H setting;
```

## 7. Current Project Status

```mermaid
flowchart TD

    A[WebSocket]
    B[Tick]
    C[Queues]
    D[Database]
    E[Logging]

    F[Strategy]
    G[Order Engine]
    H[Risk Manager]
    I[Position]
    J[P&L]

    A --> B
    B --> C
    C --> D

    C -.-> F
    F -.-> G
    G -.-> H
    H -.-> I
    I -.-> J

    classDef done fill:#2E7D32,color:#fff;
    classDef planned fill:#78909C,color:#fff,stroke-dasharray:5 5;

    class A,B,C,D,E done;
    class F,G,H,I,J planned;
```

## 8. Simple Summary

```text
SmartAPI
   ↓
WebSocket
   ↓
Tick
   ↓
dispatch_tick()
   ├── Strategy Queue
   │       ↓
   │   Strategy Worker
   │
   └── Database Queue
           ↓
       Database Worker
           ↓
        SQLite
```

The current uploaded project has the WebSocket, Tick, queue, database and logging parts. The actual strategy, order, risk, position and P&L logic is still planned/skeleton code.

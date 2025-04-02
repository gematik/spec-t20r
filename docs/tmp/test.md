' Test

'''mermaid
graph LR
    subgraph Kubernetes Cluster
        ZETA_GW[ZETA Gateway / Proxy]
        IDM[Identity & Access Management (IDM)]
        SR[Service Registry / Discovery]
        LOG[Logging Aggregator]
        MON[Monitoring System]
        CERT[Certificate Management]
        subgraph Backend Services Namespace
            SVC_A[Backend Service A (z.B. FHIR)]
            SVC_B[Backend Service B (Fachanwendung)]
        end
    end

    Client[ZETA Client (Extern)] -- ZETA (TLS 1.3 + mTLS) --> ZETA_GW
    ZETA_GW -- Validierte Anfrage --> SR
    SR -- Service Location --> ZETA_GW
    ZETA_GW -- Routed Request (mTLS intern) --> SVC_A
    ZETA_GW -- Routed Request (mTLS intern) --> SVC_B
    ZETA_GW -- Authentifizierung / Token Validierung --> IDM
    SVC_A --> LOG
    SVC_B --> LOG
    ZETA_GW --> LOG
    IDM --> LOG
    SVC_A --> MON
    SVC_B --> MON
    ZETA_GW --> MON
    IDM --> MON
    CERT -- Zertifikate --> ZETA_GW
    CERT -- Zertifikate --> SVC_A
    CERT -- Zertifikate --> SVC_B
'''
@startuml
title Flujo de envío de mensaje con control de tokens

actor Usuario
participant "ChatView" as View
participant "AgentService" as Agent
participant "QuotaService" as Quota
participant "TenantQuotaModel" as TenantQuota
participant "TokenLedgerModel" as Ledger
database "Base de Datos" as DB

== Inicialización ==
Usuario -> View: Envía mensaje a través de API
activate View
View -> View: Valida datos de entrada
View -> Agent: Crea servicio para el agente seleccionado
activate Agent

== Validación de Cuota ==
View -> Quota: Solicita validación de cuota de tokens
activate Quota
Quota -> TenantQuota: Consulta información de cuota del tenant
activate TenantQuota
TenantQuota --> Quota: Devuelve plan y consumo actual

alt Tenant sin plan asignado
    Quota --> View: Notifica que no hay plan asignado
    View --> Usuario: Muestra error 403 (No hay plan asignado)
else Tenant con plan excedido
    Quota -> TenantQuota: Verifica si ya excedió su límite
    TenantQuota --> Quota: Confirma que está bloqueado
    Quota --> View: Envía mensaje de límite excedido
    View --> Usuario: Muestra error (Límite de tokens excedido)
else Tenant con tokens disponibles
    Quota -> TenantQuota: Verifica disponibilidad de tokens
    TenantQuota --> Quota: Confirma disponibilidad
    
    == Procesamiento del Mensaje ==
    Quota -> Agent: Solicita procesamiento del mensaje
    Agent -> Agent: Procesa mensaje con modelo de IA
    Agent --> Quota: Devuelve respuesta generada
    
    == Cálculo y Registro de Tokens ==
    Quota -> Agent: Solicita métricas de consumo
    Agent --> Quota: Informa tokens consumidos
    
    Quota -> TenantQuota: Actualiza contador de tokens
    TenantQuota -> DB: Guarda nuevo estado
    
    Quota -> Ledger: Registra transacción de consumo
    activate Ledger
    Ledger -> DB: Almacena registro de auditoría
    deactivate Ledger
    
    alt Se excedió el límite durante este request
        Quota -> TenantQuota: Comprueba si se superó el límite
        TenantQuota --> Quota: Confirma límite superado
        
        alt Variante A: Permitir esta respuesta final
            Quota -> TenantQuota: Marca cuenta como excedida para futuras peticiones
            TenantQuota -> DB: Guarda estado bloqueado
            Quota --> View: Entrega respuesta normal (por esta vez)
        else Variante B: Bloquear incluso esta respuesta
            Quota -> TenantQuota: Marca cuenta como excedida inmediatamente
            TenantQuota -> DB: Guarda estado bloqueado
            Quota --> View: Notifica límite excedido (sin entregar respuesta)
        end
    else Tokens aún suficientes
        Quota --> View: Entrega respuesta normal
    end
    
    View -> View: Guarda conversación en historial
    View --> Usuario: Muestra respuesta del agente
end

deactivate TenantQuota
deactivate Quota
deactivate Agent
deactivate View

@enduml
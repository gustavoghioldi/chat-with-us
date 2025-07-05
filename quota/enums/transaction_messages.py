from enum import Enum

class SystemMessages(Enum):
    PLAN_EXCEEDED = "Excediste el limite de tokens."
    NO_QUOTA_ASSIGNED = "Este tenant no tiene una cuota de tokens asignada."

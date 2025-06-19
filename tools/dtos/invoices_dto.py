from typing import List

from pydantic import BaseModel, Field


class DetalleProducto(BaseModel):
    nombre: str = Field(..., description="Nombre del producto")
    cantidad: int = Field(..., description="Cantidad del producto")
    precio_unitario: float = Field(..., description="Precio unitario del producto")
    subtotal: float = Field(
        ..., description="Subtotal del producto (cantidad * precio unitario)"
    )
    impuesto: float = Field(
        0.0,
        description="Impuesto (fiscal o iva) aplicado al producto, por defecto es 0",
    )
    descuento: float = Field(
        0.0, description="Descuento (desct) aplicado al producto, por defecto es 0"
    )


class FacturaDTO(BaseModel):
    factura_de: str = Field(..., description="Persona que emitio la factura")
    direccion_del_emisor: str = Field(
        ...,
        description="Dirección del emisor de la factura",
    )
    factura_a: str = Field(
        ...,
        description="Persona a quien va dirigida la factura",
    )
    numero_de_factura: str = Field(..., description="numero de factura")
    fecha: str = Field(..., description="Fecha de emisión de la factura")
    fecha_de_vencimiento: str = Field(
        ...,
        description="Fecha de vencimiento de la factura",
    )
    detalle_de_productos: List[DetalleProducto] = Field(
        ...,
        description="Lista de productos detallados en la factura",
    )
    subtotal: float = Field(..., description="Subtotal de la factura")
    iva: float = Field(..., description="IVA aplicado a la factura")
    total: float = Field(..., description="Total de la factura")
    descuento: float = Field(
        0.0, description="Descuento aplicado a la factura, por defecto es 0"
    )
    costo_de_envio: float = Field(
        0.0, description="Costo de envío aplicado a la factura, por defecto es 0"
    )
    notas: str = Field(
        "",
        description="Notas adicionales sobre la factura, por defecto es una cadena vacía",
    )
    instrucciones_de_pago: str = Field(
        "",
        description="Instrucciones de pago para la factura, por defecto es una cadena vacía",
    )

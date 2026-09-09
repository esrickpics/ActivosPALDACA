"""Etiquetas QR vinculadas a activos ya registrados (alta manual)."""

from __future__ import annotations

from django.core.exceptions import ValidationError
from django.utils import timezone

from activos.models import Activo, EtiquetaQR


def crear_etiqueta_vinculada_para_activo(
    activo: Activo,
    *,
    creada_por=None,
) -> tuple[EtiquetaQR, bool]:
    """Crea (o reutiliza) la etiqueta vigente de un activo existente.

    Devuelve ``(etiqueta, creada)``. Si ya hay una vinculada, la devuelve sin
    duplicar — útil para reimprimir tras un alta manual.
    """
    existente = (
        EtiquetaQR.objects.filter(
            activo=activo,
            estado=EtiquetaQR.EstadoEtiqueta.VINCULADA,
        )
        .order_by("-fecha_vinculacion")
        .first()
    )
    if existente:
        return existente, False

    ahora = timezone.now()
    misma_codigo = (
        EtiquetaQR.objects.filter(codigo_reservado=activo.codigo_inventario)
        .order_by("-fecha_creacion")
        .first()
    )
    if misma_codigo is not None:
        if misma_codigo.estado == EtiquetaQR.EstadoEtiqueta.ANULADA and (
            misma_codigo.activo_id is None or misma_codigo.activo_id == activo.pk
        ):
            misma_codigo.activo = activo
            misma_codigo.estado = EtiquetaQR.EstadoEtiqueta.VINCULADA
            misma_codigo.fecha_vinculacion = ahora
            misma_codigo.save(
                update_fields=["activo", "estado", "fecha_vinculacion"]
            )
            return misma_codigo, True
        raise ValidationError(
            f"El código {activo.codigo_inventario} ya está usado por otra etiqueta QR."
        )

    etiqueta = EtiquetaQR(
        codigo_reservado=activo.codigo_inventario,
        subcategoria=activo.subcategoria,
        activo=activo,
        estado=EtiquetaQR.EstadoEtiqueta.VINCULADA,
        fecha_vinculacion=ahora,
        creada_por=creada_por,
        token=EtiquetaQR.generar_token(),
    )
    etiqueta.save()
    return etiqueta, True


def eliminar_etiqueta_sin_datos(etiqueta: EtiquetaQR) -> str:
    """Borra de verdad una etiqueta pendiente sin datos, o una anulada.

    Libera el ``codigo_reservado`` para que pueda volver a usarse.
    """
    if not etiqueta.puede_eliminarse:
        raise ValidationError(
            "Solo se pueden eliminar etiquetas pendientes sin datos "
            "o etiquetas ya anuladas."
        )
    codigo = etiqueta.codigo_reservado
    etiqueta.delete()
    return codigo

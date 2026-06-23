package com.campito.backend.controller;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.campito.backend.dto.CompraCreditoBusquedaDTO;
import com.campito.backend.dto.CompraCreditoDTOResponse;
import com.campito.backend.dto.PaginatedResponse;
import com.campito.backend.dto.TransaccionBusquedaDTO;
import com.campito.backend.dto.TransaccionDTOResponse;
import com.campito.backend.service.CompraCreditoService;
import com.campito.backend.service.SecurityService;
import com.campito.backend.service.TransaccionService;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotNull;
import lombok.RequiredArgsConstructor;

/**
 * Controlador interno para el microservicio de IA (agente).
 *
 * Estos endpoints NO realizan validación de JWT ni de permisos de workspace
 * porque el agente que los consume ya autenticó al usuario contra el backend
 * y solo es accesible desde la red interna de Docker.
 *
 * Hacen exactamente lo mismo que los endpoints públicos de TransaccionController
 * y ComprasCreditoController, pero sin la capa de seguridad.
 */
@RestController
@RequestMapping("/api/internal")
@Tag(name = "Internal", description = "Endpoints internos para el microservicio de IA (sin autenticación JWT)")
@RequiredArgsConstructor
public class InternalController {

    private final TransaccionService transaccionService;
    private final CompraCreditoService comprasCreditoService;
    private final SecurityService securityService;

    @Operation(summary = "Buscar transacciones (interno)",
               description = "Igual que POST /api/transaccion/buscar pero sin validación JWT. "
                           + "Solo accesible desde la red interna de Docker.")
    @PostMapping("/transaccion/buscar")
    public ResponseEntity<PaginatedResponse<TransaccionDTOResponse>> buscarTransaccion(
            @Valid
            @NotNull(message = "Los criterios de búsqueda son obligatorios")
            @RequestBody TransaccionBusquedaDTO datosBusqueda) {

        // Validar acceso al espacio de trabajo
        //securityService.validateWorkspaceAccess(datosBusqueda.idEspacioTrabajo());
        PaginatedResponse<TransaccionDTOResponse> transacciones =
                transaccionService.buscarTransaccion(datosBusqueda);
        return new ResponseEntity<>(transacciones, HttpStatus.OK);
    }

    @Operation(summary = "Buscar compras a crédito (interno)",
               description = "Igual que POST /api/comprascredito/buscar pero sin validación JWT. "
                           + "Solo accesible desde la red interna de Docker.")
    @PostMapping("/comprascredito/buscar")
    public ResponseEntity<PaginatedResponse<CompraCreditoDTOResponse>> buscarComprasCredito(
            @Valid
            @NotNull(message = "Los criterios de búsqueda son obligatorios")
            @RequestBody CompraCreditoBusquedaDTO datosBusqueda) {

        //securityService.validateWorkspaceAccess(datosBusqueda.idEspacioTrabajo());
        PaginatedResponse<CompraCreditoDTOResponse> compras =
                comprasCreditoService.buscarComprasCredito(datosBusqueda);
        return new ResponseEntity<>(compras, HttpStatus.OK);
    }
}

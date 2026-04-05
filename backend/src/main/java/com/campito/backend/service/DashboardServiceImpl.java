package com.campito.backend.service;

import lombok.extern.slf4j.Slf4j;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.YearMonth;
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

import org.springframework.stereotype.Service;

import com.campito.backend.dao.CuotaCreditoRepository;
import com.campito.backend.dao.DashboardRepository;
import com.campito.backend.dao.EspacioTrabajoRepository;
import com.campito.backend.dao.GastosIngresosMensualesRepository;
import com.campito.backend.dao.TarjetaRepository;
import com.campito.backend.dto.DashboardStatsDTO;
import com.campito.backend.dto.DistribucionGastoDTO;
import com.campito.backend.dto.FlujoCreditoMesDTO;
import com.campito.backend.dto.FlujoCreditoMesDTOImpl;
import com.campito.backend.dto.IngresosGastosMesDTO;
import com.campito.backend.dto.IngresosGastosMesDTOImpl;
import com.campito.backend.model.CuotaCredito;
import com.campito.backend.model.EspacioTrabajo;
import com.campito.backend.model.GastosIngresosMensuales;
import com.campito.backend.model.Tarjeta;

import jakarta.persistence.EntityNotFoundException;
import lombok.RequiredArgsConstructor;

/**
 * Implementación del servicio para gestión del dashboard.
 * 
 * Proporciona métodos para obtener estadísticas y datos relevantes para el dashboard.
 */
@Service
@RequiredArgsConstructor  // Genera constructor con todos los campos final para inyección de dependencias
@Slf4j
public class DashboardServiceImpl implements DashboardService {

    private final EspacioTrabajoRepository espacioRepository;
    private final DashboardRepository dashboardRepository;
    private final CuotaCreditoRepository cuotaCreditoRepository;
    private final TarjetaRepository tarjetaRepository;
    private final GastosIngresosMensualesRepository gastosIngresosMensualesRepository;

    /**
     * Obtiene las estadísticas consolidadas del dashboard para un espacio de trabajo.
     * 
     * @param idEspacio ID del espacio de trabajo.
     * @return DTO con todas las estadísticas del dashboard (KPIs + charts).
     * @throws EntityNotFoundException si el espacio de trabajo no se encuentra.
     * @throws IllegalArgumentException si el ID del espacio es nulo.
     */
    @Override
    public DashboardStatsDTO obtenerDashboardStats(UUID idEspacio) {

        log.info("Obteniendo estadisticas consolidadas del dashboard para el espacio ID: {}", idEspacio);

        EspacioTrabajo espacio = buscarEspacioTrabajoPorId(idEspacio);
        ZoneId buenosAiresZone = ZoneId.of("America/Argentina/Buenos_Aires");
        ZonedDateTime nowInBuenosAires = ZonedDateTime.now(buenosAiresZone);
        Integer anioActual = nowInBuenosAires.getYear();
        Integer mesActual = nowInBuenosAires.getMonthValue();
        LocalDate now = LocalDate.now();
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM");

        /* 1. Balance total del espacio */
        BigDecimal balanceTotal = espacio.getSaldo();

        /* 2. Gastos del mes actual */
        BigDecimal gastosMensuales = gastosMesActual(espacio, anioActual, mesActual);

        /* 3. Deuda total pendiente (todas las cuotas impagadas) */
        BigDecimal deudaTotalPendiente = cuotaCreditoRepository.calcularDeudaTotalPendiente(idEspacio);

        /* 4. Flujo mensual (últimos 12 meses) */
        
        // Generar lista de los últimos 12 meses (del más antiguo al más reciente)
        List<String> ultimosMeses = new ArrayList<>();
        for (int i = 11; i >= 0; i--) {
            ultimosMeses.add(now.minusMonths(i).format(formatter));
        }

        // Obtener los registros existentes de GastosIngresosMensuales
        List<GastosIngresosMensuales> registrosMensuales = gastosIngresosMensualesRepository
            .findByEspacioTrabajoAndMeses(idEspacio, ultimosMeses);
        
        // Crear un mapa para acceso rápido por mes
        Map<String, GastosIngresosMensuales> mapRegistros = new HashMap<>();
        for (GastosIngresosMensuales reg : registrosMensuales) {
            String mesKey = String.format("%d-%02d", reg.getAnio(), reg.getMes());
            mapRegistros.put(mesKey, reg);
        }

        List<IngresosGastosMesDTO> flujoMensualCompleto = FlujoMensual(now, idEspacio, ultimosMeses, mapRegistros);
        log.debug("Flujo mensual calculado con {} registros encontrados de {} meses solicitados", 
        registrosMensuales.size(), ultimosMeses.size());

        /* 5. Distribución de gastos por motivo (último mes) */
        LocalDate fechaLimite = now.minusMonths(1);
        List<DistribucionGastoDTO> distribucionGastos = dashboardRepository.findDistribucionGastos(idEspacio, fechaLimite);

        /* 6. Flujo de tarjeta mensual (últimos 12 meses) - construido desde registrosMensuales ya cargados */
        List<FlujoCreditoMesDTO> flujoTarjetaMensualCompleto = FlujoCreditoMensual(ultimosMeses, mapRegistros);

        /* 7. Distribución de compras con crédito por motivo (último mes) */
        List<DistribucionGastoDTO> distribucionComprasCredito = dashboardRepository.findDistribucionComprasCredito(idEspacio, fechaLimite);

        /* 8. Resumen mensual (suma de las cuotas que entrarán en los próximos resúmenes por tarjeta) */
        BigDecimal resumenMensual = resumenMensual(idEspacio, now);

        DashboardStatsDTO stats = new DashboardStatsDTO(
            balanceTotal,
            gastosMensuales,
            resumenMensual,
            deudaTotalPendiente,
            flujoMensualCompleto,
            distribucionGastos,
            flujoTarjetaMensualCompleto,
            distribucionComprasCredito
        );

        log.info("Estadisticas del dashboard para el espacio ID {} generadas exitosamente.", idEspacio);
        return stats;
    }

    /*
    ===========================================================================
        MÉTODOS AUXILIARES PRIVADOS
    ===========================================================================
    */

    private EspacioTrabajo buscarEspacioTrabajoPorId(UUID idEspacio) {
        return espacioRepository.findById(idEspacio).orElseThrow(() -> {
            String msg = "Espacio de trabajo con ID " + idEspacio + " no encontrado";
            log.warn(msg);
            return new EntityNotFoundException(msg);
        });
    }

    /**
     * Calcula la fecha de vencimiento del pago del resumen (misma lógica del scheduler)
     */
    private LocalDate calcularFechaVencimiento(LocalDate fechaCierre, int diaVencimiento) {
        YearMonth mesActual = YearMonth.from(fechaCierre);
        YearMonth mesSiguiente = mesActual.plusMonths(1);
        int diaAjustado = Math.min(diaVencimiento, mesSiguiente.lengthOfMonth());
        return mesSiguiente.atDay(diaAjustado);
    }

    /**
     * Calcula el total de gastos del mes actual para el espacio dado.
     */
    private BigDecimal gastosMesActual(EspacioTrabajo espacio, Integer anioActual, Integer mesActual) {
        Optional<GastosIngresosMensuales> opt = gastosIngresosMensualesRepository.findByEspacioTrabajo_IdAndAnioAndMes(espacio.getId(), anioActual, mesActual);

        GastosIngresosMensuales registro = opt.orElseGet(() -> {
            return GastosIngresosMensuales.builder()
                    .anio(anioActual)
                    .mes(mesActual)
                    .gastos(BigDecimal.ZERO)
                    .ingresos(BigDecimal.ZERO)
                    .espacioTrabajo(espacio)
                    .build();
        });

        return registro.getGastos();
    }

        /**
        * Obtiene el flujo mensual de ingresos y gastos para los últimos 12 meses.
        * Rellena con ceros los meses que no tengan registros.
        */
    private List<IngresosGastosMesDTO> FlujoMensual(LocalDate now, UUID idEspacio, List<String> ultimosMeses, Map<String, GastosIngresosMensuales> mapRegistros) {
        
        // Construir la lista completa con todos los meses (rellenar con ceros los faltantes)
        List<IngresosGastosMesDTO> flujoMensualCompleto = new ArrayList<>();
        for (String mes : ultimosMeses) {
            GastosIngresosMensuales reg = mapRegistros.get(mes);
            if (reg != null) {
                flujoMensualCompleto.add(new IngresosGastosMesDTOImpl(
                    mes,
                    reg.getIngresos(),
                    reg.getGastos()
                ));
            } else {
                // Mes sin datos: ingresos y gastos en cero
                flujoMensualCompleto.add(new IngresosGastosMesDTOImpl(
                    mes,
                    BigDecimal.ZERO,
                    BigDecimal.ZERO
                ));
            }
        }
        return flujoMensualCompleto;
    }

    /* Obtener el flujo mensual de tarjetas para los últimos 12 meses */
    private List<FlujoCreditoMesDTO> FlujoCreditoMensual(List<String> ultimosMeses, Map<String, GastosIngresosMensuales> mapRegistros) {
        List<FlujoCreditoMesDTO> flujoTarjetaMensualCompleto = new ArrayList<>();
        for (String mes : ultimosMeses) {
            GastosIngresosMensuales reg = mapRegistros.get(mes);
            if (reg != null) {
                flujoTarjetaMensualCompleto.add(new FlujoCreditoMesDTOImpl(
                    mes,
                    reg.getComprasCredito() != null ? reg.getComprasCredito() : BigDecimal.ZERO,
                    reg.getPagoResumen() != null ? reg.getPagoResumen() : BigDecimal.ZERO
                ));
            } else {
                flujoTarjetaMensualCompleto.add(new FlujoCreditoMesDTOImpl(
                    mes,
                    BigDecimal.ZERO,
                    BigDecimal.ZERO
                ));
            }
        }
        return flujoTarjetaMensualCompleto;
    }

    /**
     * Calcula el resumen mensual total (suma de cuotas que entrarán en próximos resúmenes).
     * Optimizado para minimizar queries: trae todas las tarjetas, calcula el rango máximo de 
     * fechas y luego trae todas las cuotas pendientes en ese rango para filtrar en memoria.
     */
    private BigDecimal resumenMensual(UUID idEspacio, LocalDate now) {
        // 1. Traer todas las tarjetas del espacio (1 query)
        List<Tarjeta> tarjetas = tarjetaRepository.findByEspacioTrabajo_Id(idEspacio);
        
        if (tarjetas.isEmpty()) {
            return BigDecimal.ZERO;
        }

        // 2. Calcular el rango de fechas más amplio posible para todas las tarjetas
        //    Esto permite traer todas las cuotas relevantes en una sola query
        LocalDate fechaInicioMinima = now;
        LocalDate fechaFinMaxima = now;
        
        for (Tarjeta tarjeta : tarjetas) {
            YearMonth ym = YearMonth.from(now);
            int diaAjustadoCierre = Math.min(tarjeta.getDiaCierre(), ym.lengthOfMonth());
            LocalDate fechaCierre = ym.atDay(diaAjustadoCierre);
            
            if (!fechaCierre.isAfter(now)) {
                YearMonth siguiente = ym.plusMonths(1);
                diaAjustadoCierre = Math.min(tarjeta.getDiaCierre(), siguiente.lengthOfMonth());
                fechaCierre = siguiente.atDay(diaAjustadoCierre);
            }
            
            LocalDate fechaInicio = fechaCierre.plusDays(1);
            LocalDate fechaFin = calcularFechaVencimiento(fechaCierre, tarjeta.getDiaVencimientoPago());
            
            if (fechaInicio.isBefore(fechaInicioMinima)) {
                fechaInicioMinima = fechaInicio;
            }
            if (fechaFin.isAfter(fechaFinMaxima)) {
                fechaFinMaxima = fechaFin;
            }
        }
        
        // 3. Traer TODAS las cuotas pendientes sin resumen en el rango amplio (1 query batch)
        //    Usamos la nueva query optimizada que trae todo de una vez
        List<CuotaCredito> todasLasCuotasPendientes = cuotaCreditoRepository
            .findByEspacioTrabajoSinResumenEnRango(idEspacio, fechaInicioMinima, fechaFinMaxima);
        
        // 4. Filtrar y sumar en memoria según el período específico de cada tarjeta
        BigDecimal resumenMensual = BigDecimal.ZERO;
        
        for (Tarjeta tarjeta : tarjetas) {
            int diaCierre = tarjeta.getDiaCierre();
            
            YearMonth ym = YearMonth.from(now);
            int diaAjustadoCierre = Math.min(diaCierre, ym.lengthOfMonth());
            LocalDate fechaCierre = ym.atDay(diaAjustadoCierre);
            
            if (!fechaCierre.isAfter(now)) {
                YearMonth siguiente = ym.plusMonths(1);
                diaAjustadoCierre = Math.min(diaCierre, siguiente.lengthOfMonth());
                fechaCierre = siguiente.atDay(diaAjustadoCierre);
            }
            
            LocalDate fechaInicio = fechaCierre.plusDays(1);
            LocalDate fechaFin = calcularFechaVencimiento(fechaCierre, tarjeta.getDiaVencimientoPago());
            
            // Filtrar cuotas de esta tarjeta en su período específico
            BigDecimal montoTarjeta = todasLasCuotasPendientes.stream()
                .filter(cuota -> cuota.getCompraCredito().getTarjeta().getId().equals(tarjeta.getId()))
                .filter(cuota -> !cuota.getFechaVencimiento().isBefore(fechaInicio) 
                              && !cuota.getFechaVencimiento().isAfter(fechaFin))
                .map(CuotaCredito::getMontoCuota)
                .reduce(BigDecimal.ZERO, BigDecimal::add);
            
            resumenMensual = resumenMensual.add(montoTarjeta);
        }
        
        return resumenMensual;
    }
}

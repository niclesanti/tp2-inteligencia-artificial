---
name: shadcn_UI_Skill
description: >
  Skill de diseño system y componentes UI para el frontend del Gestor de Gastos
  Personales. Indexa la configuración de shadcn/ui, las variables CSS del tema
  oscuro, los patrones de componentes (Radix + Tailwind + CVA), y los componentes
  existentes en src/components/ui/. Úsala para crear nuevos componentes UI,
  páginas o features siguiendo el estilo y patrones establecidos.
---

# shadcn_UI_Skill — Diseño System y Componentes UI

## Configuración de shadcn/ui

```json
{
  "style": "new-york",
  "rsc": false,
  "tsx": true,
  "tailwind": {
    "config": "tailwind.config.js",
    "css": "src/index.css",
    "baseColor": "neutral",
    "cssVariables": true,
    "prefix": ""
  },
  "iconLibrary": "lucide",
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils",
    "ui": "@/components/ui",
    "lib": "@/lib",
    "hooks": "@/hooks"
  }
}
```

- **Style**: `new-york` — bordes más sutiles, espaciado compacto
- **baseColor**: `neutral` — grises neutros sin subtonos cálidos/fríos
- **CSS variables**: `true` — todos los colores via HSL variables para dark mode
- **Icon library**: `lucide-react` (version 0.307.0)

## Sistema de Diseño

### Paleta de Colores (Dark Mode)

| Variable | HSL Value | Uso |
|----------|-----------|-----|
| `--background` | `0 0% 3.9%` | Fondo principal |
| `--foreground` | `0 0% 98%` | Texto principal |
| `--card` | `240 5.9% 10%` | Fondo de cards |
| `--card-foreground` | `0 0% 98%` | Texto en cards |
| `--popover` | `0 0% 3.9%` | Fondo de popovers/dropdowns |
| `--primary` | `0 0% 98%` | Botón primario (blanco) |
| `--primary-foreground` | `0 0% 9%` | Texto en botón primario |
| `--secondary` | `0 0% 14.9%` | Botón secundario |
| `--muted` | `0 0% 14.9%` | Elementos apagados |
| `--muted-foreground` | `0 0% 63.9%` | Texto secundario |
| `--accent` | `0 0% 14.9%` | Hover/accent |
| `--accent-foreground` | `0 0% 98%` | Texto en accent |
| `--destructive` | `0 62.8% 30.6%` | Rojo destructivo |
| `--destructive-foreground` | `0 0% 98%` | Texto destructivo |
| `--border` | `0 0% 14.9%` | Bordes |
| `--input` | `0 0% 14.9%` | Bordes de input |
| `--ring` | `0 0% 83.1%` | Focus ring |
| `--radius` | `0.5rem` | Border radius base |
| `--chart-1` | `217 72% 58%` | Azul gráficos |
| `--chart-2` | `160 76% 52%` | Verde gráficos |
| `--chart-3` | `30 78% 56%` | Naranja gráficos |
| `--chart-4` | `260 74% 58%` | Púrpura gráficos |
| `--chart-5` | `340 76% 58%` | Rosa gráficos |
| `--sidebar-background` | `240 5.9% 10%` | Fondo sidebar |
| `--sidebar-foreground` | `240 4.8% 95.9%` | Texto sidebar |
| `--sidebar-primary` | `0 0% 98%` | Primario sidebar |
| `--sidebar-border` | `240 3.7% 15.9%` | Borde sidebar |

**Importante**: Todos los colores se usan via `hsl(var(--variable))` en Tailwind — NUNCA hardcodear valores de color.

### Tipografía

```css
--font-sans: "Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI",
             Roboto, "Helvetica Neue", Arial, sans-serif;
--font-mono: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Monaco, Consolas,
             "Liberation Mono", "Courier New", monospace;
```

- Inter como variable font con pesos 100-900
- `font-feature-settings: "rlig" 1, "calt" 1`

### Espaciado y Border Radius

```js
borderRadius: {
  lg: 'var(--radius)',               // 0.5rem (8px)
  md: 'calc(var(--radius) - 2px)',   // 6px
  sm: 'calc(var(--radius) - 4px)',   // 4px
}
```

### Breakpoints

```js
screens: { sm: '640px', md: '768px', lg: '1024px', xl: '1280px', '2xl': '1400px' }
```

### Animaciones

- `accordion-down` / `accordion-up` (para acordeones Radix)
- `animate-in` / `animate-out` (fade, slide, zoom — de tailwindcss-animate)
- `avatar-pulse` — animación CSS personalizada para el thinking indicator del Agente IA

## Patrones de Componentes

### Estructura de un Componente shadcn/ui

```tsx
import * as React from "react"
import * as Primitive from "@radix-ui/react-..."
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

// Variantes con CVA (opcional, solo si tiene variantes)
const componentVariants = cva(
  "base-classes",
  {
    variants: {
      variant: { default: "...", secondary: "..." },
      size: { default: "...", sm: "..." },
    },
    defaultVariants: { variant: "default", size: "default" },
  }
)

// Componente principal
const Component = React.forwardRef<
  React.ElementRef<typeof Primitive.Root>,
  React.ComponentPropsWithoutRef<typeof Primitive.Root> & VariantProps<typeof componentVariants>
>(({ className, ...props }, ref) => (
  <Primitive.Root
    ref={ref}
    className={cn(componentVariants({ className }))}
    {...props}
  />
))
Component.displayName = Primitive.Root.displayName

export { Component, componentVariants }
```

### Todos los Componentes UI Disponibles

La aplicación tiene los siguientes componentes shadcn/ui en `src/components/ui/`:

| Componente | Archivo | Dependencia Radix |
|-----------|---------|-------------------|
| AlertDialog | `alert-dialog.tsx` | `@radix-ui/react-alert-dialog` |
| Avatar | `avatar.tsx` | `@radix-ui/react-avatar` |
| Badge | `badge.tsx` | — (CVA-based) |
| Breadcrumb | `breadcrumb.tsx` | — (HTML + cn) |
| Button | `button.tsx` | `@radix-ui/react-slot` + CVA |
| Calendar | `calendar.tsx` | `react-day-picker` |
| Card | `card.tsx` | — (HTML + cn) |
| Chart | `chart.tsx` | Recharts wrapper |
| Checkbox | `checkbox.tsx` | `@radix-ui/react-checkbox` |
| Command | `command.tsx` | `cmdk` + `@radix-ui/react-dialog` |
| DataTable | `data-table.tsx` | `@tanstack/react-table` |
| Dialog | `dialog.tsx` | `@radix-ui/react-dialog` |
| Drawer | `drawer.tsx` | `vaul` |
| DropdownMenu | `dropdown-menu.tsx` | `@radix-ui/react-dropdown-menu` |
| Form | `form.tsx` | `react-hook-form` + `@radix-ui/react-label` |
| Input | `input.tsx` | — (HTML + cn) |
| Label | `label.tsx` | `@radix-ui/react-label` |
| Pagination | `pagination.tsx` | — (HTML + cn) |
| Popover | `popover.tsx` | `@radix-ui/react-popover` |
| RadioGroup | `radio-group.tsx` | `@radix-ui/react-radio-group` |
| ScrollArea | `scroll-area.tsx` | `@radix-ui/react-scroll-area` |
| Select | `select.tsx` | `@radix-ui/react-select` |
| Separator | `separator.tsx` | `@radix-ui/react-separator` |
| Sheet | `sheet.tsx` | `@radix-ui/react-dialog` |
| Sidebar | `sidebar.tsx` | `@radix-ui/react-collapsible` + `@radix-ui/react-tooltip` |
| Skeleton | `skeleton.tsx` | — (HTML + cn) |
| Switch | `switch.tsx` | `@radix-ui/react-switch` |
| Table | `table.tsx` | — (HTML + cn) |
| Tabs | `tabs.tsx` | `@radix-ui/react-tabs` |
| Textarea | `textarea.tsx` | — (HTML + cn) |
| Tooltip | `tooltip.tsx` | `@radix-ui/react-tooltip` |
| VisuallyHidden | `visually-hidden.tsx` | `@radix-ui/react-visually-hidden` |

## Patrones de Layout Responsive

### Dashboard Layout (Grid System)

```tsx
<div className="grid gap-4 pt-4 md:gap-6 md:pt-6">
  {/* Full width */}
  <DashboardStats />

  {/* 2 columns on large screens */}
  <div className="grid gap-4 md:gap-6 lg:grid-cols-3">
    <MonthlyCashflow />   {/* col-span-1 lg:col-span-2 para ocupar 2/3 */}
    <SpendingByCategory />
  </div>

  {/* 2 columns */}
  <div className="grid gap-4 md:gap-6 lg:grid-cols-2">
    <BankAccounts />
    <UpcomingPayments />
  </div>
</div>
```

### Card Pattern

```tsx
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'

<Card>
  <CardHeader>
    <CardTitle>Título</CardTitle>
    <CardDescription>Descripción opcional</CardDescription>
  </CardHeader>
  <CardContent>
    {/* contenido */}
  </CardContent>
</Card>
```

### Modal Pattern (Desktop ↔ Mobile)

```tsx
// En mobile: usar Drawer (Vaul)
// En desktop: usar Dialog (Radix)

// Ver uso en TransactionModal.tsx o CreditPurchaseModal.tsx
// Patrón: useIsMobile() hook para decidir
import { useIsMobile } from '@/hooks/use-mobile'

function Modal({ open, onOpenChange, children }) {
  const isMobile = useIsMobile()

  if (isMobile) {
    return <Drawer open={open} onOpenChange={onOpenChange}>{children}</Drawer>
  }
  return <Dialog open={open} onOpenChange={onOpenChange}>{children}</Dialog>
}
```

### Tabla de Datos

```tsx
import { DataTable } from '@/components/ui/data-table'

// Usar @tanstack/react-table con el wrapper DataTable
// Ver MovimientosPage.tsx para referencia
```

### Sidebar + Header Layout

```tsx
// Layout principal (DashboardLayout.tsx)
<SidebarProvider>
  <AppSidebar />
  <SidebarInset>
    <Header />
    <main className="flex flex-1 flex-col gap-4 px-3 py-4 pt-0 sm:px-4 md:p-4 md:pt-0">
      <PageTransition />  {/* Anima las transiciones entre rutas */}
    </main>
    <MobileActionsFAB />  {/* Solo visible en mobile */}
  </SidebarInset>
</SidebarProvider>
```

## Patrones Específicos del Proyecto

### MoneyDisplay (Visualización Monetaria)

```tsx
import { MoneyDisplay } from '@/components/MoneyDisplay'

<MoneyDisplay value={1234.56} />               // "$1,234.56"
<MoneyDisplay value={balance} colored />        // Verde/rojo según signo
<MoneyDisplay value={null} fallback="N/A" />    // "N/A"
<MoneyDisplay value={monto} showCurrency={false} decimals={3} />
```

### MoneyInput (Entrada Monetaria)

```tsx
import { MoneyInput } from '@/components/MoneyInput'

<MoneyInput
  value={monto}
  onChange={setMonto}
  min={0}
  max={balance}
  allowNegative={false}
  showPrefix={true}
  placeholder="0.00"
/>
```

### EmptyState Pattern

```tsx
import { EmptyState } from '@/components/EmptyState'
import { BarChart3 } from 'lucide-react'

<EmptyState
  illustration={<BarChart3 className="text-muted-foreground" strokeWidth={1.5} />}
  title="Aún no hay datos"
  description="Comienza a registrar para ver información aquí."
/>
```

### AnimatedCounter

```tsx
import { AnimatedCounter } from '@/components/AnimatedCounter'

<AnimatedCounter value={numericValue} formatFn={(val) => formatCurrency(val)} />
```

### Recharts Pattern (with ChartContainer)

```tsx
"use client"

import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from 'recharts'
import {
  ChartContainer,
  ChartTooltip,
  ChartLegend,
  ChartLegendContent,
  type ChartConfig,
} from '@/components/ui/chart'

const chartConfig = {
  ingresos: { label: 'Ingresos', color: 'hsl(var(--chart-2))' },
  gastos: { label: 'Gastos', color: 'hsl(var(--chart-3))' },
} satisfies ChartConfig

<ChartContainer config={chartConfig} className="h-[200px] sm:h-[280px] lg:h-[350px] w-full">
  <BarChart data={data} margin={{ left: 5, right: 10, top: 10, bottom: 0 }}>
    <CartesianGrid vertical={false} strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.3} />
    <XAxis dataKey="month" tickLine={false} axisLine={false} tickMargin={8} tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 11 }} />
    <ChartTooltip content={<CustomTooltip />} />
    <ChartLegend content={<ChartLegendContent />} />
    <Bar dataKey="ingresos" fill="hsl(var(--chart-2))" radius={[4, 4, 0, 0]} />
  </BarChart>
</ChartContainer>
```

### Forms con React Hook Form + Zod

```tsx
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Form, FormField, FormItem, FormLabel, FormControl, FormMessage } from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'

const formSchema = z.object({
  nombre: z.string().min(1, 'El nombre es requerido'),
  monto: z.number().positive('Debe ser un monto positivo'),
})

function MyForm() {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: { nombre: '', monto: 0 },
  })

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField control={form.control} name="nombre" render={({ field }) => (
          <FormItem>
            <FormLabel>Nombre</FormLabel>
            <FormControl><Input {...field} /></FormControl>
            <FormMessage />
          </FormItem>
        )} />
        <Button type="submit">Guardar</Button>
      </form>
    </Form>
  )
}
```

### DataTable Pattern

```tsx
import { DataTable } from '@/components/ui/data-table'
import { ColumnDef } from '@tanstack/react-table'
import { MoneyDisplay } from '@/components/MoneyDisplay'

const columns: ColumnDef<Transaccion>[] = [
  { accessorKey: 'fecha', header: 'Fecha' },
  { accessorKey: 'monto', header: 'Monto', cell: ({ row }) => <MoneyDisplay value={row.original.monto} colored /> },
  { accessorKey: 'tipo', header: 'Tipo' },
]
```

### Componentes de Feedback

```tsx
// Confirmación de eliminación
import { DeleteConfirmDialog } from '@/components/DeleteConfirmDialog'
<DeleteConfirmDialog
  open={open}
  onOpenChange={setOpen}
  onConfirm={handleDelete}
  title="Eliminar transacción"
  description="¿Estás seguro? Esta acción no se puede deshacer."
/>

// Toast notifications (via Sonner, configurado en App.tsx con <Toaster />)
import { toast } from 'sonner'
toast.success('Operación exitosa')
toast.error('Error al procesar')
```

## Convenciones de Estilo para Tailwind

- Usar `text-muted-foreground` para texto secundario (nunca `text-gray-400`)
- Usar `bg-card` / `bg-background` para fondos (nunca `bg-gray-900`)
- Usar `border-border` para bordes
- Responsive: `p-3 md:p-6`, `text-xs md:text-sm`, `grid-cols-2 lg:grid-cols-4`
- Iconos: `className="h-4 w-4"` (tamaño estándar), con `className="size-4"` también aceptado
- Loading: `Loader2` con `animate-spin`
- Evitar `min-h-screen` — usar `min-h-[calc(100dvh-4rem)]` para full-height dinámico
- Usar `overflow-x-hidden` y `w-full max-w-full` en contenedores del dashboard para evitar scroll horizontal

## Gestión de Estado (Zustand Store Pattern)

```ts
import { create } from 'zustand'

const CACHE_DURATION = 5 * 60 * 1000 // 5 minutos

const isCacheValid = (timestamp: number): boolean =>
  Date.now() - timestamp < CACHE_DURATION

interface MyCache { data: MyType[]; timestamp: number }

interface MyState {
  items: Map<string, MyCache>
  loadItems: (id: string, forceRefresh?: boolean) => Promise<MyType[]>
  invalidateItems: (id: string) => void
}
```

## Componentes Compartidos Existentes

| Componente | Archivo | Propósito |
|-----------|---------|-----------|
| `NotificationBell` | `components/notifications/NotificationBell.tsx` | Campana con badge + popover |
| `NotificationCenter` | `components/notifications/NotificationCenter.tsx` | Panel lateral completo |
| `NotificationItem` | `components/notifications/NotificationItem.tsx` | Item individual |
| `DeleteConfirmDialog` | `components/DeleteConfirmDialog.tsx` | Confirmación eliminación |
| `TransactionModal` | `components/TransactionModal.tsx` | Registrar/editar transacción |
| `TransactionDetailsModal` | `components/TransactionDetailsModal.tsx` | Detalle transacción |
| `AccountTransferModal` | `components/AccountTransferModal.tsx` | Transferencia entre cuentas |
| `CreditPurchaseModal` | `components/CreditPurchaseModal.tsx` | Compra en cuotas |
| `CreditPurchaseDetailsModal` | `components/CreditPurchaseDetailsModal.tsx` | Detalle compra crédito |
| `CardPaymentModal` | `components/CardPaymentModal.tsx` | Pago resumen tarjeta |
| `MobileActionsFAB` | `components/MobileActionsFAB.tsx` | FAB con acciones rápidas |
| `PaymentProviderLogo` | `components/PaymentProviderLogo.tsx` | Logo red de pago |
| `ProtectedRoute` | `components/ProtectedRoute.tsx` | HOC de autenticación |
| `Header` | `components/Header.tsx` | Header de la app |
| `EmptyState` | `components/EmptyState.tsx` | Estado vacío con ilustración |
| `AnimatedCounter` | `components/AnimatedCounter.tsx` | Contador animado |
| `PageTransition` | `components/PageTransition.tsx` | Transición entre páginas |

## Reglas de Validación para Código UI Generado

1. **Usar variables CSS HSL** para todos los colores — no hardcodear
2. **Responsive**: todo componente debe funcionar en mobile (<768px) y desktop
3. **Dark mode**: el tema oscuro es el único soportado, probar en `.dark`
4. **Precisión monetaria**: usar siempre MoneyDecimal, nunca `number` o `float` para montos
5. **Iconos**: solo Lucide React (`lucide-react`), todas las importaciones desde el paquete
6. **Accesibilidad**: usar primitivos Radix UI con ARIA completo
7. **Performance**: memoizar componentes pesados con `React.memo`, usar `useMemo`/`useCallback`
8. **No duplicar**: revisar componentes existentes antes de crear nuevos
9. **shadcn/ui components**: no modificar los componentes base en `src/components/ui/` — extenderlos via props o crear wrappers
10. **Importaciones**: usar `@/` path alias, ej: `@/components/ui/button`, `@/lib/utils`
11. **Sin `any`**: tipar correctamente con TypeScript, usar `satisfies` para configuraciones de charts
12. **Sin comentarios**: no agregar comentarios a menos que sea absolutamente necesario

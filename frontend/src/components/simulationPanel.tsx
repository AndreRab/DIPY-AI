import { useCallback, useEffect, useLayoutEffect, useRef, useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import ky from "ky"
import { backendUrl } from "@/agent/agent"
import { Button } from "@/components/ui/button"

type Camera = { x: number; y: number; scale: number; zoom: number }

type Pair = { command: number | null; measured: number | null }
type Values = Record<string, number | null | Pair>
type Step = { step: number; segment: number; values: Values }
type Snapshot = { interval_ms: number; run_id: string | null; mode: string | null; running: boolean; error: string | null; states: Step[] }
type Mode = { id: string; label: string }
const fields: Record<string, string> = {
    x_position_mm: "X · mm", y_position_mm: "Y · mm", laser_power_w: "Power · W",
    scan_speed_mm_s: "Scan speed · mm/s", melt_pool_length_t100_mm: "Melt pool length T100 · mm",
    melt_pool_width_t100_mm: "Melt pool width T100 · mm", melt_pool_area_t80_mm2: "Melt pool area T80 · mm²",
    melt_pool_area_t100_mm2: "Melt pool area T100 · mm²", melt_pool_area_t120_mm2: "Melt pool area T120 · mm²",
}
const format = (value: number | null) => value === null ? "No data" : value.toLocaleString("en-US", { maximumFractionDigits: 5 })

function LaserMap({ states, selected }: { states: Step[]; selected: Step | null }) {
    const mapRef = useRef<HTMLDivElement>(null)
    const drag = useRef<{ y: number; height: number } | null>(null)
    const [camera, setCamera] = useState<Camera | null>(null)
    const pan = useRef<{ pointer: number; x: number; y: number; camera: Camera } | null>(null)
    const [panning, setPanning] = useState(false)
    const [height, setHeight] = useState(150)
    const [size, setSize] = useState({ width: 360, height: 150 })
    useEffect(() => {
        const element = mapRef.current
        if (!element) return
        const observer = new ResizeObserver(([entry]) => setSize({ width: entry.contentRect.width, height: entry.contentRect.height }))
        observer.observe(element)
        return () => observer.disconnect()
    }, [])
    const resize = (next: number) => {
        const map = mapRef.current
        const panel = map?.closest("aside")
        const maximum = map && panel ? Math.max(90, panel.getBoundingClientRect().bottom - map.getBoundingClientRect().top - 220) : 450
        setHeight(Math.max(90, Math.min(next, maximum)))
    }
    const active = states.at(-1)
    const segment = states.filter(s => s.segment === active?.segment)
    const coordinate = (s: Step, axis: string, kind: keyof Pair) => (s.values[axis] as Pair)?.[kind] ?? null
    const points = [...segment, ...(selected ? [selected] : [])].flatMap(s => (["command", "measured"] as const).flatMap(kind => {
        const x = coordinate(s, "x_position_mm", kind), y = coordinate(s, "y_position_mm", kind)
        return x === null || y === null ? [] : [{ x, y }]
    }))
    const xs = points.map(p => p.x), ys = points.map(p => p.y)
    const minX = xs.length ? Math.min(...xs) : -0.5, maxX = xs.length ? Math.max(...xs) : 0.5, minY = ys.length ? Math.min(...ys) : -0.5, maxY = ys.length ? Math.max(...ys) : 0.5
    const span = Math.max(maxX - minX, maxY - minY, 1)
    const scale = Math.max(1, Math.min(size.width - 40, size.height - 40)) / span
    const fitX = (minX + maxX) / 2, fitY = (minY + maxY) / 2
    const view = camera ?? { x: fitX, y: fitY, scale, zoom: 1 }
    const zoomAt = useCallback((factor: number, px: number, py: number) => {
        setCamera(previous => {
            const current = previous ?? { x: fitX, y: fitY, scale, zoom: 1 }
            const zoom = Math.max(0.1, Math.min(50, current.zoom * factor))
            const nextScale = current.scale * zoom / current.zoom
            const dx = px - size.width / 2, dy = py - size.height / 2
            return { x: current.x + dx / current.scale - dx / nextScale, y: current.y - dy / current.scale + dy / nextScale, scale: nextScale, zoom }
        })
    }, [fitX, fitY, scale, size.width, size.height])
    useEffect(() => {
        const element = mapRef.current
        if (!element) return
        const wheel = (event: WheelEvent) => {
            event.preventDefault()
            const rect = element.getBoundingClientRect()
            const delta = event.deltaY * (event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? rect.height : 1)
            zoomAt(Math.exp(-Math.max(-100, Math.min(100, delta)) * 0.01), event.clientX - rect.left, event.clientY - rect.top)
        }
        element.addEventListener("wheel", wheel, { passive: false })
        return () => element.removeEventListener("wheel", wheel)
    }, [zoomAt])
    const project = (x: number, y: number) => `${size.width / 2 + (x - view.x) * view.scale},${size.height / 2 - (y - view.y) * view.scale}`
    const path = (kind: keyof Pair) => {
        let connected = false
        return segment.map(s => {
            const x = coordinate(s, "x_position_mm", kind), y = coordinate(s, "y_position_mm", kind)
            if (x === null || y === null) { connected = false; return "" }
            const command = connected ? "L" : "M"; connected = true
            return `${command}${project(x, y)}`
        }).join(" ")
    }
    const x = active ? coordinate(active, "x_position_mm", "measured") : null
    const y = active ? coordinate(active, "y_position_mm", "measured") : null
    const marker = x !== null && y !== null ? project(x, y).split(",").map(Number) : null
    const selectedX = selected ? coordinate(selected, "x_position_mm", "measured") : null
    const selectedY = selected ? coordinate(selected, "y_position_mm", "measured") : null
    const selectedMarker = selectedX !== null && selectedY !== null ? project(selectedX, selectedY).split(",").map(Number) : null
    return <div className="shrink-0 rounded-xl border bg-background p-3">
        <div className="flex flex-wrap items-center justify-between gap-2 text-sm"><strong>Laser map</strong>
            <div className="flex items-center gap-1">
                <Button variant="outline" size="sm" aria-label="Zoom out" onClick={() => zoomAt(1 / 1.25, size.width / 2, size.height / 2)}>−</Button>
                <Button variant="outline" size="sm" aria-label="Zoom in" onClick={() => zoomAt(1.25, size.width / 2, size.height / 2)}>+</Button>
                <Button variant="outline" size="sm" onClick={() => setCamera(null)}>Reset view</Button>
            </div>
        </div>
        <div ref={mapRef} className={`my-2 w-full touch-none overflow-hidden rounded-lg bg-muted/40 ${panning ? "cursor-grabbing" : "cursor-grab"}`} style={{ height }}
            onDoubleClick={() => setCamera(null)}
            onPointerDown={event => {
                if (event.button !== 0) return
                event.preventDefault()
                event.currentTarget.setPointerCapture(event.pointerId)
                pan.current = { pointer: event.pointerId, x: event.clientX, y: event.clientY, camera: view }
                setCamera(view)
                setPanning(true)
            }}
            onPointerMove={event => {
                const start = pan.current
                if (!start || start.pointer !== event.pointerId) return
                setCamera({ ...start.camera, x: start.camera.x - (event.clientX - start.x) / start.camera.scale, y: start.camera.y + (event.clientY - start.y) / start.camera.scale })
            }}
            onPointerUp={() => { pan.current = null; setPanning(false) }}
            onPointerCancel={() => { pan.current = null; setPanning(false) }}
            onLostPointerCapture={() => { pan.current = null; setPanning(false) }}>
        <svg viewBox={`0 0 ${size.width} ${size.height}`} className="h-full w-full" role="img" aria-label="Commanded and measured laser paths">
            <defs><pattern id="laser-grid" width="24" height="24" patternUnits="userSpaceOnUse" patternTransform={`translate(${size.width / 2 - view.x * view.scale} ${size.height / 2 + view.y * view.scale}) scale(${view.zoom})`}><path d="M 24 0 L 0 0 0 24" fill="none" stroke="currentColor" strokeOpacity="0.08" /></pattern></defs>
            <rect width={size.width} height={size.height} fill="url(#laser-grid)" />
            {points.length > 0 ? <>
                <path d={path("command")} stroke="#94a3b8" strokeWidth="2" strokeDasharray="5 4" fill="none" />
                <path d={path("measured")} stroke="#0d9488" strokeWidth="2" fill="none" />
                {selectedMarker && <circle cx={selectedMarker[0]} cy={selectedMarker[1]} r="6" fill="#6b7280" stroke="white" strokeWidth="2"><title>Selected step {selected?.step}</title></circle>}
                {marker && <circle cx={marker[0]} cy={marker[1]} r="5" fill="#f97316" stroke="white" strokeWidth="2" />}
            </> : <text x={size.width / 2} y={size.height / 2} textAnchor="middle" fill="currentColor" fontSize="13">Waiting for data</text>}
        </svg>
        </div>
        <div role="separator" aria-label="Resize laser map" aria-orientation="horizontal" aria-valuemin={90} aria-valuenow={height} tabIndex={0}
            className="mb-2 flex h-4 touch-none cursor-row-resize items-center justify-center rounded hover:bg-muted focus-visible:outline-2"
            onPointerDown={event => { event.currentTarget.setPointerCapture(event.pointerId); drag.current = { y: event.clientY, height } }}
            onPointerMove={event => { if (drag.current) resize(drag.current.height + event.clientY - drag.current.y) }}
            onPointerUp={() => { drag.current = null }} onPointerCancel={() => { drag.current = null }}
            onKeyDown={event => { if (event.key === "ArrowDown" || event.key === "ArrowUp") { event.preventDefault(); resize(height + (event.key === "ArrowDown" ? 20 : -20)) } }}>
            <span className="h-1 w-10 rounded-full bg-border" />
        </div>
        <div className="flex flex-wrap gap-3 text-xs text-muted-foreground"><span>┄ Commanded</span><span className="text-teal-600">━ Measured</span><span className="text-orange-500">● Laser</span>{selected && <span className="text-gray-500">● Selected step {selected.step}</span>}</div>
        <p className="mt-2 text-xs text-muted-foreground">Scroll to zoom · Drag to pan · Double-click to reset · X / Y in mm</p>
        {active && <p className="mt-2 text-xs text-muted-foreground">Step {active.step} · X {format(x)} · Y {format(y)}</p>}
    </div>
}

export function SimulationPanel() {
    const client = useQueryClient()
    const [interval, setInterval] = useState<number | null>(null)
    const [mode, setMode] = useState<string | null>(null)
    const [selection, setSelection] = useState<{ run: string; state: Step } | null>(null)
    const modes = useQuery({ queryKey: ["simulation-modes"], queryFn: () => ky.get(`${backendUrl}/simulation/modes`).json<Mode[]>() })
    const simulation = useQuery({ queryKey: ["simulation"], queryFn: ({ signal }) => ky.get(`${backendUrl}/simulation`, { signal }).json<Snapshot>(), refetchInterval: query => Math.max(100, Math.min(1000, query.state.data?.interval_ms ?? 1000)) })
    const options = modes.data ?? []
    const chosen = mode ?? options[0]?.id
    const data = simulation.data
    const intervalMs = interval ?? data?.interval_ms ?? 1000
    const inspected = selection?.run === data?.run_id ? selection : null
    const selected = inspected?.state.step ?? null
    const rows = data ? [...data.states, ...(inspected && !data.states.some(s => s.step === selected) ? [inspected.state] : [])].sort((a, b) => b.step - a.step) : []
    const listRef = useRef<HTMLDivElement>(null)
    const selectedRowRef = useRef<HTMLDivElement>(null)
    const anchorRef = useRef<{ run: string; step: number; offset: number } | null>(null)
    const rememberPosition = () => {
        const list = listRef.current
        const row = selectedRowRef.current
        anchorRef.current = list && row && inspected ? {
            run: inspected.run, step: inspected.state.step,
            offset: row.getBoundingClientRect().top - list.getBoundingClientRect().top,
        } : null
    }
    useLayoutEffect(() => {
        const list = listRef.current
        const row = selectedRowRef.current
        const anchor = anchorRef.current
        if (list && row && inspected && anchor?.run === inspected.run && anchor.step === selected) {
            const offset = row.getBoundingClientRect().top - list.getBoundingClientRect().top
            list.scrollTop += offset - anchor.offset
        }
        rememberPosition()
    })
    const start = useMutation({
        mutationFn: async () => {
            await client.cancelQueries({ queryKey: ["simulation"] })
            return ky.post(`${backendUrl}/simulation/start`, { json: { mode: chosen, interval_ms: intervalMs } }).json<Snapshot>()
        },
        onSuccess: snapshot => { setSelection(null); client.setQueryData(["simulation"], snapshot) },
    })
    const stop = useMutation({
        mutationFn: async () => {
            await client.cancelQueries({ queryKey: ["simulation"] })
            return ky.post(`${backendUrl}/simulation/stop`).json<Snapshot>()
        },
        onSuccess: snapshot => client.setQueryData(["simulation"], snapshot),
    })
    const resume = useMutation({
        mutationFn: async () => {
            await client.cancelQueries({ queryKey: ["simulation"] })
            return ky.post(`${backendUrl}/simulation/resume`, { json: { interval_ms: intervalMs } }).json<Snapshot>()
        },
        onSuccess: snapshot => client.setQueryData(["simulation"], snapshot),
    })
    const busy = start.isPending || stop.isPending || resume.isPending
    return <aside className="flex h-full min-h-0 flex-col gap-3 overflow-hidden p-4" aria-label="Simulation panel">
        <div className="shrink-0"><h2 className="text-lg font-semibold">Simulation</h2><p className="text-sm text-muted-foreground">Select a mode and start a new run.</p></div>
        <div className="shrink-0 rounded-xl border bg-background p-3">
            <label htmlFor="corruption-mode" className="text-sm font-medium">Corruption mode</label>
            <select id="corruption-mode" value={chosen ?? ""} onChange={e => setMode(e.target.value)} disabled={!options.length || busy || data?.running} className="mt-2 w-full rounded-md border bg-background px-3 py-2 text-sm">
                {!options.length && <option value="">Loading modes…</option>}
                {options.map(m => <option key={m.id} value={m.id}>{m.label}</option>)}
            </select>
            <div className="mt-3">
                <div className="flex items-center justify-between text-sm">
                    <label htmlFor="step-interval" className="font-medium">Step interval</label>
                    <output htmlFor="step-interval" className="tabular-nums">{intervalMs} ms</output>
                </div>
                <input id="step-interval" type="range" min={50} max={2000} step={50} value={intervalMs} onChange={event => setInterval(Number(event.target.value))} disabled={busy || data?.running} className="mt-2 w-full accent-teal-600" aria-valuetext={`${intervalMs} milliseconds per step`} />
                <div className="flex justify-between text-xs text-muted-foreground"><span>50 ms · Faster</span><span>2000 ms · Slower</span></div>
            </div>
            <div className="mt-4 flex gap-2">
                <Button className="flex-1" disabled={!chosen || busy || data?.running} onClick={() => start.mutate()}>{start.isPending ? "Starting…" : "Start"}</Button>
                {data?.run_id && !data.running && !data.error ? <Button variant="outline" className="flex-1" disabled={busy} onClick={() => resume.mutate()}>{resume.isPending ? "Resuming…" : "Resume"}</Button> :
                <Button variant="outline" className="flex-1" disabled={!data?.running || busy} onClick={() => stop.mutate()}>{stop.isPending ? "Stopping…" : "Stop"}</Button>}
            </div>
            {data?.mode && <p className="mt-2 text-xs text-muted-foreground">Active mode: {options.find(m => m.id === data.mode)?.label}</p>}
        </div>
        {(modes.isError || simulation.isError || start.isError || stop.isError || resume.isError || data?.error) && <p role="alert" className="rounded-lg border border-destructive p-3 text-sm text-destructive">{data?.error ?? (resume.isError ? "Could not resume the simulation. Try again." : stop.isError ? "Could not stop the simulation. Try again." : start.isError ? "Could not start the simulation. Check the data and backend." : "Could not load simulation data.")}</p>}
        <LaserMap key={data?.run_id ?? "idle"} states={data?.states ?? []} selected={inspected?.state ?? null} />
        <div className="flex shrink-0 items-center justify-between"><h3 className="text-sm font-semibold">States · {data?.running ? "LIVE" : data?.run_id ? "Stopped" : "Idle"}</h3>{selected !== null && <button onClick={() => setSelection(null)} className="text-xs underline">Clear selection</button>}</div>
        <p className="text-xs text-muted-foreground">Last 100 steps of the current run.</p>
        <div ref={listRef} onScroll={rememberPosition} className="min-h-0 flex-1 space-y-2 overflow-y-auto overscroll-contain [overflow-anchor:none]">
            {!data?.states.length && <p className="py-5 text-center text-sm text-muted-foreground">Press Start to receive states.</p>}
            {rows.map(s => <div key={`${data?.run_id}-${s.step}`} ref={selected === s.step ? selectedRowRef : undefined} className="rounded-lg border bg-background">
                <button className="flex w-full items-center justify-between p-3 text-sm" aria-expanded={selected === s.step} onClick={() => setSelection(selected === s.step ? null : { run: data!.run_id!, state: s })}><strong>{selected === s.step ? "▾" : "▸"} Step {s.step}</strong><span className="text-xs text-muted-foreground">{format((s.values.laser_power_w as Pair).measured)} W</span></button>
                {selected === s.step && <div className="overflow-x-auto border-t p-3"><table className="w-full text-xs"><thead><tr className="text-left text-muted-foreground"><th className="pb-2">Parameter</th><th>Commanded</th><th>Measured</th></tr></thead><tbody>{Object.entries(s.values).map(([key, value]) => <tr key={key} className="border-t"><td className="py-2 pr-2">{fields[key] ?? key}</td>{typeof value === "object" && value !== null ? <><td className="pr-2">{format(value.command)}</td><td>{format(value.measured)}</td></> : <><td className="pr-2 text-muted-foreground">—</td><td>{format(value)}</td></>}</tr>)}</tbody></table></div>}
            </div>)}
        </div>
    </aside>
}

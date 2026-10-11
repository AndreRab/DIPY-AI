import { useState } from "react"
import { ChatComponent } from "./components/chatComponent"
import { SimulationPanel } from "./components/simulationPanel"
import { Button } from "./components/ui/button"

const App = () => {
  const [showSimulation, setShowSimulation] = useState(false)
  return (
    <main className="flex min-h-dvh flex-col bg-muted/40 lg:h-dvh lg:overflow-hidden">
      <header className="flex shrink-0 justify-end border-b bg-background px-4 py-3">
        <Button variant="outline" aria-expanded={showSimulation} onClick={() => setShowSimulation(value => !value)}>
          {showSimulation ? "Hide simulation" : "Simulation"}
        </Button>
      </header>
      <div className={showSimulation ? "grid min-h-0 flex-1 lg:grid-cols-2 lg:overflow-hidden" : "min-h-0 flex-1 lg:overflow-hidden"}>
        <ChatComponent />
        <div className={showSimulation ? "h-[calc(100dvh-4rem)] min-h-0 min-w-0 border-t lg:h-full lg:border-t-0 lg:border-l" : "hidden"}><SimulationPanel /></div>
      </div>
    </main>
  )
}
export default App

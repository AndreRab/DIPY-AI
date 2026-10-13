import { useState } from "react"
import { ChatComponent } from "./components/chatComponent"
import { SimulationPanel } from "./components/simulationPanel"

const App = () => {
  const [showSimulation, setShowSimulation] = useState(false)
  return (
    <main className="flex min-h-dvh flex-col bg-muted/40 lg:h-dvh lg:overflow-hidden">
      <div className={showSimulation ? "grid min-h-0 flex-1 lg:grid-cols-2 lg:overflow-hidden" : "min-h-0 flex-1 lg:overflow-hidden"}>
        <ChatComponent showSimulation={showSimulation} onToggleSimulation={() => setShowSimulation(value => !value)} />
        <div className={showSimulation ? "h-dvh min-h-0 min-w-0 border-t lg:h-full lg:border-t-0 lg:border-l" : "hidden"}><SimulationPanel /></div>
      </div>
    </main>
  )
}
export default App

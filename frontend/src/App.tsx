import { OperatorButtons } from "./components/operatorButtons"
import { Button } from "./components/ui/button"

const App = () => {
  return (
    <main>
      <Button className="p-3 m-3" onClick={() => {
        console.log("Start Simulation")
      }}>
        Start Simulation
      </Button>
    </main>
  )
}

export default App

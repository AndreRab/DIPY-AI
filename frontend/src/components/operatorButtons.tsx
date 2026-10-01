import { useRef } from "react"
import { Button } from "./ui/button"
// TODO , temporary placeholder for the operator buttons
export const OperatorButtons = () => {
    const inputRef = useRef<HTMLInputElement>(null)
    
    return (
        <main>
            <div>
                <input type="text" placeholder="Enter the text" ref={inputRef}/>
                <Button>Ask AI bot</Button>
            </div>
        </main>
    )
}
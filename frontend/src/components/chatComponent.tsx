import invokeAgent, { type AgentResponse } from "@/agent/agent"
import { Button } from "@/components/ui/button"
import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { useMutation } from "@tanstack/react-query"
import { Bot, LoaderCircle, SendHorizontal, User } from "lucide-react"
import { useEffect, useRef, useState } from "react"
import Markdown from "react-markdown"
import remarkGfm from "remark-gfm"

interface conversation {
    id: number
    prompt: string
    response?: string
}

interface ChatComponentProps {
    showSimulation: boolean
    onToggleSimulation: () => void
}

export const ChatComponent = ({ showSimulation, onToggleSimulation }: ChatComponentProps) => {
    const [prompts, setPrompts] = useState<conversation[]>([])
    const mutation = useMutation({
        mutationFn: invokeAgent,
        onSuccess: (data: AgentResponse) => {
            console.log(data)
        },
        onError: (error: Error) => {
            console.error(error)
        }
    })
    const charValue = useRef<HTMLInputElement>(null)
    const bottomRef = useRef<HTMLDivElement>(null)
    const nextMessageId = useRef(0)

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" })
    }, [prompts, mutation.isPending])

    const send = () => {
        const text = charValue.current?.value.trim() ?? ""
        if (!text || mutation.isPending) return
        const id = nextMessageId.current++
        setPrompts((prev) => [...prev, { id, prompt: text }])
        if (charValue.current) charValue.current.value = ""
        mutation.mutate(text, {
            onSuccess: (data) => {
                setPrompts((prev) => prev.map((item) =>
                    item.id === id ? { ...item, response: data.response } : item
                ))
            },
        })
    }

    const handleEnter = (event: React.KeyboardEvent<HTMLInputElement>) => {
        if (event.key === "Enter") {
            event.preventDefault()
            send()
        }
    }

    return (
        <section className="flex h-dvh min-h-0 min-w-0 p-4 lg:h-full">
            <Card className="flex h-full min-h-0 w-full flex-col overflow-hidden shadow-sm">
                <CardHeader className="shrink-0 border-b">
                    <div className="flex items-center justify-between gap-3">
                        <div className="flex min-w-0 items-center gap-3">
                            <div className="flex size-9 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground">
                                <Bot className="size-5" />
                            </div>
                            <div className="min-w-0">
                                <CardTitle className="text-lg">Chat with the AI</CardTitle>
                                <CardDescription>Ask about the current state of the process.</CardDescription>
                            </div>
                        </div>
                        <Button className="shrink-0" variant="outline" aria-expanded={showSimulation} onClick={onToggleSimulation}>
                            {showSimulation ? "Hide simulation" : "Simulation"}
                        </Button>
                    </div>
                </CardHeader>

                <CardContent className="flex min-h-0 flex-1 flex-col gap-4 overflow-y-auto overscroll-contain">
                    {prompts.length === 0 && !mutation.isPending && (
                        <p className="m-auto text-center text-sm text-muted-foreground">
                            Type a question below and press Enter.
                        </p>
                    )}

                    {prompts.map((item) => (
                        <div key={item.id} className="flex flex-col gap-3">
                            <div className="flex items-start justify-end gap-2">
                                <div className="max-w-[80%] rounded-2xl rounded-tr-sm bg-primary px-4 py-2 text-sm text-primary-foreground">
                                    {item.prompt}
                                </div>
                                <div className="flex size-7 shrink-0 items-center justify-center rounded-full bg-muted">
                                    <User className="size-4" />
                                </div>
                            </div>
                            {item.response !== undefined && <div className="flex items-start gap-2">
                                <div className="flex size-7 shrink-0 items-center justify-center rounded-full bg-muted">
                                    <Bot className="size-4" />
                                </div>
                                <div className="chat-markdown min-w-0 max-w-[90%] rounded-2xl rounded-tl-sm bg-muted px-4 py-2 text-sm">
                                    <Markdown
                                        remarkPlugins={[remarkGfm]}
                                        components={{
                                            table: ({ children }) => (
                                                <div className="overflow-x-auto">
                                                    <table>{children}</table>
                                                </div>
                                            ),
                                        }}
                                    >
                                        {item.response}
                                    </Markdown>
                                </div>
                            </div>}
                        </div>
                    ))}

                    {mutation.isPending && (
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                            <div className="flex size-7 shrink-0 items-center justify-center rounded-full bg-muted">
                                <Bot className="size-4" />
                            </div>
                            <LoaderCircle className="size-4 animate-spin" />
                            Thinking...
                        </div>
                    )}

                    {mutation.isError && (
                        <div className="rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-2 text-sm text-destructive">
                            Could not reach the agent. Check that the backend is running.
                        </div>
                    )}

                    <div ref={bottomRef} />
                </CardContent>

                <CardFooter className="shrink-0 gap-2 border-t bg-muted/30 py-4">
                    <Input
                        type="text"
                        placeholder="Enter the text"
                        ref={charValue}
                        onKeyDown={handleEnter}
                        disabled={mutation.isPending}
                        className="h-9 bg-background"
                    />
                    <Button onClick={send} disabled={mutation.isPending} size="lg">
                        <SendHorizontal data-icon="inline-start" />
                        Send
                    </Button>
                </CardFooter>
            </Card>
        </section>
    )
}

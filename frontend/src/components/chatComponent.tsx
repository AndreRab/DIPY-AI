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
import { useRef } from "react"

export const ChatComponent = () => {
    const mutation = useMutation({
        mutationFn: invokeAgent,
        onSuccess: (data : AgentResponse) => {
            console.log(data)
        },
        onError: (error : Error) => {
            console.error(error)
        }
    })
    const charValue = useRef<HTMLInputElement>(null)

    const send = () => {
        const text = charValue.current?.value.trim() ?? ''
        if (!text || mutation.isPending) return
        mutation.mutate(text)
        if (charValue.current) charValue.current.value = ''
    }

    const handleEnter = (event: React.KeyboardEvent<HTMLInputElement>) => {
        if (event.key === 'Enter') {
            event.preventDefault()
            send()
        }
    }

    return (
        <section className="flex min-h-svh items-center justify-center bg-muted/40 p-4">
            <Card className="w-full max-w-2xl shadow-sm m-auto">
                <CardHeader className="border-b">
                    <div className="flex items-center gap-3">
                        <div className="flex size-9 items-center justify-center rounded-full bg-primary text-primary-foreground">
                            <Bot className="size-5" />
                        </div>
                        <div>
                            <CardTitle className="text-lg">Chat with the AI</CardTitle>
                            <CardDescription>Ask about the current state of the process.</CardDescription>
                        </div>
                    </div>
                </CardHeader>

                <CardContent className="flex min-h-64 flex-col gap-4">
                    {!mutation.variables && (
                        <p className="m-auto text-center text-sm text-muted-foreground">
                            Type a question below and press Enter.
                        </p>
                    )}

                    {mutation.variables && (
                        <div className="flex items-start justify-end gap-2">
                            <div className="max-w-[80%] rounded-2xl rounded-tr-sm bg-primary px-4 py-2 text-sm text-primary-foreground">
                                {mutation.variables}
                            </div>
                            <div className="flex size-7 shrink-0 items-center justify-center rounded-full bg-muted">
                                <User className="size-4" />
                            </div>
                        </div>
                    )}

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

                    {mutation.data && !mutation.isPending && (
                        <div className="flex items-start gap-2">
                            <div className="flex size-7 shrink-0 items-center justify-center rounded-full bg-muted">
                                <Bot className="size-4" />
                            </div>
                            <div className="max-w-[80%] whitespace-pre-wrap rounded-2xl rounded-tl-sm bg-muted px-4 py-2 text-sm">
                                {mutation.data.response}
                            </div>
                        </div>
                    )}
                </CardContent>

                <CardFooter className="gap-2 border-t bg-muted/30 py-4">
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

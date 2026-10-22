import invokeAgent from "@/agent/agent"
import { ConversationHistory } from "@/components/conversationHistory"
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
import { getMessages, type ConversationMessage } from "@/db/conversation"
import { skipToken, useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Bot, History, LoaderCircle, SendHorizontal, User } from "lucide-react"
import { useEffect, useRef, useState } from "react"
import Markdown from "react-markdown"
import remarkGfm from "remark-gfm"

interface ChatComponentProps {
    showSimulation: boolean
    onToggleSimulation: () => void
}

export const ChatComponent = ({ showSimulation, onToggleSimulation }: ChatComponentProps) => {
    const [activeConversationId, setActiveConversationId] = useState<number | null>(null)
    const [showHistory, setShowHistory] = useState(() => window.matchMedia("(min-width: 768px)").matches)
    const client = useQueryClient()
    const messagesQuery = useQuery({
        queryKey: ["conversation-messages", activeConversationId],
        queryFn: activeConversationId === null ? skipToken : ({ signal }) => getMessages(activeConversationId, signal),
    })
    const mutation = useMutation({
        mutationFn: invokeAgent,
        retry: false,
        onMutate: async (request) => {
            await client.cancelQueries({ queryKey: ["conversation-messages", request.conversation_id ?? null] })
        },
        onSuccess: (data, request) => {
            client.setQueryData<ConversationMessage[]>(["conversation-messages", data.conversation_id], previous => [
                ...(previous ?? []),
                { role: "user", content: request.prompt },
                { role: "assistant", content: data.response },
            ])
            setActiveConversationId(data.conversation_id)
            void client.invalidateQueries({ queryKey: ["conversations"] })
        },
    })
    const charValue = useRef<HTMLInputElement>(null)
    const bottomRef = useRef<HTMLDivElement>(null)
    const savedMessages = messagesQuery.data ?? []
    const unsavedPrompt = mutation.isPending || mutation.isError ? mutation.variables?.prompt : undefined
    const messages: ConversationMessage[] = unsavedPrompt !== undefined
        ? [...savedMessages, { role: "user", content: unsavedPrompt }]
        : savedMessages
    const isLoadingMessages = activeConversationId !== null && messagesQuery.isPending
    const cannotSend = mutation.isPending || isLoadingMessages || messagesQuery.isError

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" })
    }, [activeConversationId, messages.length, mutation.status])

    const selectConversation = (id: number | null) => {
        if (mutation.isPending) return
        setActiveConversationId(id)
        mutation.reset()
        if (charValue.current) charValue.current.value = ""
        if (!window.matchMedia("(min-width: 768px)").matches) setShowHistory(false)
    }

    const send = () => {
        const text = charValue.current?.value.trim() ?? ""
        if (!text || cannotSend) return
        if (charValue.current) charValue.current.value = ""
        mutation.mutate({ prompt: text, conversation_id: activeConversationId ?? undefined })
    }

    const handleEnter = (event: React.KeyboardEvent<HTMLInputElement>) => {
        if (event.key === "Enter" && !event.nativeEvent.isComposing) {
            event.preventDefault()
            send()
        }
    }

    return (
        <section className="flex h-dvh min-h-0 min-w-0 p-4 lg:h-full">
            <Card className="flex h-full min-h-0 w-full flex-col gap-0 overflow-hidden shadow-sm">
                <CardHeader className="shrink-0 border-b pb-4">
                    <div className="flex flex-wrap items-center justify-between gap-3">
                        <div className="flex min-w-0 items-center gap-3">
                            <div className="flex size-9 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground">
                                <Bot className="size-5" />
                            </div>
                            <div className="min-w-0">
                                <CardTitle className="text-lg">Chat with the AI</CardTitle>
                                <CardDescription>Ask about the current state of the process.</CardDescription>
                            </div>
                        </div>
                        <div className="flex items-center gap-2">
                            <Button variant="outline" aria-label="Toggle conversation history" aria-controls="conversation-history" aria-expanded={showHistory} onClick={() => setShowHistory(value => !value)}>
                                <History />
                                History
                            </Button>
                            <Button variant="outline" aria-expanded={showSimulation} onClick={onToggleSimulation}>
                                {showSimulation ? "Hide simulation" : "Simulation"}
                            </Button>
                        </div>
                    </div>
                </CardHeader>

                <div className="flex min-h-0 flex-1 flex-col md:flex-row">
                    {showHistory && <ConversationHistory activeConversationId={activeConversationId} disabled={mutation.isPending} onSelect={selectConversation} onDelete={id => { if (id === activeConversationId) selectConversation(null) }} />}
                    <div className="flex min-h-0 min-w-0 flex-1 flex-col">
                        <CardContent aria-busy={isLoadingMessages || mutation.isPending} className="flex min-h-0 flex-1 flex-col gap-4 overflow-y-auto overscroll-contain py-4">
                            {isLoadingMessages ? (
                                <p role="status" className="m-auto flex items-center gap-2 text-sm text-muted-foreground"><LoaderCircle className="size-4 animate-spin" /> Loading conversation...</p>
                            ) : messagesQuery.isError ? (
                                <div role="alert" className="m-auto text-center text-sm text-muted-foreground">
                                    <p>Could not load this conversation.</p>
                                    <Button variant="link" onClick={() => void messagesQuery.refetch()}>Try again</Button>
                                </div>
                            ) : messages.length === 0 && (
                                <p className="m-auto text-center text-sm text-muted-foreground">
                                    Type a question below and press Enter.
                                </p>
                            )}

                            {messages.map((message, index) => (
                                <div key={index} className={`flex items-start gap-2 ${message.role === "user" ? "justify-end" : ""}`}>
                                    {message.role === "assistant" && <div className="flex size-7 shrink-0 items-center justify-center rounded-full bg-muted"><Bot className="size-4" /></div>}
                                    {message.role === "user" ? (
                                        <div className="max-w-[80%] rounded-2xl rounded-tr-sm bg-primary px-4 py-2 text-sm break-words whitespace-pre-wrap text-primary-foreground">{message.content}</div>
                                    ) : (
                                        <div className="chat-markdown min-w-0 max-w-[90%] rounded-2xl rounded-tl-sm bg-muted px-4 py-2 text-sm">
                                            <Markdown remarkPlugins={[remarkGfm]} components={{
                                                table: ({ children }) => <div className="overflow-x-auto"><table>{children}</table></div>,
                                            }}>
                                                {message.content}
                                            </Markdown>
                                        </div>
                                    )}
                                    {message.role === "user" && <div className="flex size-7 shrink-0 items-center justify-center rounded-full bg-muted"><User className="size-4" /></div>}
                                </div>
                            ))}

                            {mutation.isPending && (
                                <div role="status" className="flex items-center gap-2 text-sm text-muted-foreground">
                                    <div className="flex size-7 shrink-0 items-center justify-center rounded-full bg-muted"><Bot className="size-4" /></div>
                                    <LoaderCircle className="size-4 animate-spin" /> Thinking...
                                </div>
                            )}

                            {mutation.isError && (
                                <div role="alert" className="rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-2 text-sm text-destructive">
                                    <p>Could not get a response. Please try again.</p>
                                    <Button variant="link" size="sm" className="px-0 text-destructive" onClick={() => mutation.variables && mutation.mutate(mutation.variables)}>Try again</Button>
                                </div>
                            )}

                            <div ref={bottomRef} />
                        </CardContent>

                        <CardFooter className="shrink-0 gap-2 border-t bg-muted/30 py-4">
                            <Input
                                type="text"
                                placeholder="Enter the text"
                                aria-label="Message"
                                maxLength={1000}
                                ref={charValue}
                                onKeyDown={handleEnter}
                                disabled={cannotSend}
                                className="h-9 bg-background"
                            />
                            <Button onClick={send} disabled={cannotSend} size="lg">
                                <SendHorizontal data-icon="inline-start" /> Send
                            </Button>
                        </CardFooter>
                    </div>
                </div>
            </Card>
        </section>
    )
}

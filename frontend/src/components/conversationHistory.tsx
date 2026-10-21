import { Button } from '@/components/ui/button'
import { getConversations } from '@/db/conversation'
import { useQuery } from '@tanstack/react-query'
import { LoaderCircle, MessageSquare, Plus } from 'lucide-react'

interface ConversationHistoryProps {
    activeConversationId: number | null
    disabled: boolean
    onSelect: (id: number | null) => void
}

export const ConversationHistory = ({ activeConversationId, disabled, onSelect }: ConversationHistoryProps) => {
    const { data: conversations = [], isPending, isError, refetch } = useQuery({
        queryKey: ['conversations'],
        queryFn: ({ signal }) => getConversations(signal),
    })

    return (
        <aside id="conversation-history" aria-label="Conversation history" className="flex max-h-52 shrink-0 flex-col gap-3 border-b bg-muted/20 p-3 md:max-h-none md:w-56 md:border-r md:border-b-0">
            <div className="flex items-center justify-between gap-2">
                <h2 className="text-sm font-medium">Conversations</h2>
                <Button variant="ghost" size="sm" onClick={() => onSelect(null)} disabled={disabled}>
                    <Plus /> New chat
                </Button>
            </div>
            <nav aria-label="Saved conversations" className="min-h-0 space-y-1 overflow-y-auto overscroll-contain">
                {isPending && <p role="status" className="flex items-center gap-2 px-2 py-3 text-xs text-muted-foreground"><LoaderCircle className="size-3 animate-spin" /> Loading...</p>}
                {isError ? (
                    <div role="alert" className="px-2 py-3 text-xs text-muted-foreground">
                        <p>Could not load conversations.</p>
                        <Button variant="link" size="sm" className="px-0" onClick={() => void refetch()}>Try again</Button>
                    </div>
                ) : !isPending && conversations.length === 0 && (
                    <p className="px-2 py-3 text-xs text-muted-foreground">Your conversations will appear here after your first message.</p>
                )}
                {conversations.map(conversation => (
                    <Button
                        key={conversation.id}
                        variant={activeConversationId === conversation.id ? 'secondary' : 'ghost'}
                        className="h-auto w-full justify-start gap-2 py-2 text-left font-normal"
                        title={conversation.title}
                        aria-current={activeConversationId === conversation.id ? 'true' : undefined}
                        disabled={disabled}
                        onClick={() => onSelect(conversation.id)}
                    >
                        <MessageSquare className="size-3.5 text-muted-foreground" />
                        <span className="min-w-0 truncate">{conversation.title}</span>
                    </Button>
                ))}
            </nav>
        </aside>
    )
}

import { Button } from '@/components/ui/button'
import { deleteConversation, getConversations } from '@/db/conversation'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { LoaderCircle, MessageSquare, Plus, Trash2 } from 'lucide-react'

interface ConversationHistoryProps {
    activeConversationId: number | null
    disabled: boolean
    onSelect: (id: number | null) => void
    onDelete: (id: number) => void
}

export const ConversationHistory = ({ activeConversationId, disabled, onSelect, onDelete }: ConversationHistoryProps) => {
    const { data: conversations = [], isPending, isError, refetch } = useQuery({
        queryKey: ['conversations'],
        queryFn: ({ signal }) => getConversations(signal),
    })

    const client = useQueryClient()
    const deletion = useMutation({
        mutationFn: deleteConversation,
        onSuccess: async (_, id) => {
            onDelete(id)
            await client.cancelQueries({ queryKey: ['conversation-messages', id] })
            client.removeQueries({ queryKey: ['conversation-messages', id] })
            await client.invalidateQueries({ queryKey: ['conversations'] })
        },
    })
    const controlsDisabled = disabled || deletion.isPending

    return (
        <aside id="conversation-history" aria-label="Conversation history" className="flex max-h-52 shrink-0 flex-col gap-3 border-b bg-muted/20 p-3 md:max-h-none md:w-56 md:border-r md:border-b-0">
            <div className="flex items-center justify-between gap-2">
                <h2 className="text-sm font-medium">Conversations</h2>
                <Button variant="ghost" size="sm" onClick={() => onSelect(null)} disabled={controlsDisabled}>
                    <Plus /> New chat
                </Button>
            </div>
            {deletion.isError && <p role="alert" className="px-2 text-xs text-destructive">Could not delete the conversation. Please try again.</p>}
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
                    <div key={conversation.id} className="flex items-center gap-1">
                    <Button
                        variant={activeConversationId === conversation.id ? 'secondary' : 'ghost'}
                        className="h-auto min-w-0 flex-1 justify-start gap-2 py-2 text-left font-normal"
                        title={conversation.title}
                        aria-current={activeConversationId === conversation.id ? 'true' : undefined}
                        disabled={controlsDisabled}
                        onClick={() => onSelect(conversation.id)}
                    >
                        <MessageSquare className="size-3.5 text-muted-foreground" />
                        <span className="min-w-0 truncate">{conversation.title}</span>
                    </Button>
                    <Button
                        variant="ghost"
                        size="icon-sm"
                        aria-label={`Delete conversation: ${conversation.title}`}
                        title="Delete conversation"
                        disabled={controlsDisabled}
                        onClick={() => {
                            if (window.confirm(`Delete "${conversation.title}" and all its messages? This cannot be undone.`)) {
                                deletion.mutate(conversation.id)
                            }
                        }}
                    >
                        {deletion.isPending && deletion.variables === conversation.id
                            ? <LoaderCircle className="size-3.5 animate-spin" />
                            : <Trash2 className="size-3.5" />}
                    </Button>
                    </div>
                ))}
            </nav>
        </aside>
    )
}

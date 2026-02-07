import { useState, useRef, useEffect, useMemo, useCallback } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import {
  MessageSquare,
  Send,
  Plus,
  Trash2,
  Moon,
  Sparkles,
  ExternalLink,
  PanelLeftClose,
  PanelLeft,
  Bot,
  User,
  Clock,
  ImagePlus,
  X,
} from 'lucide-react'
import { chatApi, ChatMessage, DreamSource } from '@/lib/api'
import { PageTitle, Button, Spinner } from '@/components/ui'
import { cn } from '@/lib/utils'

interface ChatImageAttachment {
  file: File
  preview: string
}

function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onloadend = () => {
      const dataUrl = reader.result as string
      resolve(dataUrl.split(',')[1])
    }
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

export function ChatPage() {
  const [selectedChatId, setSelectedChatId] = useState<number | null>(null)
  const [input, setInput] = useState('')
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [attachedImages, setAttachedImages] = useState<ChatImageAttachment[]>([])
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const imageInputRef = useRef<HTMLInputElement>(null)
  const queryClient = useQueryClient()

  // Fetch chat list
  const { data: chatsData, isLoading: chatsLoading } = useQuery({
    queryKey: ['chats'],
    queryFn: () => chatApi.list().then((r) => r.data),
  })

  // Fetch selected chat messages
  const { data: selectedChat, isLoading: messagesLoading } = useQuery({
    queryKey: ['chat', selectedChatId],
    queryFn: () => chatApi.get(selectedChatId!).then((r) => r.data),
    enabled: !!selectedChatId,
  })

  // Create new chat
  const createChatMutation = useMutation({
    mutationFn: () => chatApi.create(),
    onSuccess: (response) => {
      queryClient.invalidateQueries({ queryKey: ['chats'] })
      setSelectedChatId(response.data.id)
    },
  })

  // Send message
  const sendMessageMutation = useMutation({
    mutationFn: async ({ chatId, content, images }: { chatId: number; content: string; images?: ChatImageAttachment[] }) => {
      let encodedImages: { base64: string; mime_type: string }[] | undefined
      if (images && images.length > 0) {
        encodedImages = await Promise.all(
          images.map(async (img) => ({
            base64: await fileToBase64(img.file),
            mime_type: img.file.type,
          }))
        )
      }
      return chatApi.sendMessage(chatId, content, true, encodedImages)
    },
    onMutate: async ({ chatId, content }) => {
      // Cancel outgoing refetches so they don't overwrite our optimistic update
      await queryClient.cancelQueries({ queryKey: ['chat', chatId] })

      const previous = queryClient.getQueryData(['chat', chatId])

      // Optimistically add the user message
      queryClient.setQueryData(['chat', chatId], (old: any) => {
        if (!old) return old
        return {
          ...old,
          messages: [
            ...old.messages,
            {
              id: Date.now(),
              role: 'user' as const,
              content,
              sources: [],
              query_type: null,
              processing_time_ms: null,
              created_at: new Date().toISOString(),
            },
          ],
        }
      })

      setInput('')
      attachedImages.forEach((img) => URL.revokeObjectURL(img.preview))
      setAttachedImages([])

      return { previous, chatId }
    },
    onSuccess: (_, { chatId }) => {
      queryClient.invalidateQueries({ queryKey: ['chat', chatId] })
      queryClient.invalidateQueries({ queryKey: ['chats'] })
    },
    onError: (_err, _vars, context) => {
      // Roll back on error
      if (context?.previous) {
        queryClient.setQueryData(['chat', context.chatId], context.previous)
      }
    },
  })

  // Delete chat
  const deleteChatMutation = useMutation({
    mutationFn: (chatId: number) => chatApi.delete(chatId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['chats'] })
      setSelectedChatId(null)
    },
  })

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [selectedChat?.messages])

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = Math.max(44, Math.min(textareaRef.current.scrollHeight, 150)) + 'px'
    }
  }, [input])

  const handleSend = () => {
    if ((!input.trim() && attachedImages.length === 0) || !selectedChatId) return
    const content = input.trim() || 'Please analyze these images.'
    sendMessageMutation.mutate({ chatId: selectedChatId, content, images: attachedImages.length > 0 ? attachedImages : undefined })
  }

  const handleImageAttach = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (!files) return
    const newImages: ChatImageAttachment[] = []
    for (const file of Array.from(files)) {
      if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) continue
      if (file.size > 20 * 1024 * 1024) continue
      if (attachedImages.length + newImages.length >= 3) break
      newImages.push({ file, preview: URL.createObjectURL(file) })
    }
    setAttachedImages((prev) => [...prev, ...newImages])
    e.target.value = ''
  }, [attachedImages.length])

  const removeAttachedImage = useCallback((index: number) => {
    setAttachedImages((prev) => {
      const updated = [...prev]
      URL.revokeObjectURL(updated[index].preview)
      updated.splice(index, 1)
      return updated
    })
  }, [])

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex h-full overflow-hidden">
      <PageTitle>Chat</PageTitle>

      {/* Collapsible Sidebar */}
      <div
        className={cn(
          'border-r border-border bg-surface flex flex-col transition-all duration-300 ease-in-out',
          sidebarOpen ? 'w-72' : 'w-0'
        )}
      >
        <div className={cn('flex flex-col h-full', sidebarOpen ? 'opacity-100' : 'opacity-0 pointer-events-none')}>
          {/* New Chat Button */}
          <div className="p-3 border-b border-border">
            <Button
              onClick={() => createChatMutation.mutate()}
              isLoading={createChatMutation.isPending}
              className="w-full"
              variant="secondary"
            >
              <Plus className="w-4 h-4 mr-2" />
              New Chat
            </Button>
          </div>

          {/* Chat List */}
          <div className="flex-1 overflow-y-auto p-2">
            {chatsLoading ? (
              <div className="flex justify-center py-8">
                <Spinner />
              </div>
            ) : chatsData?.data && chatsData.data.length > 0 ? (
              <div className="space-y-1">
                {chatsData.data.map((chat) => (
                  <button
                    key={chat.id}
                    onClick={() => setSelectedChatId(chat.id)}
                    className={cn(
                      'w-full text-left p-3 rounded-lg transition-all group',
                      selectedChatId === chat.id
                        ? 'bg-accent/10 border border-accent/30'
                        : 'hover:bg-surface-2 border border-transparent'
                    )}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <div className={cn(
                          'font-medium truncate text-sm',
                          selectedChatId === chat.id ? 'text-accent' : 'text-foreground'
                        )}>
                          {chat.name}
                        </div>
                        <div className="text-xs text-muted flex items-center gap-1.5 mt-1">
                          <MessageSquare className="w-3 h-3" />
                          {chat.message_count} messages
                        </div>
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          if (confirm('Delete this chat?')) {
                            deleteChatMutation.mutate(chat.id)
                          }
                        }}
                        className="opacity-0 group-hover:opacity-100 text-muted hover:text-danger p-1 transition-opacity"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </button>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-muted text-sm">
                <MessageSquare className="w-8 h-8 mx-auto mb-2 opacity-50" />
                No chats yet
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <div className="h-14 border-b border-border flex items-center px-4 gap-3 bg-surface/50 backdrop-blur-sm">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 hover:bg-surface-2 rounded-lg transition-colors text-muted hover:text-foreground"
            title={sidebarOpen ? 'Hide sidebar' : 'Show sidebar'}
          >
            {sidebarOpen ? (
              <PanelLeftClose className="w-5 h-5" />
            ) : (
              <PanelLeft className="w-5 h-5" />
            )}
          </button>

          {selectedChat && (
            <div className="flex items-center gap-2">
              <Bot className="w-5 h-5 text-accent" />
              <span className="font-medium text-foreground">{selectedChat.name}</span>
            </div>
          )}
        </div>

        {selectedChatId ? (
          <>
            {/* Messages */}
            <div className="flex-1 overflow-y-auto">
              <div className="max-w-3xl mx-auto p-6 space-y-6">
                {messagesLoading ? (
                  <div className="flex justify-center py-8">
                    <Spinner />
                  </div>
                ) : selectedChat?.messages && selectedChat.messages.length > 0 ? (
                  <>
                    {selectedChat.messages.map((message) => (
                      <ChatMessageBubble key={message.id} message={message} />
                    ))}
                    {sendMessageMutation.isPending && (
                      <div className="flex gap-4">
                        <div className="w-8 h-8 rounded-full bg-accent/10 flex items-center justify-center flex-shrink-0">
                          <Bot className="w-4 h-4 text-accent" />
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 text-muted">
                            <div className="flex gap-1">
                              <span className="w-2 h-2 bg-accent/60 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                              <span className="w-2 h-2 bg-accent/60 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                              <span className="w-2 h-2 bg-accent/60 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                            </div>
                            <span className="text-sm">Querying your dream knowledge base can take up some time, please wait...</span>
                          </div>
                        </div>
                      </div>
                    )}
                  </>
                ) : (
                  <div className="flex flex-col items-center justify-center py-16 text-center">
                    <div className="w-16 h-16 rounded-full bg-accent/10 flex items-center justify-center mb-4">
                      <Sparkles className="w-8 h-8 text-accent" />
                    </div>
                    <h3 className="text-lg font-medium text-foreground mb-2">Start exploring your dreams</h3>
                    <p className="text-muted max-w-md">
                      Ask about patterns, recurring symbols, emotions, or anything you'd like to understand about your dream journal.
                    </p>
                    <div className="flex flex-wrap gap-2 mt-6 justify-center">
                      {['What symbols appear most?', 'Show recurring themes', 'Analyze my emotions'].map((suggestion) => (
                        <button
                          key={suggestion}
                          onClick={() => setInput(suggestion)}
                          className="px-3 py-1.5 text-sm bg-surface-2 hover:bg-surface-2/80 rounded-full text-muted hover:text-foreground transition-colors"
                        >
                          {suggestion}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            </div>

            {/* Input */}
            <div className="border-t border-border bg-surface/80 backdrop-blur-sm">
              <div className="max-w-3xl mx-auto p-4">
                {/* Image previews */}
                {attachedImages.length > 0 && (
                  <div className="flex gap-2 mb-3">
                    {attachedImages.map((img, i) => (
                      <div key={i} className="relative group">
                        <img
                          src={img.preview}
                          alt={`Attachment ${i + 1}`}
                          className="w-16 h-16 object-cover rounded-lg border border-border"
                        />
                        <button
                          onClick={() => removeAttachedImage(i)}
                          className="absolute -top-1 -right-1 p-0.5 bg-black/70 rounded-full text-white opacity-0 group-hover:opacity-100 transition-opacity"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </div>
                    ))}
                  </div>
                )}
                <div className="flex gap-3 items-center">
                  <input
                    ref={imageInputRef}
                    type="file"
                    accept="image/jpeg,image/png,image/webp"
                    multiple
                    onChange={handleImageAttach}
                    className="hidden"
                  />
                  <button
                    onClick={() => imageInputRef.current?.click()}
                    disabled={sendMessageMutation.isPending || attachedImages.length >= 3}
                    className={cn(
                      'h-11 w-11 flex items-center justify-center rounded-xl border transition-colors flex-shrink-0',
                      attachedImages.length > 0
                        ? 'bg-accent/10 border-accent/30 text-accent'
                        : 'bg-surface-2 border-border text-muted hover:text-foreground hover:border-accent/30'
                    )}
                    title="Attach image"
                  >
                    <ImagePlus className="w-4 h-4" />
                  </button>
                  <div className="flex-1 relative">
                    <textarea
                      ref={textareaRef}
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      onKeyDown={handleKeyDown}
                      placeholder="Ask about your dreams..."
                      className="w-full px-4 py-2.5 min-h-[44px] bg-surface-2 border border-border rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-accent/50 focus:border-accent transition-all"
                      rows={1}
                      disabled={sendMessageMutation.isPending}
                    />
                  </div>
                  <Button
                    onClick={handleSend}
                    disabled={(!input.trim() && attachedImages.length === 0) || sendMessageMutation.isPending}
                    className="h-11 w-11 p-0 rounded-xl"
                  >
                    <Send className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center p-6">
            <div className="text-center max-w-md">
              <div className="w-20 h-20 rounded-full bg-gradient-to-br from-accent/20 to-purple-500/20 flex items-center justify-center mx-auto mb-6">
                <MessageSquare className="w-10 h-10 text-accent" />
              </div>
              <h2 className="text-2xl font-semibold text-foreground mb-3">Chat with your dreams</h2>
              <p className="text-muted mb-6">
                Start a conversation to explore patterns, symbols, and insights from your dream journal using AI analysis.
              </p>
              <Button onClick={() => createChatMutation.mutate()} size="lg">
                <Plus className="w-5 h-5 mr-2" />
                Start New Chat
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

// Markdown rendering component
function MarkdownContent({ content }: { content: string }) {
  const rendered = useMemo(() => {
    // Process the markdown content
    let html = content

    // Escape HTML
    html = html.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')

    // Bold (**text** or __text__)
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong class="font-semibold text-foreground">$1</strong>')
    html = html.replace(/__([^_]+)__/g, '<strong class="font-semibold text-foreground">$1</strong>')

    // Italic (*text* or _text_)
    html = html.replace(/\*([^*]+)\*/g, '<em class="italic">$1</em>')
    html = html.replace(/_([^_]+)_/g, '<em class="italic">$1</em>')

    // Headers
    html = html.replace(/^### (.+)$/gm, '<h3 class="text-lg font-semibold mt-4 mb-2 text-foreground">$1</h3>')
    html = html.replace(/^## (.+)$/gm, '<h2 class="text-xl font-semibold mt-4 mb-2 text-foreground">$1</h2>')
    html = html.replace(/^# (.+)$/gm, '<h1 class="text-2xl font-bold mt-4 mb-2 text-foreground">$1</h1>')

    // Unordered lists
    html = html.replace(/^[\s]*[-*•]\s+(.+)$/gm, '<li class="ml-4 list-disc">$1</li>')

    // Ordered lists
    html = html.replace(/^[\s]*(\d+)\.\s+(.+)$/gm, '<li class="ml-4 list-decimal">$2</li>')

    // Wrap consecutive list items
    html = html.replace(/(<li class="ml-4 list-disc">[\s\S]*?<\/li>)(\s*)(?=<li class="ml-4 list-disc">|$)/g, '$1$2')
    html = html.replace(/((?:<li class="ml-4 list-disc">[^<]*<\/li>\s*)+)/g, '<ul class="my-2 space-y-1">$1</ul>')
    html = html.replace(/((?:<li class="ml-4 list-decimal">[^<]*<\/li>\s*)+)/g, '<ol class="my-2 space-y-1">$1</ol>')

    // Links [text](url) - only allow http/https URLs to prevent javascript: XSS
    html = html.replace(/\[([^\]]+)\]\((https?:\/\/[^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer" class="text-accent hover:underline">$1</a>')

    // Blockquotes
    html = html.replace(/^>\s+(.+)$/gm, '<blockquote class="border-l-2 border-accent/50 pl-3 my-2 italic text-muted">$1</blockquote>')

    // Horizontal rules
    html = html.replace(/^---$/gm, '<hr class="my-4 border-border" />')

    // Line breaks (double newline = paragraph)
    html = html.replace(/\n\n/g, '</p><p class="mb-3">')

    // Single line breaks
    html = html.replace(/\n/g, '<br />')

    // Wrap in paragraph
    html = `<p class="mb-3">${html}</p>`

    // Clean up empty paragraphs
    html = html.replace(/<p class="mb-3"><\/p>/g, '')
    html = html.replace(/<p class="mb-3">(<(?:ul|ol|pre|blockquote|h[1-3]))/g, '$1')
    html = html.replace(/(<\/(?:ul|ol|pre|blockquote|h[1-3])>)<\/p>/g, '$1')

    return html
  }, [content])

  return (
    <div
      className="prose dark:prose-invert prose-sm max-w-none"
      dangerouslySetInnerHTML={{ __html: rendered }}
    />
  )
}

function ChatMessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === 'user'

  return (
    <div className={cn('flex gap-4', isUser ? 'flex-row-reverse' : 'flex-row')}>
      {/* Avatar */}
      <div className={cn(
        'w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0',
        isUser ? 'bg-accent' : 'bg-accent/10'
      )}>
        {isUser ? (
          <User className="w-4 h-4 text-white" />
        ) : (
          <Bot className="w-4 h-4 text-accent" />
        )}
      </div>

      {/* Message Content Container */}
      <div className={cn('flex-1 min-w-0', isUser ? 'flex flex-col items-end' : '')}>
        {/* Message Bubble */}
        <div
          className={cn(
            'rounded-2xl px-4 py-3 max-w-[85%]',
            isUser
              ? 'bg-accent text-white'
              : 'bg-surface-2 text-foreground'
          )}
        >
          {isUser ? (
            <p className="whitespace-pre-wrap">{message.content}</p>
          ) : (
            <MarkdownContent content={message.content} />
          )}

          {/* Sources - only for assistant */}
          {!isUser && message.sources && message.sources.length > 0 && (
            <div className="mt-4 pt-3 border-t border-border/30">
              <div className="text-xs text-muted mb-2 flex items-center gap-1.5">
                <Moon className="w-3.5 h-3.5" />
                Referenced Dreams
              </div>
              <div className="flex flex-wrap gap-2">
                {message.sources.map((source, i) => (
                  <SourceChip key={i} source={source} />
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Timestamp - moved inside the message content container */}
        {message.created_at && (
          <div className={cn(
            'text-xs text-muted mt-1 flex items-center gap-1',
            isUser ? 'self-end' : ''
          )}>
            <Clock className="w-3 h-3" />
            {new Date(message.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </div>
        )}
      </div>
    </div>
  )
}

function SourceChip({ source }: { source: DreamSource }) {
  return (
    <Link
      to={`/dreams/${source.dream_id}`}
      className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-accent/10 hover:bg-accent/20 rounded-full text-xs text-accent transition-colors"
    >
      <ExternalLink className="w-3 h-3" />
      {source.dream_title || `Dream #${source.dream_id}`}
    </Link>
  )
}

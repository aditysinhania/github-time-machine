import { useState, useRef, useEffect } from 'react'
import { Send, Bot } from 'lucide-react'
import { aiApi } from '@/api'
import type { ChatMessage } from '@/types/api'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'

interface ChatPanelProps {
  repoId: number
  repoName: string
}

const SUGGESTIONS = [
  'Who owns the auth module?',
  'What are the biggest risks?',
  'Summarize this repo in 3 sentences',
  'Who should review security changes?',
]

function renderMarkdown(text: string): string {
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/`(.*?)`/g, '<code class="bg-secondary px-1 py-0.5 rounded text-[11px]">$1</code>')
    .replace(/\n- /g, '<br>• ')
    .replace(/\n/g, '<br>')
}

export function ChatPanel({ repoId, repoName }: ChatPanelProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      content: `I've analyzed **${repoName}**. Ask me anything about ownership, risks, history, or recommendations.`,
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const endRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const send = async (text?: string) => {
    const q = (text ?? input).trim()
    if (!q || loading) return
    setInput('')

    const newHistory = [...messages, { role: 'user' as const, content: q }]
    setMessages(newHistory)
    setLoading(true)

    try {
      const response = await aiApi.chat(repoId, {
        message: q,
        history: messages, // prior turns, excluding the one we just added
      })
      setMessages([...newHistory, { role: 'assistant', content: response.answer }])
    } catch {
      setMessages([
        ...newHistory,
        { role: 'assistant', content: '⚠️ Could not reach the AI service. Please check your API key configuration.' },
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex h-full flex-col">
      <div className="flex-1 space-y-3 overflow-y-auto pb-3" style={{ maxHeight: 420 }}>
        {messages.map((m, i) => (
          <div key={i} className={`flex gap-2.5 ${m.role === 'user' ? 'flex-row-reverse' : ''}`}>
            {m.role === 'assistant' && (
              <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full border border-primary/40 bg-primary/20">
                <Bot className="h-3.5 w-3.5 text-primary" />
              </div>
            )}
            <div
              className={`max-w-[85%] rounded-xl px-3 py-2 text-[13px] leading-relaxed ${
                m.role === 'user'
                  ? 'rounded-tr-sm bg-secondary text-foreground'
                  : 'rounded-tl-sm border border-border bg-card text-foreground'
              }`}
              dangerouslySetInnerHTML={{ __html: renderMarkdown(m.content) }}
            />
          </div>
        ))}
        {loading && (
          <div className="flex gap-2.5">
            <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full border border-primary/40 bg-primary/20">
              <Bot className="h-3.5 w-3.5 text-primary" />
            </div>
            <div className="flex items-center gap-1.5 rounded-xl rounded-tl-sm border border-border bg-card px-3.5 py-2.5">
              {[0, 1, 2].map((i) => (
                <span
                  key={i}
                  className="h-1.5 w-1.5 animate-pulse rounded-full bg-primary"
                  style={{ animationDelay: `${i * 0.2}s` }}
                />
              ))}
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      <div className="border-t border-border pt-3">
        <div className="mb-2.5 flex flex-wrap gap-1.5">
          {SUGGESTIONS.map((s) => (
            <button
              key={s}
              onClick={() => send(s)}
              className="rounded-full border border-border bg-secondary/60 px-2.5 py-1 text-[11px] text-muted-foreground transition-colors hover:text-foreground"
            >
              {s}
            </button>
          ))}
        </div>
        <div className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && send()}
            placeholder="Ask anything about this repo..."
            className="text-[13px]"
          />
          <Button size="icon" onClick={() => send()} disabled={!input.trim() || loading}>
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  )
}

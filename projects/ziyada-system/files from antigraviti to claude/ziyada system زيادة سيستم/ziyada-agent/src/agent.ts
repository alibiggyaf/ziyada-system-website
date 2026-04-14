import { EventEmitter } from 'eventemitter3';

export interface Message {
  role: 'user' | 'assistant' | 'system' | 'tool';
  content: string | null;
  name?: string;
  tool_call_id?: string;
  tool_calls?: any[];
}

export interface AgentConfig {
  apiKey: string;
  model?: string;
  instructions?: string;
  tools?: any[];
}

export class Agent extends EventEmitter<any> {
  private messages: Message[] = [];
  private config: AgentConfig;

  constructor(config: AgentConfig) {
    super();
    this.config = config;
    if (config.instructions) {
      this.messages.push({ role: 'system', content: config.instructions });
    }
  }

  getMessages(): Message[] { return [...this.messages]; }

  async sendSync(content: string): Promise<string> {
    this.messages.push({ role: 'user', content });

    try {
      const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.config.apiKey}`,
          'Content-Type': 'application/json',
          'HTTP-Referer': 'https://ziyadasystem.local', // Required by OpenRouter rankers
          'X-Title': 'Ziyada System Agent' 
        },
        body: JSON.stringify({
          model: this.config.model ?? 'openrouter/auto',
          messages: this.messages,
          tools: this.config.tools && this.config.tools.length > 0 ? this.config.tools : undefined
        })
      });

      if (!response.ok) throw new Error(`OpenRouter error: ${response.statusText}`);
      
      const data = await response.json();
      const message = data.choices[0].message;
      this.messages.push(message);

      return message.content || "Tool executed (see history).";
    } catch (err: any) {
      throw new Error(err.message);
    }
  }
}

export function createAgent(config: AgentConfig): Agent {
  return new Agent(config);
}

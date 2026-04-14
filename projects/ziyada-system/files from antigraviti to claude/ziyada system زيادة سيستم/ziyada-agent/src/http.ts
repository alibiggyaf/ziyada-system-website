import express from 'express';
import { createAgent } from './agent.js';
import { ziyadaTools } from './tools.js';

const app = express();
app.use(express.json());

// Main endpoint for n8n to drop a lead payload into
app.post('/api/n8n/process-lead', async (req, res) => {
  const { leadData } = req.body;

  if (!process.env.OPENROUTER_API_KEY) {
     res.status(500).json({ success: false, error: 'Misconfigured: missing OPENROUTER_API_KEY' });
     return;
  }

  try {
    const agent = createAgent({
      apiKey: process.env.OPENROUTER_API_KEY,
      model: 'openrouter/auto', // Auto select best model
      instructions: `You are the AI Assistant for the Ziyada System. Analyze the incoming lead data: ${JSON.stringify(leadData)}. Evaluate the lead and call appropriate tools like saving the lead summary or requesting human handoff. Provide a drafted reply as your final response to send back via n8n.`,
      tools: ziyadaTools,
    });

    const response = await agent.sendSync("Process this lead and perform necessary tool calls. Ensure you summarize the lead and draft an email response.");
    
    // In n8n, this response payload will be available for downstream nodes (e.g. sending the drafting email via Gmail/Mailgun nodes)
    res.json({ success: true, text: response, history: agent.getMessages() });
  } catch (error: any) {
    res.status(500).json({ success: false, error: error.message });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Ziyada Agent HTTP API listening on port ${PORT}`);
});

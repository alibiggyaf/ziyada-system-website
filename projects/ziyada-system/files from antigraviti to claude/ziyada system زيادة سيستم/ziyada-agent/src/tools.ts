export const saveLeadSummaryTool = {
  type: "function",
  function: {
    name: "save_lead_summary",
    description: "Save the analyzed summary and qualification status of a lead to the Ziyada System database",
    parameters: {
      type: "object",
      properties: {
        leadName: { type: "string" },
        qualificationScore: { type: "number", description: "A score from 1-10 on how qualified this lead is" },
        summary: { type: "string", description: "A brief analysis of the lead needs" }
      },
      required: ["leadName", "qualificationScore", "summary"]
    }
  }
};

export const requestAgentHandoffTool = {
  type: "function",
  function: {
    name: "request_agent_handoff",
    description: "Request human assistance if the lead has a complex issue or requires immediate attention",
    parameters: {
      type: "object",
      properties: {
        reason: { type: "string", description: "Why human intervention is needed" }
      },
      required: ["reason"]
    }
  }
};

export const ziyadaTools = [saveLeadSummaryTool, requestAgentHandoffTool];

import { supabase } from "@/lib/supabase";

// ---------------------------------------------------------------------------
// Table-name mapping
// ---------------------------------------------------------------------------
const TABLE_MAP = {
  Lead: "leads",
  Booking: "bookings",
  BlogPost: "blog_posts",
  CaseStudy: "case_studies",
  Subscriber: "subscribers",
  FAQItem: "faq_items",
  Service: "services",
  CompetitorIntel: "competitor_intel",
  ContentSuggestion: "content_suggestions",
  AgentConversation: "agent_conversations",
  ContentCalendarBatch: "content_calendar_batches",
  ContentCalendarEntry: "content_calendar_entries",
};

// ---------------------------------------------------------------------------
// Sort-field mapping  (old Python API field -> Supabase column)
// ---------------------------------------------------------------------------
const SORT_FIELD_MAP = {
  created_date: "created_at",
  updated_date: "updated_at",
  published_date: "published_at",
};

/**
 * Parse a sort string such as "-created_date" into { column, ascending }.
 * A leading "-" means descending.  Falls back to created_at desc.
 */
const parseSort = (sort) => {
  if (!sort) return { column: "created_at", ascending: false };

  const descending = sort.startsWith("-");
  const raw = descending ? sort.slice(1) : sort;
  const column = SORT_FIELD_MAP[raw] || raw;

  return { column, ascending: !descending };
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Throw a readable error when a Supabase call fails. */
const throwIfError = (result) => {
  if (result.error) {
    throw new Error(result.error.message || "Supabase request failed");
  }
  return result.data;
};

// ---------------------------------------------------------------------------
// Entity client factory  (preserves the exact same external API)
// ---------------------------------------------------------------------------

/**
 * @param {string} entityName  Key in TABLE_MAP (e.g. "Lead")
 */
const createEntityClient = (entityName) => {
  const table = TABLE_MAP[entityName];
  if (!table) throw new Error(`Unknown entity: ${entityName}`);

  return {
    /**
     * list(sort?, limit?, skip?) -> array
     */
    list: async (sort, limit, skip) => {
      const { column, ascending } = parseSort(sort);
      const pageSize = limit ?? 100;
      const offset = skip ?? 0;

      const result = await supabase
        .from(table)
        .select("*")
        .order(column, { ascending })
        .range(offset, offset + pageSize - 1);

      return throwIfError(result);
    },

    /**
     * filter(criteria?, sort?, limit?, skip?) -> array
     */
    filter: async (criteria, sort, limit, skip) => {
      const { column, ascending } = parseSort(sort);
      const pageSize = limit ?? 100;
      const offset = skip ?? 0;

      let query = supabase.from(table).select("*");

      if (criteria && typeof criteria === "object") {
        for (const [key, value] of Object.entries(criteria)) {
          query = query.eq(key, value);
        }
      }

      query = query
        .order(column, { ascending })
        .range(offset, offset + pageSize - 1);

      const result = await query;
      return throwIfError(result);
    },

    /**
     * get(id) -> object
     */
    get: async (id) => {
      const result = await supabase
        .from(table)
        .select("*")
        .eq("id", id)
        .single();

      return throwIfError(result);
    },

    /**
     * create(payload?) -> object
     */
    create: async (payload) => {
      const result = await supabase
        .from(table)
        .insert(payload || {})
        .select()
        .single();

      return throwIfError(result);
    },

    /**
     * update(id, payload?) -> object
     */
    update: async (id, payload) => {
      const result = await supabase
        .from(table)
        .update(payload || {})
        .eq("id", id)
        .select()
        .single();

      return throwIfError(result);
    },

    /**
     * delete(id) -> void
     */
    delete: async (id) => {
      const result = await supabase.from(table).delete().eq("id", id);

      throwIfError(result);
    },
  };
};

// ---------------------------------------------------------------------------
// Function implementations
// ---------------------------------------------------------------------------

/**
 * Insert a new lead with normalized fields.
 */
const submitLead = async (payload) => {
  const record = {
    ...payload,
    status: "new",
    source: payload.source || "contact",
  };

  const result = await supabase
    .from("leads")
    .insert(record)
    .select()
    .single();

  return throwIfError(result);
};

/**
 * Upsert a subscriber. If the email already exists and the subscriber was
 * previously unsubscribed, reactivate them.
 */
const subscribeEmail = async (payload) => {
  const { email } = payload;
  if (!email) throw new Error("Email is required");

  const fallbackRecord = {
    email,
    name: payload.name || null,
    language: payload.language || "ar",
    status: "active",
  };

  try {
    const { data: existing } = await supabase
      .from("subscribers")
      .select("*")
      .eq("email", email)
      .maybeSingle();

    if (existing) {
      const result = await supabase
        .from("subscribers")
        .update({
          status: "active",
          language: payload.language || existing.language,
        })
        .eq("email", email)
        .select()
        .single();

      if (!result.error) {
        triggerHubSpotSync("subscriber", result.data);
        return { success: true, subscriber: result.data };
      }

      throw result.error;
    }

    const result = await supabase
      .from("subscribers")
      .insert(fallbackRecord)
      .select()
      .single();

    if (!result.error) {
      triggerHubSpotSync("subscriber", result.data);
      return { success: true, subscriber: result.data };
    }

    throw result.error;
  } catch (error) {
    // Production fallback: if RLS blocks browser writes, continue notification flow.
    const errMsg = (typeof error === "object" && error && "message" in error)
      ? String(error.message || "")
      : String(error || "");
    const msg = errMsg.toLowerCase();
    if (msg.includes("row-level security") || msg.includes("permission") || msg.includes("not allowed")) {
      triggerHubSpotSync("subscriber", fallbackRecord);
      return { success: true, subscriber: fallbackRecord, fallback: "n8n_only" };
    }
    throw error;
  }
};

/**
 * Book a meeting. Also creates a lead for the email if one doesn't exist.
 */
const bookMeeting = async (payload) => {
  const email = payload.lead_email || payload.email;
  const name = payload.lead_name || payload.name;

  if (email) {
    const { data: existingLead } = await supabase
      .from("leads")
      .select("id")
      .eq("email", email)
      .maybeSingle();

    if (!existingLead) {
      await supabase.from("leads").insert({
        email,
        name: name || null,
        company: payload.company || null,
        status: "new",
        source: "booking",
      });
    }
  }

  const booking = {
    ...payload,
    status: "pending",
  };

  const result = await supabase
    .from("bookings")
    .insert(booking)
    .select()
    .single();

  return throwIfError(result);
};

/**
 * Return available hourly slots for a given date (09:00 - 16:00).
 * Slots already booked are excluded.
 */
const getAvailableSlots = async (payload) => {
  const { date } = payload;
  if (!date) throw new Error("Date is required");

  const allSlots = [];
  for (let hour = 9; hour <= 16; hour++) {
    allSlots.push(`${String(hour).padStart(2, "0")}:00`);
  }

  const { data: bookings } = await supabase
    .from("bookings")
    .select("booking_time")
    .eq("booking_date", date)
    .neq("status", "cancelled");

  const bookedTimes = new Set(
    (bookings || []).map((b) => b.booking_time?.slice(0, 5)).filter(Boolean)
  );

  const slots = allSlots.filter((s) => !bookedTimes.has(s));

  return { slots };
};

/**
 * Receive a blog post payload (typically from an n8n webhook) and insert it.
 */
const n8nWebhook = async (payload) => {
  const result = await supabase
    .from("blog_posts")
    .insert(payload)
    .select()
    .single();

  return throwIfError(result);
};

// ---------------------------------------------------------------------------
// Competitor Intelligence webhook helpers
// ---------------------------------------------------------------------------

const N8N_BASE = import.meta.env.VITE_N8N_HOST || "";
const HUBSPOT_SYNC_PATH = import.meta.env.VITE_N8N_HUBSPOT_SYNC_WEBHOOK || "/webhook/hubspot-sync";
const NOTIFY_SYNC_PATH = import.meta.env.VITE_N8N_NOTIFY_WEBHOOK || "/webhook/notify";
const NEWSLETTER_BCC_EMAIL = import.meta.env.VITE_NEWSLETTER_BCC_EMAIL || "ali.biggy.af@gmail.com";
const BRAND_EMAIL = import.meta.env.VITE_BRAND_EMAIL || "ali.biggy.af@gmail.com";

/** Helper to trigger HubSpot and internal syncs via n8n */
const triggerHubSpotSync = (type, record) => {
  const url = HUBSPOT_SYNC_PATH.startsWith("http") ? HUBSPOT_SYNC_PATH : `${N8N_BASE}${HUBSPOT_SYNC_PATH}`;
  const notifyUrl = NOTIFY_SYNC_PATH.startsWith("http") ? NOTIFY_SYNC_PATH : `${N8N_BASE}${NOTIFY_SYNC_PATH}`;
  
  // Design-specific context for premium welcome flow & BCC tracking
  const designContext = {
    brand_email: BRAND_EMAIL,
    bcc_recipient: NEWSLETTER_BCC_EMAIL,
    template_v: "2026-premium-auth",
    campaign: "New Subscriber Journey"
  };

  fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ 
      type, 
      record, 
      meta: designContext,
      hubspot: {
        lifecyclestage: type === "subscriber" ? "subscriber" : "lead"
      }
    }),
  }).catch((err) => {
    console.warn("[HubSpot sync] Non-blocking failure:", err.message);
  });

  // Trigger customer/admin email notifications for subscriber/newsletter events.
  if (type === "subscriber" || type === "newsletter") {
    fetch(notifyUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        type: "newsletter",
        record,
        meta: designContext,
      }),
    }).catch((err) => {
      console.warn("[Notify sync] Non-blocking failure:", err.message);
    });
  }
};

async function callN8nWebhook(envVar, body) {
  const path = import.meta.env[envVar];
  if (!path) throw new Error(`Missing env var: ${envVar}`);
  const url = path.startsWith("http") ? path : `${N8N_BASE}${path}`;
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`n8n webhook failed: ${res.status}`);
  return res.json().catch(() => ({}));
}

/** Trigger the competitor intelligence scraper workflow */
const triggerCompetitorScrape = () =>
  callN8nWebhook("VITE_N8N_COMPETITOR_SCRAPER_WEBHOOK", { action: "scrape" });

/** Generate content suggestions for a given intel item on a specific platform */
const generateCompetitorContent = (intel_id, platform = "all") =>
  callN8nWebhook("VITE_N8N_COMPETITOR_GENERATE_WEBHOOK", { intel_id, platform });

/** Publish an approved content suggestion as a blog draft */
const publishBlogDraft = (suggestion_id) =>
  callN8nWebhook("VITE_N8N_BLOG_PUBLISHER_WEBHOOK", { suggestion_id });

/** Trigger the Ziyada Newsletter & Blog Writer Agent */
const triggerZiyadaWriter = (query) =>
  callN8nWebhook("VITE_N8N_NEWSLETTER_WRITER_WEBHOOK", { query, type: "newsletter_and_blog" });

/** Trigger the competitor research planner agent from admin dashboard */
const triggerCompetitorAgent = (payload) =>
  callN8nWebhook("VITE_N8N_COMPETITOR_AGENT_WEBHOOK", payload);

/** Explicit helper for month calendar generation requests */
const generateMonthlyCalendar = (payload) =>
  callN8nWebhook("VITE_N8N_CONTENT_STRATEGY_WEBHOOK", {
    action: "generate_monthly_calendar",
    ...payload,
  });

/** Map of function name -> implementation */
const FUNCTIONS = {
  submitLead,
  subscribeEmail,
  bookMeeting,
  getAvailableSlots,
  n8nWebhook,
};

// ---------------------------------------------------------------------------
// Public API  (same shape as the original)
// ---------------------------------------------------------------------------

export const siteApi = {
  entities: {
    Lead: createEntityClient("Lead"),
    Booking: createEntityClient("Booking"),
    BlogPost: createEntityClient("BlogPost"),
    CaseStudy: createEntityClient("CaseStudy"),
    Subscriber: createEntityClient("Subscriber"),
    FAQItem: createEntityClient("FAQItem"),
    Service: createEntityClient("Service"),
    CompetitorIntel: createEntityClient("CompetitorIntel"),
    ContentSuggestion: createEntityClient("ContentSuggestion"),
    AgentConversation: createEntityClient("AgentConversation"),
    ContentCalendarBatch: createEntityClient("ContentCalendarBatch"),
    ContentCalendarEntry: createEntityClient("ContentCalendarEntry"),
  },
  functions: {
    invoke: async (name, payload) => {
      const fn = FUNCTIONS[name];
      if (!fn) throw new Error(`Unknown function: ${name}`);
      const result = await fn(payload || {});
      return { data: result };
    },
    triggerCompetitorScrape,
    generateCompetitorContent,
    publishBlogDraft,
    triggerZiyadaWriter,
    triggerCompetitorAgent,
    generateMonthlyCalendar,
  },
};

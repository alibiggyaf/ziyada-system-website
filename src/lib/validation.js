import { z } from "zod";

export const emailSchema = z.string().email("Invalid email address");
export const phoneSchema = z.string().regex(/^[+]?[\d\s()-]{7,20}$/, "Invalid phone number").or(z.literal(""));
export const nameSchema = z.string().min(2, "Name too short").max(100);

export const bookingSchema = z.object({
  lead_name: nameSchema,
  lead_email: emailSchema,
  lead_phone: phoneSchema,
  company: z.string().min(1),
  booking_date: z.string().min(1),
  booking_time: z.string().min(1),
});

export const proposalSchema = z.object({
  name: nameSchema,
  email: emailSchema,
});

export const contactSchema = z.object({
  name: z.string().min(1),
  email: emailSchema,
  message: z.string().min(1),
});

export function validate(schema, data) {
  const result = schema.safeParse(data);
  if (result.success) return { ok: true, errors: {} };
  const errors = {};
  for (const issue of result.error.issues) {
    const key = issue.path[0];
    if (key && !errors[key]) errors[key] = issue.message;
  }
  return { ok: false, errors };
}

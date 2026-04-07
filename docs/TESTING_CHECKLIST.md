# Ziyada System Integration Testing Checklist

**Last Updated:** April 7, 2026

## 1. Frontend Test
- [ ] Open the Ziyada System website lead/booking form
- [ ] Fill out the form with a test email (e.g., test+hubspot@yourdomain.com)
- [ ] Submit the form and confirm a success message is shown

## 2. Backend Test
- [ ] In Supabase, check the `leads` or `bookings` table for the new row
- [ ] Confirm all fields are populated and note the row `id`
- [ ] In n8n, check the workflow executions tab for a new run (all nodes green)
- [ ] In HubSpot, search for the test email in Contacts and confirm all mapped fields
- [ ] In HubSpot, check Deals for a new deal associated with the contact
- [ ] In your email inbox (`ziyadasystem@gmail.com`), confirm you received the notification
- [ ] In Supabase, confirm the `hubspot_contact_id` column is populated for the new row

## 3. Duplicate Contact Test
- [ ] Submit another form with the same email but different details
- [ ] Confirm n8n updates the existing contact (no duplicate)
- [ ] Confirm a new deal is created and associated with the existing contact

## 4. Error Handling Test
- [ ] Temporarily invalidate the HubSpot token in n8n
- [ ] Submit a test form
- [ ] Confirm the error handler triggers and sends an error notification email
- [ ] Restore the valid token

## 5. Ongoing Maintenance
- [ ] If any step fails, use the error handling and troubleshooting section in HUBSPOT_INTEGRATION.md
- [ ] For new issues, update the docs with solutions or lessons learned
- [ ] If you add new fields or change the workflow, update the mapping tables and .env documentation

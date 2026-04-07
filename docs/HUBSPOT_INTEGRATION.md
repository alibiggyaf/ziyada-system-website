# HubSpot Integration - Ziyada System

---
**Last Updated:** April 7, 2026

**Environment Variable Summary**

Add these to your `.env` (values are examples, do not share secrets):

```
SUPABASE_URL=https://nuyscajjlhxviuyrxzyq.supabase.co
SUPABASE_ANON_KEY=sb_publishable_...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
HUBSPOT_PRIVATE_APP_TOKEN=pat-eu1-...
HUBSPOT_CLIENT_SECRET=...
```

All secrets should be stored in your .env and n8n credentials, never in version control.

---
## 2A. Testing & Maintenance Instructions

### Testing (Front & Backend)

1. Submit a test lead/booking form on the website (use a test email).
2. Confirm the row appears in Supabase (`leads` or `bookings`).
3. Check n8n: Workflow triggers and completes (all nodes green).
4. Check HubSpot: Contact and deal are created/updated with all mapped fields.
5. Check email: Notification arrives at `ziyadasystem@gmail.com`.
6. Check Supabase: `hubspot_contact_id` is written back to the row.

### Ongoing Maintenance

- If any step fails, use the error handling and troubleshooting section below.
- For new issues, update this doc with solutions or lessons learned.
- If you add new fields or change the workflow, update the mapping tables and .env documentation here.

---

> Supabase Database --> n8n Workflow --> HubSpot CRM
>
> Bilingual (AR/EN) lead generation pipeline for the Ziyada System website.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [HubSpot Custom Properties](#2-hubspot-custom-properties-to-create)
3. [n8n Workflow Setup](#3-n8n-workflow-setup)
4. [Supabase Database Webhook Setup](#4-supabase-database-webhook-setup)
5. [HubSpot API Details](#5-hubspot-api-details)
6. [Email Notification Setup](#6-email-notification-setup)
7. [Testing Checklist](#7-testing-checklist)

---

## 1. Architecture Overview

```
+-------------------+       +-------------------+       +-------------------+
|                   |       |                   |       |                   |
|  Supabase DB      | ----> |  n8n Workflow      | ----> |  HubSpot CRM      |
|  (leads/bookings) |       |  (automation)      |       |  (contacts/deals) |
|                   |       |                   |       |                   |
+-------------------+       +-------------------+       +-------------------+
        |                          |                           |
   INSERT trigger            Webhook receives           Creates/updates
   fires webhook             payload, maps fields       contacts & deals
                             checks for duplicates
                             syncs to HubSpot
                             sends email notification
                             writes back contact ID
```

### Data Flow

1. A visitor submits a lead or booking form on the Ziyada System website (Arabic or English).
2. The form data is saved to the Supabase `leads` or `bookings` table.
3. A Supabase Database Webhook fires on the INSERT event and sends the row payload to n8n.
4. The n8n workflow:
   - Extracts and maps the fields.
   - Searches HubSpot for an existing contact by email.
   - Creates a new contact or updates the existing one with all custom properties.
   - Creates a deal in the HubSpot pipeline.
   - Writes the `hubspot_contact_id` back to the Supabase row.
   - Sends an email notification to the team.
5. The sales team works the lead in HubSpot.

### Technology Stack

| Component       | Technology                                      |
| --------------- | ----------------------------------------------- |
| Website         | React + Vite (bilingual AR/EN)                  |
| Database        | Supabase (PostgreSQL)                           |
| Automation      | n8n (`https://n8n.srv953562.hstgr.cloud`)       |
| CRM             | HubSpot (Free or Starter)                       |
| Notifications   | Email via n8n (SMTP or built-in Send Email node)|

---

## 2. HubSpot Custom Properties to Create

Navigate to **HubSpot Settings > Properties > Contact Properties** and create the following custom properties. Use the internal names exactly as listed so the API mapping works.

| Property Name          | Internal Name          | Field Type    | Options / Description                                                                 |
| ---------------------- | ---------------------- | ------------- | ------------------------------------------------------------------------------------- |
| Service Interest       | `service_interest`     | Multi-select  | `automation`, `crm`, `lead-generation`, `marketing`, `web-development`, `social-media`|
| Budget Range           | `budget_range`         | Dropdown      | `<5000`, `5000-15000`, `15000-50000`, `50000+`                                        |
| Timeline               | `timeline`             | Dropdown      | `immediate`, `1-3months`, `3-6months`, `exploring`                                    |
| Source Page             | `source_page`          | Single-line text | Page URL where the form was submitted                                              |
| Language Preference     | `language_preference`  | Dropdown      | `ar`, `en`                                                                            |
| UTM Source              | `utm_source`           | Single-line text | UTM source parameter                                                              |
| UTM Medium              | `utm_medium`           | Single-line text | UTM medium parameter                                                              |
| UTM Campaign            | `utm_campaign`         | Single-line text | UTM campaign parameter                                                            |

### Steps to Create Each Property

1. Go to **HubSpot** > **Settings** (gear icon) > **Properties**.
2. Click **Contact properties** tab.
3. Click **Create property**.
4. Set the **Group** to "Contact information" (or create a "Ziyada Custom" group).
5. Enter the **Label** (e.g., "Service Interest").
6. Set the **Internal name** (e.g., `service_interest`) -- HubSpot may auto-generate this from the label.
7. Choose the **Field type** (Multi-select, Dropdown, or Single-line text).
8. For dropdowns/multi-selects, add each option value.
9. Click **Create**.

---

## 3. n8n Workflow Setup

Create a new workflow in n8n named **"Supabase --> HubSpot Lead Sync"**.

### Node-by-Node Configuration

#### a. Trigger: Webhook Node

- **Node type**: Webhook
- **HTTP Method**: POST
- **Path**: Choose a unique path (e.g., `supabase-hubspot-sync`)
- **Authentication**: Header Auth (optional but recommended)
  - Header Name: `x-webhook-secret`
  - Header Value: A shared secret string
- **Response Mode**: "Last Node" (so Supabase gets a success/failure response)

The webhook URL will be:
```
https://n8n.srv953562.hstgr.cloud/webhook/[YOUR-WEBHOOK-ID]
```

#### b. Set Node: Extract Fields from Payload

- **Node type**: Set
- **Mode**: "Set from expression"
- Map the following fields from the incoming Supabase payload:

| Field Name           | Expression                                          |
| -------------------- | --------------------------------------------------- |
| `first_name`         | `{{ $json.record.first_name || $json.record.name.split(' ')[0] }}` |
| `last_name`          | `{{ $json.record.last_name || $json.record.name.split(' ').slice(1).join(' ') }}` |
| `email`              | `{{ $json.record.email }}`                          |
| `phone`              | `{{ $json.record.phone }}`                          |
| `service_interest`   | `{{ $json.record.service }}`                        |
| `message`            | `{{ $json.record.message }}`                        |
| `budget_range`       | `{{ $json.record.budget_range }}`                   |
| `timeline`           | `{{ $json.record.timeline }}`                       |
| `source_page`        | `{{ $json.record.source_page }}`                    |
| `language_preference`| `{{ $json.record.language || $json.record.lang }}`  |
| `utm_source`         | `{{ $json.record.utm_source }}`                     |
| `utm_medium`         | `{{ $json.record.utm_medium }}`                     |
| `utm_campaign`       | `{{ $json.record.utm_campaign }}`                   |
| `supabase_row_id`    | `{{ $json.record.id }}`                             |
| `table_name`         | `{{ $json.table }}`                                 |

#### c. HTTP Request: Search HubSpot for Existing Contact

- **Node type**: HTTP Request
- **Method**: POST
- **URL**: `https://api.hubapi.com/crm/v3/objects/contacts/search`
- **Authentication**: Predefined Credential Type > **Header Auth**
  - Name: `Authorization`
  - Value: `Bearer YOUR_HUBSPOT_PRIVATE_APP_TOKEN`
- **Body (JSON)**:

```json
{
  "filterGroups": [
    {
      "filters": [
        {
          "propertyName": "email",
          "operator": "EQ",
          "value": "{{ $json.email }}"
        }
      ]
    }
  ],
  "properties": ["email", "firstname", "lastname", "service_interest"]
}
```

#### d. IF Node: Contact Exists?

- **Node type**: IF
- **Condition**: `{{ $json.total }}` is greater than `0`
  - **True branch** --> Update existing contact
  - **False branch** --> Create new contact

#### e. HTTP Request: Create Contact (False Branch)

- **Node type**: HTTP Request
- **Method**: POST
- **URL**: `https://api.hubapi.com/crm/v3/objects/contacts`
- **Authentication**: Header Auth (same as above)
- **Body (JSON)**:

```json
{
  "properties": {
    "email": "{{ $('Set').item.json.email }}",
    "firstname": "{{ $('Set').item.json.first_name }}",
    "lastname": "{{ $('Set').item.json.last_name }}",
    "phone": "{{ $('Set').item.json.phone }}",
    "service_interest": "{{ $('Set').item.json.service_interest }}",
    "budget_range": "{{ $('Set').item.json.budget_range }}",
    "timeline": "{{ $('Set').item.json.timeline }}",
    "source_page": "{{ $('Set').item.json.source_page }}",
    "language_preference": "{{ $('Set').item.json.language_preference }}",
    "utm_source": "{{ $('Set').item.json.utm_source }}",
    "utm_medium": "{{ $('Set').item.json.utm_medium }}",
    "utm_campaign": "{{ $('Set').item.json.utm_campaign }}"
  }
}
```

#### f. HTTP Request: Update Contact (True Branch)

- **Node type**: HTTP Request
- **Method**: PATCH
- **URL**: `https://api.hubapi.com/crm/v3/objects/contacts/{{ $('Search Contact').item.json.results[0].id }}`
- **Authentication**: Header Auth (same as above)
- **Body (JSON)**:

```json
{
  "properties": {
    "phone": "{{ $('Set').item.json.phone }}",
    "service_interest": "{{ $('Set').item.json.service_interest }}",
    "budget_range": "{{ $('Set').item.json.budget_range }}",
    "timeline": "{{ $('Set').item.json.timeline }}",
    "source_page": "{{ $('Set').item.json.source_page }}",
    "language_preference": "{{ $('Set').item.json.language_preference }}",
    "utm_source": "{{ $('Set').item.json.utm_source }}",
    "utm_medium": "{{ $('Set').item.json.utm_medium }}",
    "utm_campaign": "{{ $('Set').item.json.utm_campaign }}"
  }
}
```

#### g. HTTP Request: Create Deal in HubSpot Pipeline

- **Node type**: HTTP Request
- **Method**: POST
- **URL**: `https://api.hubapi.com/crm/v3/objects/deals`
- **Authentication**: Header Auth (same as above)
- **Body (JSON)**:

```json
{
  "properties": {
    "dealname": "{{ $('Set').item.json.first_name }} {{ $('Set').item.json.last_name }} - {{ $('Set').item.json.service_interest }}",
    "pipeline": "default",
    "dealstage": "appointmentscheduled",
    "amount": "",
    "description": "{{ $('Set').item.json.message }}",
    "hs_priority": "medium"
  },
  "associations": [
    {
      "to": {
        "id": "{{ $json.id }}"
      },
      "types": [
        {
          "associationCategory": "HUBSPOT_DEFINED",
          "associationTypeId": 3
        }
      ]
    }
  ]
}
```

> **Note**: `associationTypeId: 3` associates a deal with a contact. The `$json.id` refers to the contact ID from the previous Create/Update node. Adjust `pipeline` and `dealstage` to match your HubSpot pipeline configuration.

#### h. HTTP Request: Update Supabase Row with HubSpot Contact ID

- **Node type**: HTTP Request
- **Method**: PATCH
- **URL**: `https://YOUR_SUPABASE_PROJECT_REF.supabase.co/rest/v1/{{ $('Set').item.json.table_name }}?id=eq.{{ $('Set').item.json.supabase_row_id }}`
- **Headers**:
  - `apikey`: `YOUR_SUPABASE_ANON_KEY`
  - `Authorization`: `Bearer YOUR_SUPABASE_SERVICE_ROLE_KEY`
  - `Content-Type`: `application/json`
  - `Prefer`: `return=minimal`
- **Body (JSON)**:

```json
{
  "hubspot_contact_id": "{{ $json.id }}"
}
```

> **Important**: You must add a `hubspot_contact_id` column (type: `text`) to both the `leads` and `bookings` tables in Supabase before this step will work.

#### i. Error Handler

- **Node type**: Error Trigger (or use the workflow-level Error Workflow setting)
- Connect to a **Send Email** node or **HTTP Request** node that logs the error.
- Recommended: Send error details to `ziyadasystem@gmail.com` so failures are not silent.

### Complete Workflow Diagram

```
[Webhook Trigger]
       |
   [Set Node] -- Extract & map fields
       |
[HTTP: Search Contact by Email]
       |
   [IF: Exists?]
    /        \
  YES         NO
   |           |
[HTTP:       [HTTP:
 Update       Create
 Contact]     Contact]
    \         /
     \       /
  [Merge Node]
       |
[HTTP: Create Deal]
       |
[HTTP: Update Supabase with hubspot_contact_id]
       |
[Send Email Notification]
       |
     [End]

     (Error Trigger) --> [Send Error Email]
```

---

## 4. Supabase Database Webhook Setup

### For the `leads` Table

1. Go to **Supabase Dashboard** > select your project.
2. Navigate to **Database** > **Webhooks** (in the left sidebar).
3. Click **Create a new hook**.
4. Configure:
   - **Name**: `leads_to_hubspot`
   - **Table**: `leads`
   - **Events**: Check **INSERT**
   - **Type**: HTTP Request
   - **Method**: POST
   - **URL**: `https://n8n.srv953562.hstgr.cloud/webhook/[YOUR-WEBHOOK-ID]`
   - **Headers** (optional but recommended):
     ```
     x-webhook-secret: YOUR_SHARED_SECRET
     Content-Type: application/json
     ```
5. Click **Create webhook**.

### For the `bookings` Table

Repeat the same steps with:

- **Name**: `bookings_to_hubspot`
- **Table**: `bookings`
- **Events**: Check **INSERT**
- **URL**: Same n8n webhook URL

### Supabase Webhook Payload Format

When a row is inserted, Supabase sends a payload like this:

```json
{
  "type": "INSERT",
  "table": "leads",
  "schema": "public",
  "record": {
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "name": "Ahmed Al-Rashid",
    "email": "ahmed@example.com",
    "phone": "+966501234567",
    "service": "automation",
    "message": "I need help automating my business processes",
    "budget_range": "5000-15000",
    "timeline": "1-3months",
    "source_page": "/en/services/automation",
    "language": "en",
    "utm_source": "google",
    "utm_medium": "cpc",
    "utm_campaign": "automation-2026",
    "created_at": "2026-04-05T12:00:00.000Z",
    "hubspot_contact_id": null
  },
  "old_record": null
}
```

### Required Database Column Addition

Run this SQL in Supabase SQL Editor to add the `hubspot_contact_id` column:

```sql
ALTER TABLE leads ADD COLUMN IF NOT EXISTS hubspot_contact_id TEXT;
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS hubspot_contact_id TEXT;
```

---

## 5. HubSpot API Details

### Authentication

1. Go to **HubSpot** > **Settings** > **Integrations** > **Private Apps**.
2. Click **Create a private app**.
3. Name it "Ziyada n8n Integration".
4. Under **Scopes**, enable:
   - `crm.objects.contacts.read`
   - `crm.objects.contacts.write`
   - `crm.objects.deals.read`
   - `crm.objects.deals.write`
   - `crm.schemas.contacts.read`
   - `crm.schemas.deals.read`
5. Click **Create app** and copy the **Access token**.

Store the token in n8n as a credential (Header Auth):
- **Name**: `Authorization`
- **Value**: `Bearer pat-na1-XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX`

### Base URL

```
https://api.hubapi.com
```

### Endpoints

#### Search Contact by Email

```
POST /crm/v3/objects/contacts/search
```

**Request Body:**

```json
{
  "filterGroups": [
    {
      "filters": [
        {
          "propertyName": "email",
          "operator": "EQ",
          "value": "ahmed@example.com"
        }
      ]
    }
  ],
  "properties": [
    "email",
    "firstname",
    "lastname",
    "phone",
    "service_interest"
  ]
}
```

**Response (contact found):**

```json
{
  "total": 1,
  "results": [
    {
      "id": "12345",
      "properties": {
        "email": "ahmed@example.com",
        "firstname": "Ahmed",
        "lastname": "Al-Rashid",
        "phone": "+966501234567",
        "service_interest": "automation",
        "createdate": "2026-04-01T10:00:00.000Z",
        "lastmodifieddate": "2026-04-05T12:00:00.000Z"
      }
    }
  ]
}
```

**Response (no contact found):**

```json
{
  "total": 0,
  "results": []
}
```

#### Create Contact

```
POST /crm/v3/objects/contacts
```

**Request Body:**

```json
{
  "properties": {
    "email": "ahmed@example.com",
    "firstname": "Ahmed",
    "lastname": "Al-Rashid",
    "phone": "+966501234567",
    "service_interest": "automation",
    "budget_range": "5000-15000",
    "timeline": "1-3months",
    "source_page": "/en/services/automation",
    "language_preference": "en",
    "utm_source": "google",
    "utm_medium": "cpc",
    "utm_campaign": "automation-2026"
  }
}
```

**Response:**

```json
{
  "id": "12345",
  "properties": {
    "email": "ahmed@example.com",
    "firstname": "Ahmed",
    "lastname": "Al-Rashid",
    "createdate": "2026-04-05T12:00:00.000Z",
    "lastmodifieddate": "2026-04-05T12:00:00.000Z",
    "hs_object_id": "12345"
  },
  "createdAt": "2026-04-05T12:00:00.000Z",
  "updatedAt": "2026-04-05T12:00:00.000Z",
  "archived": false
}
```

#### Update Contact

```
PATCH /crm/v3/objects/contacts/{contactId}
```

**Request Body:**

```json
{
  "properties": {
    "phone": "+966501234567",
    "service_interest": "automation;crm",
    "budget_range": "15000-50000",
    "timeline": "immediate"
  }
}
```

#### Create Deal

```
POST /crm/v3/objects/deals
```

**Request Body:**

```json
{
  "properties": {
    "dealname": "Ahmed Al-Rashid - automation",
    "pipeline": "default",
    "dealstage": "appointmentscheduled",
    "amount": "",
    "description": "I need help automating my business processes"
  },
  "associations": [
    {
      "to": {
        "id": "12345"
      },
      "types": [
        {
          "associationCategory": "HUBSPOT_DEFINED",
          "associationTypeId": 3
        }
      ]
    }
  ]
}
```

**Response:**

```json
{
  "id": "67890",
  "properties": {
    "dealname": "Ahmed Al-Rashid - automation",
    "pipeline": "default",
    "dealstage": "appointmentscheduled",
    "createdate": "2026-04-05T12:00:00.000Z",
    "hs_lastmodifieddate": "2026-04-05T12:00:00.000Z",
    "hs_object_id": "67890"
  },
  "createdAt": "2026-04-05T12:00:00.000Z",
  "updatedAt": "2026-04-05T12:00:00.000Z",
  "archived": false
}
```

### Rate Limits

- HubSpot API allows **100 requests per 10 seconds** for private apps.
- For burst scenarios (e.g., bulk import), add a Wait node in n8n between requests.

### Error Codes

| Status Code | Meaning                          | Action                        |
| ----------- | -------------------------------- | ----------------------------- |
| 200/201     | Success                          | Continue workflow              |
| 400         | Bad request (invalid properties) | Check property names/values    |
| 401         | Unauthorized                     | Check/refresh API token        |
| 409         | Conflict (duplicate email)       | Use update instead of create   |
| 429         | Rate limited                     | Add delay and retry            |

---

## 6. Email Notification Setup

Add a **Send Email** node after the HubSpot sync step in the n8n workflow.

### Node Configuration

- **Node type**: Send Email (or Email Send via SMTP)
- **From**: `noreply@ziyadasystem.com` (or your configured sender)
- **To**: `ziyadasystem@gmail.com`
- **Subject**:

```
New Lead: {{ $('Set').item.json.first_name }} {{ $('Set').item.json.last_name }} - {{ $('Set').item.json.service_interest }}
```

- **Body (HTML)**:

```html
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
  <h2 style="color: #2563eb; border-bottom: 2px solid #2563eb; padding-bottom: 10px;">
    New Lead Received
  </h2>

  <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
    <tr style="background: #f8fafc;">
      <td style="padding: 10px; font-weight: bold; width: 40%;">Name</td>
      <td style="padding: 10px;">{{ $('Set').item.json.first_name }} {{ $('Set').item.json.last_name }}</td>
    </tr>
    <tr>
      <td style="padding: 10px; font-weight: bold;">Email</td>
      <td style="padding: 10px;">{{ $('Set').item.json.email }}</td>
    </tr>
    <tr style="background: #f8fafc;">
      <td style="padding: 10px; font-weight: bold;">Phone</td>
      <td style="padding: 10px;">{{ $('Set').item.json.phone }}</td>
    </tr>
    <tr>
      <td style="padding: 10px; font-weight: bold;">Service Interest</td>
      <td style="padding: 10px;">{{ $('Set').item.json.service_interest }}</td>
    </tr>
    <tr style="background: #f8fafc;">
      <td style="padding: 10px; font-weight: bold;">Budget Range</td>
      <td style="padding: 10px;">{{ $('Set').item.json.budget_range }}</td>
    </tr>
    <tr>
      <td style="padding: 10px; font-weight: bold;">Timeline</td>
      <td style="padding: 10px;">{{ $('Set').item.json.timeline }}</td>
    </tr>
    <tr style="background: #f8fafc;">
      <td style="padding: 10px; font-weight: bold;">Language</td>
      <td style="padding: 10px;">{{ $('Set').item.json.language_preference }}</td>
    </tr>
    <tr>
      <td style="padding: 10px; font-weight: bold;">Source Page</td>
      <td style="padding: 10px;">{{ $('Set').item.json.source_page }}</td>
    </tr>
    <tr style="background: #f8fafc;">
      <td style="padding: 10px; font-weight: bold;">Message</td>
      <td style="padding: 10px;">{{ $('Set').item.json.message }}</td>
    </tr>
  </table>

  <div style="margin-top: 20px; padding: 15px; background: #eff6ff; border-radius: 8px;">
    <p style="margin: 0; font-size: 14px; color: #1e40af;">
      <strong>UTM Data:</strong>
      Source: {{ $('Set').item.json.utm_source }} |
      Medium: {{ $('Set').item.json.utm_medium }} |
      Campaign: {{ $('Set').item.json.utm_campaign }}
    </p>
  </div>

  <div style="margin-top: 15px; padding: 15px; background: #f0fdf4; border-radius: 8px;">
    <p style="margin: 0; font-size: 14px; color: #166534;">
      <strong>HubSpot Contact ID:</strong> {{ $json.id }}
      <br/>
      <a href="https://app.hubspot.com/contacts/YOUR_HUB_ID/contact/{{ $json.id }}">
        View in HubSpot
      </a>
    </p>
  </div>

  <hr style="margin-top: 20px; border: none; border-top: 1px solid #e2e8f0;" />
  <p style="font-size: 12px; color: #94a3b8;">
    Automated notification from Ziyada System n8n workflow.
    Table: {{ $('Set').item.json.table_name }} |
    Supabase Row ID: {{ $('Set').item.json.supabase_row_id }}
  </p>
</div>
```

### SMTP Configuration in n8n

If not already configured, add SMTP credentials in n8n:

1. Go to **n8n** > **Credentials** > **New Credential** > **SMTP**.
2. Configure with your email provider (e.g., Gmail, SendGrid, custom SMTP).
3. For Gmail:
   - **Host**: `smtp.gmail.com`
   - **Port**: `465`
   - **SSL/TLS**: Yes
   - **User**: `ziyadasystem@gmail.com`
   - **Password**: Use an App Password (not your regular password)

---

## 7. Testing Checklist

Use this checklist to verify the full integration is working end-to-end.

### Pre-flight Checks

- [ ] `hubspot_contact_id` column exists on both `leads` and `bookings` tables in Supabase
- [ ] All 8 custom properties created in HubSpot (see Section 2)
- [ ] HubSpot Private App token is valid and has required scopes
- [ ] n8n workflow is **active** (toggle on)
- [ ] Supabase database webhooks are created and pointing to the correct n8n URL
- [ ] SMTP credentials configured in n8n for email notifications

### End-to-End Test

1. **Submit a test form on the website**
   - [ ] Go to the Ziyada System website and fill out a lead form
   - [ ] Use a test email like `test+hubspot@yourdomain.com`
   - [ ] Fill in all fields (service, budget, timeline, message)

2. **Verify data lands in Supabase**
   - [ ] Open Supabase Dashboard > Table Editor > `leads`
   - [ ] Confirm the new row exists with all fields populated
   - [ ] Note the row `id` for later verification

3. **Verify n8n execution passes**
   - [ ] Open n8n > Workflow > Executions tab
   - [ ] Find the most recent execution
   - [ ] Confirm all nodes show green (success)
   - [ ] If any node is red, click it to see the error details

4. **Verify HubSpot contact was created**
   - [ ] Open HubSpot > Contacts
   - [ ] Search for the test email
   - [ ] Confirm all custom properties are populated correctly:
     - [ ] `service_interest` matches form selection
     - [ ] `budget_range` matches form selection
     - [ ] `timeline` matches form selection
     - [ ] `source_page` shows the correct URL
     - [ ] `language_preference` is `ar` or `en`
     - [ ] UTM fields populated (if applicable)

5. **Verify deal was created**
   - [ ] Open HubSpot > Deals
   - [ ] Find the deal named after the test contact
   - [ ] Confirm it is associated with the contact
   - [ ] Confirm it is in the correct pipeline stage

6. **Verify email notification received**
   - [ ] Check `ziyadasystem@gmail.com` inbox
   - [ ] Confirm the subject line includes lead name and service
   - [ ] Confirm the body includes all form fields
   - [ ] Confirm the HubSpot link works

7. **Verify `hubspot_contact_id` written back to Supabase**
   - [ ] Open Supabase > Table Editor > `leads`
   - [ ] Find the test row
   - [ ] Confirm `hubspot_contact_id` column is now populated with the HubSpot ID

### Duplicate Contact Test

- [ ] Submit another form with the **same email** but different details
- [ ] Verify n8n updates the existing contact (does NOT create a duplicate)
- [ ] Verify a new deal is created and associated with the existing contact

### Error Handling Test

- [ ] Temporarily invalidate the HubSpot token in n8n
- [ ] Submit a test form
- [ ] Verify the error handler triggers and sends an error notification email
- [ ] Restore the valid token

---

## Quick Reference: Environment Variables & Secrets

| Secret                          | Where to Store        | Used By             |
| ------------------------------- | --------------------- | ------------------- |
| HubSpot Private App Token       | n8n Credentials       | n8n workflow         |
| Supabase Service Role Key       | n8n Credentials       | n8n workflow         |
| Supabase Anon Key               | n8n Credentials       | n8n workflow         |
| Webhook Shared Secret           | n8n + Supabase config | Webhook auth         |
| SMTP Password / App Password    | n8n Credentials       | Email notifications  |

> **Security Note**: Never commit API keys or tokens to version control. All secrets should be stored in n8n credentials or environment variables.

# HubSpot & AtomChat Integration Guide

## Overview

This guide documents the native integration between HubSpot CRM and AtomChat.io for automated conversational campaigns, specifically for WhatsApp Business messaging.

## Why Native Integration?

The platform uses **direct native integration** between HubSpot and AtomChat.io instead of third-party connectors (like Zapier) for:

- ✅ Maximum stability and reliability
- ✅ Real-time data synchronization
- ✅ Lower latency in message delivery
- ✅ Better data consistency
- ✅ No additional service dependencies

## Prerequisites

- HubSpot account (Professional or Enterprise tier recommended)
- AtomChat.io account
- WhatsApp Business API access (via AtomChat)
- Admin access to both platforms

## Integration Setup

### 1. Connect AtomChat to HubSpot

1. **In AtomChat Dashboard:**
   - Navigate to "Integrations"
   - Select "HubSpot"
   - Click "Connect"
   - Authorize the connection

2. **In HubSpot:**
   - Go to Settings → Integrations → Connected Apps
   - Find "AtomChat" and verify connection status
   - Review permission scopes

### 2. Configure WhatsApp Business

1. **Link WhatsApp Number:**
   - In AtomChat: Settings → WhatsApp Business
   - Follow Meta Business verification
   - Link your WhatsApp Business phone number

2. **Create Message Templates:**
   - Navigate to AtomChat → Templates
   - Create pre-approved message templates
   - Submit for Meta approval (required for WhatsApp)
   - Wait for approval (usually 24-48 hours)

### 3. Set Up HubSpot Workflows

#### Example: New Lead Follow-up

1. **Create Workflow:**
   - HubSpot → Automation → Workflows
   - "Create workflow from scratch"
   - Choose "Contact-based"

2. **Set Enrollment Trigger:**
   ```
   When: Contact is created
   AND
   Lead Source = Facebook/Instagram Ads
   ```

3. **Add AtomChat Action:**
   - Click "+" to add action
   - Search for "AtomChat"
   - Select "Send WhatsApp Message"

4. **Configure Message:**
   - Template: Select approved template
   - Variables: Map HubSpot properties
   ```
   Hi {{contact.firstname}},
   
   Thank you for your interest in our services!
   Your reference number is {{contact.id}}.
   
   One of our team members will contact you within 24 hours.
   ```

5. **Set Delays (Optional):**
   - Add delay before message
   - Set business hours filter
   - Configure retry logic

## Automated Campaign Workflows

### 1. Lead Nurturing Campaign

**Trigger:** Contact enters "Lead" stage

**Actions:**
1. Send welcome WhatsApp message (immediately)
2. Wait 2 days
3. Send educational content
4. Wait 3 days
5. Send case study
6. Wait 2 days
7. Send meeting invitation

**Implementation:**
```
Enrollment: Lifecycle stage is Lead
│
├─→ Send WhatsApp (Template: Welcome)
│
├─→ Delay 2 days
│
├─→ Send WhatsApp (Template: Education)
│
├─→ Delay 3 days
│
├─→ Send WhatsApp (Template: Case Study)
│
├─→ Delay 2 days
│
└─→ Send WhatsApp (Template: Meeting Request)
```

### 2. Payment Reminder Campaign

**Trigger:** Invoice due date approaching

**Actions:**
1. Check payment status
2. If unpaid, send reminder 3 days before
3. Send reminder 1 day before
4. Send day-of reminder
5. Create task for collections team if overdue

**Implementation:**
```
Enrollment: Invoice due date is in 3 days
AND Payment status is Unpaid
│
├─→ Send WhatsApp (Reminder 3 days)
│
├─→ Delay until 1 day before due
│
├─→ If-then branch: Still unpaid?
│   │
│   ├─→ YES: Send WhatsApp (Reminder 1 day)
│   │
│   └─→ NO: End workflow
│
├─→ Delay until due date
│
└─→ If-then branch: Still unpaid?
    │
    ├─→ YES: 
    │   ├─→ Send WhatsApp (Final reminder)
    │   └─→ Create task for collections
    │
    └─→ NO: End workflow
```

### 3. Loan Disbursement Notification

**Trigger:** Loan status changes to "Approved"

**Actions:**
1. Send approval notification
2. Request bank details via WhatsApp
3. Wait for response
4. Update CRM with details
5. Send confirmation of disbursement

## Message Template Best Practices

### Template Structure

```
[Greeting]
Hi {{1}},

[Body]
Your loan of ${{2}} has been approved!

[Call to Action]
Please reply with your bank details:
- Account Number
- Bank Name

[Footer]
ABACO Financial Services
```

### Variable Mapping

Map HubSpot properties to template variables:

| Template Variable | HubSpot Property |
|------------------|------------------|
| {{1}} | First Name |
| {{2}} | Loan Amount |
| {{3}} | Reference Number |
| {{4}} | Due Date |

### Template Types

**1. Notification Templates**
- Order confirmations
- Payment receipts
- Status updates

**2. Marketing Templates**
- Promotional offers
- Product announcements
- Event invitations

**3. Utility Templates**
- OTP codes
- Appointment reminders
- Account updates

## Data Synchronization

### Contact Property Sync

Configure bidirectional sync:

**HubSpot → AtomChat:**
- Contact name
- Phone number
- Email
- Company
- Deal stage
- Custom properties

**AtomChat → HubSpot:**
- Last message date
- Response status
- Opt-in status
- Conversation notes

### Conversation Logging

All WhatsApp conversations are logged to HubSpot:

1. **Timeline Entry:**
   - Each message appears on contact timeline
   - Includes timestamp and message content
   - Shows delivery and read status

2. **Engagement Metrics:**
   - Messages sent
   - Messages delivered
   - Messages read
   - Response rate

## Advanced Workflows

### Multi-Channel Follow-up

Combine WhatsApp with email and SMS:

```
Enrollment: Deal stage is "Proposal Sent"
│
├─→ Send Email (Proposal)
│
├─→ Delay 1 day
│
├─→ If-then: Email opened?
│   │
│   ├─→ NO: Send WhatsApp reminder
│   │
│   └─→ YES: Wait for deal update
│
├─→ Delay 3 days
│
└─→ If-then: Deal still in Proposal?
    │
    ├─→ YES: Send SMS follow-up
    │
    └─→ NO: End workflow
```

### Smart Routing

Route conversations to specific agents:

```
Trigger: New WhatsApp message received
│
├─→ Extract intent using keywords
│
├─→ Branch by intent:
│   │
│   ├─→ Sales → Assign to Sales Team
│   ├─→ Support → Assign to Support Team
│   ├─→ Billing → Assign to Finance Team
│   └─→ Other → Assign to General Queue
│
└─→ Create ticket in HubSpot
```

## Testing & Monitoring

### Test Workflow

1. Create test contact in HubSpot
2. Enroll in workflow manually
3. Verify message delivery in AtomChat
4. Check timeline updates in HubSpot
5. Validate data synchronization

### Monitoring Dashboard

Track key metrics:

- **Delivery Rate:** Messages delivered / sent
- **Read Rate:** Messages read / delivered
- **Response Rate:** Responses / messages sent
- **Conversion Rate:** Deals closed / contacts reached

### Error Handling

Common issues and solutions:

**Message Not Delivered:**
- Check WhatsApp number validity
- Verify template approval status
- Confirm contact opt-in status

**Workflow Not Triggering:**
- Review enrollment criteria
- Check workflow active status
- Verify trigger conditions

**Data Sync Issues:**
- Refresh integration connection
- Check field mappings
- Review API logs in AtomChat

## Compliance & Best Practices

### WhatsApp Business Policy

✅ **DO:**
- Use approved templates for first message
- Get explicit opt-in from contacts
- Include opt-out instructions
- Respect 24-hour window for replies

❌ **DON'T:**
- Send promotional messages without opt-in
- Use personal WhatsApp accounts
- Share sensitive data without encryption
- Spam contacts with frequent messages

### GDPR Compliance

- Store consent records in HubSpot
- Allow contacts to request data deletion
- Document data processing activities
- Implement right to be forgotten

### Data Security

- Use encrypted channels for sensitive data
- Implement access controls
- Regular security audits
- Monitor for suspicious activity

## API Integration (Advanced)

For custom integrations:

### HubSpot API
```python
import requests

HUBSPOT_API_KEY = "your-key"
url = "https://api.hubapi.com/contacts/v1/contact"

headers = {
    "Authorization": f"Bearer {HUBSPOT_API_KEY}",
    "Content-Type": "application/json"
}

# Create contact
data = {
    "properties": [
        {"property": "firstname", "value": "John"},
        {"property": "phone", "value": "+1234567890"}
    ]
}

response = requests.post(url, json=data, headers=headers)
```

### AtomChat API
```python
ATOMCHAT_API_KEY = "your-key"
ATOMCHAT_APP_ID = "your-app-id"

url = "https://api.atomchat.io/v1/messages/send"

headers = {
    "apiKey": ATOMCHAT_API_KEY,
    "appId": ATOMCHAT_APP_ID
}

data = {
    "to": "+1234567890",
    "template": "welcome_message",
    "variables": ["John", "12345"]
}

response = requests.post(url, json=data, headers=headers)
```

## Resources

- [HubSpot Workflows Documentation](https://knowledge.hubspot.com/workflows)
- [AtomChat Integration Guide](https://atomchat.io/integrations/hubspot)
- [WhatsApp Business API](https://developers.facebook.com/docs/whatsapp)
- [Meta Business Verification](https://business.facebook.com/business/help/)

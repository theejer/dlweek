# SafePassage Heartbeat & Alert System Demo Guide

**For:** User demos and testing  
**Date:** March 3, 2026  
**Purpose:** Simple walkthrough to demonstrate heartbeat monitoring and 3-stage alert escalation

---

## What is the Heartbeat System?

The heartbeat system is SafePassage's **CURE** (connectivity-aware offline anomaly alerts) pillar. It works like this:

1. **Mobile app sends "heartbeats"** - Regular check-ins from your phone saying "I'm here, I'm safe"
2. **Backend monitors heartbeats** - Watches for missing check-ins
3. **Alert escalation** - If you go offline too long, it sends alerts to your emergency contacts:
   - **Stage 1:** Initial alert - "They've been offline longer than expected"
   - **Stage 2:** Escalation - "Still offline, this is serious"
   - **Stage 3:** Recovery - "They're back online, all good!"

---

## Part 1: Demo the Heartbeat Feature (Frontend → Backend)

### What You'll See:
- Mobile app sends heartbeats automatically every 30 minutes
- You can also trigger manual heartbeats for testing
- Backend receives and stores the heartbeat data
- Dashboard shows recent heartbeats with details

### Steps:

#### 1. Start the Backend Server

Open a terminal and run:

```bash
cd "c:\JR's Cache\dlweek_project\backend"
.\.venv\Scripts\Activate.ps1
python wsgi.py
```

**Expected output:**
```
 * Running on http://127.0.0.1:5000
```

#### 2. Start the Frontend App

Open another terminal:

```bash
cd "c:\JR's Cache\dlweek_project\frontend"
npx expo start --tunnel
```

**Scan the QR code** with Expo Go app on your phone.

#### 3. Create a User and Trip

In the app:
1. Open the app → You'll land on "Onboarding" screen
2. Fill in:
   - Name: "Demo User"
   - Phone: "+919876543210"
   - Email: "demo@test.com"
3. Tap **"Complete Onboarding"**
4. You'll see the Dashboard
5. Tap **"Create New Trip"**
6. Fill in trip details:
   - Title: "Bihar Safety Test"
   - Start Date: Today
   - End Date: Tomorrow
   - Destination: "India"
7. Tap **"Create Trip"**

**Important:** The trip is automatically created with `heartbeat_enabled: true`.


#### 4. View Heartbeats on Dashboard

In the app:
1. Go back to **Dashboard**
2. Scroll down to **"Recent Heartbeats"** section
3. You should see your heartbeat listed:
   - Timestamp (e.g., "10:45 AM")
   - Status indicator (🟢 Synced)
   - Network status and battery level
4. Tap on a heartbeat to expand and see details:
   - Battery: 85%
   - Network: Online
   - Source: manual_debug
   - Sync status: Synced



## Part 2: Demo the Alert System (Stage 1, 2, 3)

### How Alerts Work:

The backend has a **watchdog** that runs every 5 minutes (configurable). It:
1. Checks all active trips with heartbeat monitoring enabled
2. Looks at the last heartbeat time
3. Calculates how long the user has been offline
4. If offline too long → triggers alerts

**Alert Stages:**

| Stage | Trigger | Alert Message | Recipient |
|-------|---------|---------------|-----------|
| **Stage 1** | Offline longer than expected | "Initial alert: They haven't checked in" | Emergency contacts |
| **Stage 2** | Still offline after Stage 1 | "Escalation: Still no contact, please check" | Emergency contacts (more urgent) |
| **Stage 3** | User comes back online | "Good news: They're back online!" | Emergency contacts |

### Steps to Demo Alerts:

#### Option A: Use Test Mode (Quick Demo, No Waiting)

**1. Enable Test Mode**

In `backend/.env`, add:
```
HEARTBEAT_FORCE_STAGE_1_TEST_MODE=1
```

Restart the backend server.

**What this does:** Stage 1 alert triggers immediately for ANY trip, even if heartbeat just came in. This is for testing only.

**2. Enable the Watchdog Scheduler**

In `backend/.env`, also add:
```
ENABLE_HEARTBEAT_SCHEDULER=1
HEARTBEAT_WATCHDOG_INTERVAL_MINUTES=1
```

Restart backend again.

**3. Watch the Backend Logs**

Within 1 minute, you'll see in the backend logs:

```
[INFO] Heartbeat watchdog cycle starting...
[INFO] Evaluating trip: Bihar Safety Test (trip_id: xxx)
[INFO] [TEST MODE] Sending Stage 1 alert to emergency contacts
[INFO] Stage 1 alert sent to: +919123456789
[INFO] Heartbeat watchdog cycle completed; next_run_utc=...
```

**4. Check Alert in Database**

```sql
SELECT * FROM alert_events ORDER BY created_at DESC LIMIT 1;
```

You'll see:
- `alert_type`: `stage_1_initial_alert`
- `user_id`: Your user ID
- `trip_id`: Your trip ID
- `message`: The alert message sent to contacts

**5. Trigger Stage 3 (Recovery)**

Go back to the mobile app and tap **"Send Debug Heartbeat"** again.

Within 1 minute, backend logs will show:
```
[INFO] Stage 3 auto-recovery alert triggered
[INFO] User is back online, sending good news to contacts
```

---

#### Option B: Real Scenario Demo (More Realistic, Takes Time)

**1. Disable Test Mode**

In `backend/.env`:
```
HEARTBEAT_FORCE_STAGE_1_TEST_MODE=0
ENABLE_HEARTBEAT_SCHEDULER=1
HEARTBEAT_WATCHDOG_INTERVAL_MINUTES=5
```

**2. Setup Expected Offline Window**

The alert system uses "expected offline minutes" from itinerary risk analysis. By default, it's 90 minutes.

To trigger Stage 1 faster, we can adjust the trip's risk profile or manually set shorter thresholds (requires code changes, see Advanced section).

**3. Simulate Going Offline**

- Send one heartbeat from the mobile app
- **Close the app completely** and **turn off WiFi/data**
- Wait 90+ minutes (or whatever the expected offline time is)

**4. Watch for Stage 1 Alert**

After 90+ minutes, the watchdog will detect:
- Last heartbeat was > 90 minutes ago
- Offline duration exceeds expected window
- Trigger Stage 1 alert

Backend logs:
```
[INFO] Evaluating trip: Bihar Safety Test
[INFO] Offline duration: 95 minutes, expected: 90 minutes
[INFO] Triggering Stage 1 alert
```

**5. Simulate Further Delay for Stage 2**

Stay offline for another 60+ minutes. Stage 2 will trigger:

```
[INFO] Offline duration: 155 minutes (Stage 2 threshold crossed)
[INFO] Triggering Stage 2 escalation alert
```

**6. Come Back Online (Stage 3)**

- Turn WiFi/data back on
- Open the app
- Send a heartbeat (or wait for automatic 30-min heartbeat)

Backend logs:
```
[INFO] Heartbeat received from previously offline user
[INFO] Triggering Stage 3 auto-recovery alert
[INFO] Sending 'all clear' message to emergency contacts
```

---

## Part 3: Manual Watchdog Trigger (Advanced Testing)

If you don't want to wait for the scheduler, you can manually trigger the watchdog.

### Steps:

**1. Set Watchdog API Key**

In `backend/.env`:
```
HEARTBEAT_WATCHDOG_KEY=my-secret-test-key
```

**2. Call the Watchdog Endpoint**

Use Postman or curl:

```bash
curl -X POST http://localhost:5000/heartbeats/watchdog/run \
  -H "x-watchdog-key: my-secret-test-key"
```

**Expected response:**
```json
{
  "status": "completed",
  "evaluated_trips": 1,
  "alerts_triggered": {
    "stage_1": 0,
    "stage_2": 0,
    "stage_3": 0
  }
}
```

**What this does:**
- Immediately runs the watchdog evaluation loop
- Checks all active trips
- Triggers alerts if conditions met
- Returns summary of what happened

**Use this method** to quickly test alert logic without waiting for scheduler intervals.

---

## Part 4: Viewing Alerts (Frontend)

### Current State:
The frontend **does not yet have** an alert history viewer. Alerts are currently sent via SMS (stubbed) and logged in the backend.

### Roadmap:
Future features:
- **Alert History Screen** - View all Stage 1/2/3 alerts for your trips
- **Push Notifications** - Receive alerts on your phone
- **Alert Detail View** - See full alert context, offline duration, location

### For Demo Purposes:
To show alerts, you can:
1. Check backend database: `SELECT * FROM alert_events`
2. Show backend logs during live demo
3. Explain that SMS alerts would go to emergency contacts (show stub log message)

---

## Troubleshooting

### Issue: "Heartbeat skipped (missing-active-user-or-heartbeat-enabled-trip)"

**Cause:** No active trip with heartbeat enabled.

**Solution:**
1. Create a trip in the app
2. Ensure trip dates include today
3. Verify `heartbeat_enabled` is true (it's default)

---

### Issue: "No Stage 1 alert triggered even in test mode"

**Causes:**
1. `HEARTBEAT_FORCE_STAGE_1_TEST_MODE=0` (not enabled)
2. No emergency contacts added to the user
3. Trip is not active (start_date > today or end_date < today)
4. Trip has `heartbeat_enabled: false`

**Solution:**
- Check `.env` has `HEARTBEAT_FORCE_STAGE_1_TEST_MODE=1`
- Add emergency contact via API: `POST /users/{user_id}/emergency_contacts`
- Verify trip dates cover today
- Restart backend after changing `.env`

---

### Issue: "Backend returns 401 Unauthorized on heartbeat POST"

**Cause:** Missing or invalid bearer token.

**Solution:**
The heartbeat endpoint requires authentication. Frontend automatically handles this via `apiClient`. If testing manually:

```bash
curl -X POST http://localhost:5000/heartbeats \
  -H "Authorization: Bearer YOUR_USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-uuid",
    "trip_id": "trip-uuid",
    "timestamp": "2026-03-03T10:30:00Z",
    "battery_percent": 85,
    "network_status": "online",
    "source": "manual_debug"
  }'
```

---

## Demo Script Summary (2-Minute Version)

**For quick demos to stakeholders:**

### 1. Show Heartbeat Feature (30 seconds)
- Open mobile app
- Navigate to Dashboard
- Show "Recent Heartbeats" section with live data
- Tap one heartbeat to show details (battery, GPS, network status)

### 2. Trigger Manual Heartbeat (15 seconds)
- Go to "Heartbeat Debug" screen
- Tap "Send Debug Heartbeat"
- Return to Dashboard, see new heartbeat appear (auto-refreshes every 10s)

### 3. Explain Alert System (45 seconds)
"Behind the scenes, our backend monitors these heartbeats. If someone goes offline longer than expected:
- **Stage 1:** We send an initial alert to their emergency contacts
- **Stage 2:** If still offline, we escalate with a more urgent message
- **Stage 3:** When they come back online, we send an 'all clear' message

Let me show you the backend logs..."

### 4. Show Backend Logs (30 seconds)
- Switch to backend terminal
- Show watchdog cycle logs
- If test mode enabled, show Stage 1 alert being triggered
- Show alert message content in logs

**Total time:** ~2 minutes

---

# Compliance patterns for Level 3 implementation
# This file provides clean pattern definitions without f-string issues

COMPLIANCE_PATTERNS = {
    "pci-dss-password-hashing.md": """---
title: PCI-DSS Pattern - Password Hashing
type: compliance-pattern
tags: [compliance, pci-dss, security, passwords]
related:
  - [[.specs/memory.md]]
  - [[.ai-docs/COMPLIANCE-CHECKLIST-PCI-DSS.md]]
---

# PCI-DSS: Password Hashing (Requirement 8)

Passwords must be encrypted using strong cryptography, not stored in plaintext.

## Pattern: Use bcrypt (cost ≥ 12)

### Python (Django)
```python
from django.contrib.auth.hashers import make_password, check_password

# Hash password on registration
hashed = make_password(password, salt=None, hasher='bcrypt')
user.password = hashed
user.save()

# Verify on login
if check_password(provided_password, user.password):
    # Login success
    pass
```

### Node.js (Express)
```javascript
const bcrypt = require('bcrypt');

// Hash on registration
const saltRounds = 12; // Cost ≥ 12 per PCI-DSS
const hashed = await bcrypt.hash(password, saltRounds);
user.password = hashed;
await user.save();

// Verify on login
const match = await bcrypt.compare(providedPassword, user.password);
if (match) {
    // Login success
}
```

### Go
```go
import "golang.org/x/crypto/bcrypt"

// Hash on registration (cost 12)
hash, _ := bcrypt.GenerateFromPassword([]byte(password), 12)
user.Password = string(hash)
db.Save(user)

// Verify on login
err := bcrypt.CompareHashAndPassword([]byte(user.Password), []byte(provided))
if err == nil {
    // Login success
}
```

## Acceptance Criteria
- [ ] bcrypt cost ≥ 12 used
- [ ] Passwords never logged or exported
- [ ] Plaintext passwords deleted after hash creation
- [ ] Password reset requires email verification

## Test Example
```python
def test_password_hashing():
    password = "TestPass123!"
    hashed = make_password(password)
    assert hashed != password
    assert check_password(password, hashed)
    assert not check_password("WrongPassword", hashed)
```
""",
    "pci-dss-encrypt-at-rest.md": """---
title: PCI-DSS Pattern - Encryption at Rest
type: compliance-pattern
tags: [compliance, pci-dss, security, encryption]
related:
  - [[.specs/memory.md]]
  - [[.ai-docs/COMPLIANCE-CHECKLIST-PCI-DSS.md]]
---

# PCI-DSS: Encrypt Sensitive Data at Rest (Requirement 3)

Cardholder data must be encrypted when stored (not in transit).

## Pattern: AES-256-GCM

### Python
```python
from cryptography.fernet import Fernet
import os

# Generate key once, store in env
KEY = os.environ['ENCRYPTION_KEY']
cipher = Fernet(KEY)

# Encrypt on storage
encrypted = cipher.encrypt(credit_card.encode())
db.save(card_number=encrypted)

# Decrypt on retrieval
decrypted = cipher.decrypt(encrypted).decode()
```

### Node.js
```javascript
const crypto = require('crypto');
const algorithm = 'aes-256-gcm';
const key = Buffer.from(process.env.ENCRYPTION_KEY, 'hex');

function encrypt(data) {
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipheriv(algorithm, key, iv);
  let encrypted = cipher.update(data, 'utf8', 'hex');
  encrypted += cipher.final('hex');
  return {
    iv: iv.toString('hex'),
    data: encrypted,
    tag: cipher.getAuthTag().toString('hex')
  };
}

function decrypt(encrypted) {
  const decipher = crypto.createDecipheriv(algorithm, key, Buffer.from(encrypted.iv, 'hex'));
  decipher.setAuthTag(Buffer.from(encrypted.tag, 'hex'));
  let decrypted = decipher.update(encrypted.data, 'hex', 'utf8');
  decrypted += decipher.final('utf8');
  return decrypted;
}
```

### Go
```go
import (
  "crypto/aes"
  "crypto/cipher"
  "crypto/rand"
  "io"
)

func Encrypt(key []byte, plaintext string) []byte {
  block, _ := aes.NewCipher(key)
  gcm, _ := cipher.NewGCM(block)
  nonce := make([]byte, gcm.NonceSize())
  io.ReadFull(rand.Reader, nonce)
  return gcm.Seal(nonce, nonce, []byte(plaintext), nil)
}

func Decrypt(key []byte, ciphertext []byte) (string, error) {
  block, _ := aes.NewCipher(key)
  gcm, _ := cipher.NewGCM(block)
  nonceSize := gcm.NonceSize()
  nonce, ciphertext := ciphertext[:nonceSize], ciphertext[nonceSize:]
  plaintext, err := gcm.Open(nil, nonce, ciphertext, nil)
  return string(plaintext), err
}
```

## Acceptance Criteria
- [ ] AES-256-GCM algorithm used
- [ ] Key ≥ 256 bits, stored in env var / secrets manager
- [ ] IV/nonce generated randomly per message
- [ ] AuthTag verified on decrypt
- [ ] No plaintext cardholder data in logs

## Test Example
```python
def test_encryption_decryption():
    card = "4111111111111111"
    encrypted = cipher.encrypt(card.encode())
    assert encrypted != card.encode()
    decrypted = cipher.decrypt(encrypted).decode()
    assert decrypted == card
```
""",
    "pci-dss-tls-enforcement.md": """---
title: PCI-DSS Pattern - TLS Enforcement
type: compliance-pattern
tags: [compliance, pci-dss, security, tls]
related:
  - [[.specs/memory.md]]
  - [[.ai-docs/COMPLIANCE-CHECKLIST-PCI-DSS.md]]
---

# PCI-DSS: Enforce TLS for Cardholder Data (Requirement 4)

All cardholder data transmitted across networks must use TLS 1.2 or higher.

## Pattern: Enforce HTTPS

### Python (Django)
```python
# settings.py
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### Node.js (Express)
```javascript
const https = require('https');
const fs = require('fs');

const options = {
  key: fs.readFileSync('path/to/key.pem'),
  cert: fs.readFileSync('path/to/cert.pem')
};

https.createServer(options, app).listen(443);

// Redirect HTTP to HTTPS
const http = require('http');
http.createServer((req, res) => {
  res.writeHead(301, {'Location': 'https://' + req.headers.host + req.url});
  res.end();
}).listen(80);
```

### Go
```go
import "net/http"

func main() {
  http.HandleFunc("/api/card", func(w http.ResponseWriter, r *http.Request) {
    if r.Header.Get("X-Forwarded-Proto") != "https" {
      http.Error(w, "HTTPS required", http.StatusBadRequest)
      return
    }
    // Handle request
  })
  
  // Serve HTTPS only
  http.ListenAndServeTLS(":443", "cert.pem", "key.pem", nil)
}
```

## Acceptance Criteria
- [ ] TLS 1.2 minimum enforced
- [ ] HSTS header set (min 1 year)
- [ ] Strong ciphers only (no SSLv3, TLSv1.0)
- [ ] Certificates valid and not self-signed for production
- [ ] HTTP redirects to HTTPS

## Test Example
```python
def test_tls_enforcement():
    response = client.get('http://example.com/api')
    assert response.status_code == 301
    assert response['Location'].startswith('https')
```
""",
    "hipaa-audit-logging.md": """---
title: HIPAA Pattern - Audit Logging
type: compliance-pattern
tags: [compliance, hipaa, security, logging]
related:
  - [[.specs/memory.md]]
  - [[.ai-docs/COMPLIANCE-CHECKLIST-HIPAA.md]]
---

# HIPAA: Audit Logging for PHI Access

All access to Protected Health Information (PHI) must be logged with user, timestamp, action.

## Pattern: Structured Audit Logs

### Python (Django)
```python
import logging
from django.contrib.auth.models import User

logger = logging.getLogger('hipaa_audit')

def access_patient_record(user: User, patient_id: int, action: str):
    # Log the access
    logger.info(f"PHI_ACCESS {{'user': '{user.username}', 'user_id': {user.id}, 'patient_id': {patient_id}, 'action': '{action}'}}")
    
    # Check authorization
    if not user.has_perm('view_patient', patient_id):
        logger.warning(f"UNAUTHORIZED_PHI_ACCESS: {user.username} tried to access {patient_id}")
        raise PermissionDenied
    
    # Retrieve PHI
    return PatientRecord.objects.get(id=patient_id)
```

### Node.js
```javascript
const winston = require('winston');

const auditLog = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.File({ filename: 'hipaa_audit.log' })
  ]
});

async function accessPatientRecord(user, patientId, action) {
  auditLog.info({
    event: 'PHI_ACCESS',
    user: user.username,
    user_id: user.id,
    patient_id: patientId,
    action: action,
    timestamp: new Date().toISOString(),
    ip_address: req.ip
  });
  
  if (!await user.canAccess(patientId)) {
    auditLog.warn({
      event: 'UNAUTHORIZED_PHI_ACCESS',
      user: user.username,
      attempted_patient: patientId
    });
    throw new Error('Unauthorized');
  }
  
  return await PatientRecord.findById(patientId);
}
```

### Go
```go
import "log"

type PHIAuditLog struct {
  Event       string    `json:"event"`
  User        string    `json:"user"`
  UserID      int       `json:"user_id"`
  PatientID   int       `json:"patient_id"`
  Action      string    `json:"action"`
  Timestamp   time.Time `json:"timestamp"`
  IPAddress   string    `json:"ip_address"`
}

func AccessPatientRecord(user *User, patientID int, action string) error {
  // Log access
  auditEntry := PHIAuditLog{
    Event:     "PHI_ACCESS",
    User:      user.Username,
    UserID:    user.ID,
    PatientID: patientID,
    Action:    action,
    Timestamp: time.Now(),
    IPAddress: r.RemoteAddr,
  }
  
  if !user.CanAccess(patientID) {
    auditEntry.Event = "UNAUTHORIZED_PHI_ACCESS"
    log.Printf("%+v", auditEntry)
    return fmt.Errorf("unauthorized")
  }
  
  log.Printf("%+v", auditEntry)
  return nil
}
```

## Acceptance Criteria
- [ ] All PHI access logged (user, timestamp, action)
- [ ] Unauthorized access attempts logged
- [ ] Audit logs immutable (append-only)
- [ ] Audit logs retained ≥ 6 years
- [ ] Logs reviewed regularly for anomalies

## Test Example
```python
def test_audit_logging(caplog):
    with caplog.at_level(logging.INFO):
        access_patient_record(user, patient_id=123, action='view')
    
    assert 'PHI_ACCESS' in caplog.text
    assert 'user123' in caplog.text
    assert 'patient_id' in caplog.text
```
""",
    "gdpr-data-retention.md": '''---
title: GDPR Pattern - Data Retention & Deletion
type: compliance-pattern
tags: [compliance, gdpr, security, privacy]
related:
  - [[.specs/memory.md]]
  - [[.ai-docs/COMPLIANCE-CHECKLIST-GDPR.md]]
---

# GDPR: Automatic Data Deletion After Retention Period

Personal data must be deleted when no longer needed (retention limit).

## Pattern: TTL-Based Auto-Deletion

### Python (Django + Celery)
```python
from django.utils import timezone
from django.db import models
from celery import shared_task
from datetime import timedelta

class UserData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    data = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    retention_days = models.IntegerField(default=365)  # GDPR retention
    
    def should_be_deleted(self):
        cutoff = timezone.now() - timedelta(days=self.retention_days)
        return self.created_at < cutoff

@shared_task
def delete_expired_user_data():
    """Delete data older than retention period."""
    expired = UserData.objects.filter(
        created_at__lt=timezone.now() - timedelta(days=365)
    )
    count = expired.count()
    expired.delete()
    logger.info(f"GDPR_RETENTION: Deleted {count} expired records")
    return count

# In settings.py, run daily via celery beat
from celery.schedules import crontab
app.conf.beat_schedule = {
    'delete-expired-user-data': {
        'task': 'myapp.tasks.delete_expired_user_data',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
}
```

### Node.js (Express + MongoDB)
```javascript
const schedule = require('node-schedule');
const UserData = require('./models/UserData');

async function deleteExpiredUserData() {
  const retentionDays = 365;
  const cutoffDate = new Date();
  cutoffDate.setDate(cutoffDate.getDate() - retentionDays);
  
  const result = await UserData.deleteMany({
    created_at: { $lt: cutoffDate }
  });
  
  console.log(`GDPR_RETENTION: Deleted ${result.deletedCount} expired records`);
}

// Run daily at 2 AM
schedule.scheduleJob('0 2 * * *', deleteExpiredUserData);
```

### Go
```go
import "github.com/robfig/cron/v3"

func DeleteExpiredUserData(db *sql.DB) error {
  retention := 365 * 24 * time.Hour
  cutoff := time.Now().Add(-retention)
  
  result, err := db.Exec(
    "DELETE FROM user_data WHERE created_at < $1",
    cutoff,
  )
  if err != nil {
    return err
  }
  
  deleted, _ := result.RowsAffected()
  log.Printf("GDPR_RETENTION: Deleted %d expired records", deleted)
  return nil
}

func main() {
  c := cron.New()
  c.AddFunc("0 2 * * *", func() { DeleteExpiredUserData(db) })
  c.Start()
}
```

## Acceptance Criteria
- [ ] Retention period defined per data type
- [ ] Automated deletion job runs daily
- [ ] Deletion is immutable (cannot restore)
- [ ] Deletion logged for audit trail
- [ ] User can request manual deletion at any time

## Test Example
```python
def test_data_retention_deletion():
    # Create data
    data = UserData.objects.create(user=user, data="test", retention_days=1)
    
    # Advance time
    data.created_at = timezone.now() - timedelta(days=2)
    data.save()
    
    # Run deletion
    delete_expired_user_data()
    
    # Verify deleted
    assert not UserData.objects.filter(id=data.id).exists()
```
''',
    "soc2-access-logging.md": """---
title: SOC2 Pattern - Access & Change Logging
type: compliance-pattern
tags: [compliance, soc2, security, logging]
related:
  - [[.specs/memory.md]]
  - [[.ai-docs/COMPLIANCE-CHECKLIST-SOC2.md]]
---

# SOC2: Access & Change Logging

All user access and system changes must be logged and auditable.

## Pattern: Comprehensive Audit Trail

### Python (Django)
```python
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import logging

audit_logger = logging.getLogger('audit')

@receiver(post_save, sender=User)
def log_user_access(sender, instance, created, **kwargs):
    if created:
        audit_logger.info(f"USER_CREATED: {instance.username} at {timezone.now()}")
    else:
        audit_logger.info(f"USER_MODIFIED: {instance.username} at {timezone.now()}")

@receiver(post_delete, sender=User)
def log_user_deletion(sender, instance, **kwargs):
    audit_logger.critical(f"USER_DELETED: {instance.username} at {timezone.now()}")

# API access logging middleware
class AuditLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        audit_logger.info(f"API_ACCESS: {request.user} {request.method} {request.path} {response.status_code}")
        return response
```

### Node.js
```javascript
const morgan = require('morgan');
const auditLog = require('./auditLog');

// HTTP request logging
app.use(morgan((tokens, req, res) => {
  const logEntry = {
    timestamp: new Date().toISOString(),
    user: req.user?.username || 'anonymous',
    method: tokens.method(req, res),
    path: tokens.url(req, res),
    status: tokens.status(req, res),
    response_time: tokens['response-time'](req, res) + 'ms'
  };
  auditLog.info('API_ACCESS', logEntry);
}), { immediate: false }));

// User creation
app.post('/users', async (req, res) => {
  const user = await User.create(req.body);
  auditLog.critical('USER_CREATED', { username: user.username });
  res.json(user);
});

// User deletion
app.delete('/users/:id', async (req, res) => {
  const user = await User.findById(req.params.id);
  await user.delete();
  auditLog.critical('USER_DELETED', { username: user.username });
  res.json({ ok: true });
});
```

### Go
```go
import "log"

func LogAccess(user string, action string, resource string, status string) {
  logEntry := map[string]interface{}{
    "timestamp": time.Now().Format(time.RFC3339),
    "user":      user,
    "action":    action,
    "resource":  resource,
    "status":    status,
  }
  auditLog.Printf("%+v", logEntry)
}

func (h *Handler) DeleteUser(w http.ResponseWriter, r *http.Request) {
  userID := r.URL.Query().Get("id")
  err := h.db.DeleteUser(userID)
  
  if err != nil {
    LogAccess(r.Header.Get("X-User"), "DELETE_USER", userID, "FAILED")
    http.Error(w, "Delete failed", http.StatusInternalServerError)
    return
  }
  
  LogAccess(r.Header.Get("X-User"), "DELETE_USER", userID, "SUCCESS")
  w.WriteHeader(http.StatusOK)
}
```

## Acceptance Criteria
- [ ] All API access logged (user, action, resource, time)
- [ ] All user changes logged (create, modify, delete)
- [ ] All authentication attempts logged
- [ ] Audit logs immutable and centralized
- [ ] Logs retained ≥ 1 year
- [ ] Anomalies detected via automated alerts

## Test Example
```python
def test_access_logging(caplog):
    with caplog.at_level(logging.INFO):
        client.get('/api/users', HTTP_AUTHORIZATION='Bearer token123')
    
    assert 'API_ACCESS' in caplog.text
    assert 'GET' in caplog.text
    assert '/api/users' in caplog.text
```
""",
}


def get_compliance_patterns(pack_keys):
    """Return patterns dict filtered by compliance pack keys."""
    result = {}

    # Map pack keys to pattern file prefixes
    pack_map = {
        "pci-dss": ["pci-dss"],
        "hipaa": ["hipaa"],
        "gdpr": ["gdpr"],
        "soc2": ["soc2"],
        # Add CCPA and ISO27001 patterns when ready
    }

    for pack_key in pack_keys:
        prefixes = pack_map.get(pack_key, [])
        for prefix in prefixes:
            for filename, content in COMPLIANCE_PATTERNS.items():
                if filename.startswith(prefix):
                    result[f".specs/compliance/{filename}"] = content

    return result


if __name__ == "__main__":
    # Test
    patterns = get_compliance_patterns(["pci-dss", "hipaa", "gdpr", "soc2"])
    print(f"Found {len(patterns)} patterns")
    for path in sorted(patterns.keys()):
        print(f"  {path}")

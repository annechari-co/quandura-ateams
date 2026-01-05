# Voice/Telephony Integration Research

## Summary

For a government phone-based intake system:

| Component | Recommendation | Rationale |
|-----------|---------------|-----------|
| Telephony | Twilio | FedRAMP authorized, reliable |
| STT | Deepgram Nova-2 | Best latency (300-500ms), accurate |
| LLM | Claude 3.5 Sonnet | Strong reasoning, streaming |
| TTS | ElevenLabs Turbo | Low latency, natural voices |

**Target latency**: <1000ms end-to-end
**Cost**: $0.06-0.12/minute

## Telephony Provider Comparison

| Provider | Gov Compliance | Cost/Min | Best For |
|----------|---------------|----------|----------|
| Twilio | FedRAMP | $0.0085-$0.014 | Federal agencies |
| Bandwidth | SOC 2, HIPAA | $0.004-$0.009 | State/local (cost) |
| Vonage | SOC 2, HIPAA | $0.006-$0.012 | Enterprise |
| Plivo | SOC 2 | $0.003-$0.008 | Cost-sensitive |

**Recommendation**: Twilio for federal, Bandwidth for state/local

## Speech-to-Text Comparison

| Provider | Latency | Accuracy | Cost/Min | Gov Compliance |
|----------|---------|----------|----------|----------------|
| Deepgram | 300-500ms | ~5-7% WER | $0.0043 | SOC 2, HIPAA |
| Google STT | 500-800ms | ~6-9% WER | $0.024 | FedRAMP High |
| AWS Transcribe | 800-1200ms | ~7-10% WER | $0.024 | FedRAMP High |
| Whisper API | 2-5s (batch) | ~5-8% WER | $0.006 | None |

**Recommendation**: Deepgram for real-time conversation

## Latency Budget

Total target: <1000ms

| Component | Budget |
|-----------|--------|
| Network (in) | 50-150ms |
| STT | 300-500ms |
| LLM | 200-500ms |
| TTS | 200-400ms |
| Network (out) | 50-150ms |

**Critical optimizations:**
- Stream everything (STT, LLM, TTS)
- Use WebSockets, not REST
- Deploy geographically close to users
- Implement interrupt detection

## Recording & Compliance

### Consent Laws
- **38 states**: One-party consent
- **12 states**: All-party consent (CA, FL, IL, MD, MA, MI, MT, NH, NV, PA, WA, CT)

**Best practice**: Always announce and get explicit consent

### Recording Requirements

| Requirement | Implementation |
|-------------|----------------|
| Encryption | AES-256 at rest, TLS in transit |
| Access control | Role-based, audit logged |
| Retention | Follow agency policy (typically 3-7 years) |
| Redaction | PII/PHI redaction in transcripts |
| Chain of custody | For investigative use |

### Pre-call Script
"This call may be recorded for quality assurance and investigative purposes. By continuing, you consent to recording."

## Accessibility Requirements (Section 508/ADA)

**Required features:**
- [ ] TTY/TDD detection and routing
- [ ] DTMF fallback for all voice inputs
- [ ] Multilingual support (Spanish minimum)
- [ ] Adjustable speech rate
- [ ] Extended timeout for responses
- [ ] Option to replay information
- [ ] Human escalation path

## Integration Architecture

```
Caller → Twilio → WebSocket Server → Deepgram STT (streaming)
                                           ↓
                                    Agent Orchestrator
                                           ↓
                                    Claude (streaming)
                                           ↓
                                    ElevenLabs TTS (streaming)
                                           ↓
                            Audio stream back to caller
```

## Cost Analysis

### Per-Minute Breakdown

| Component | Cost/Min |
|-----------|----------|
| Inbound Voice (Twilio) | $0.0085 |
| STT (Deepgram) | $0.0043 |
| LLM (Claude) | $0.015-0.045 |
| TTS (ElevenLabs) | $0.03-0.06 |
| Storage | $0.0002 |
| **Total** | **$0.058-0.118** |

### Monthly Estimates

| Volume | Minutes | Cost |
|--------|---------|------|
| Low | 5,000 | $290-590 |
| Medium | 25,000 | $1,450-2,950 |
| High | 50,000 | $2,900-5,900 |

### ROI
- Human agent: $0.33-0.67/minute
- Voice AI: $0.06-0.12/minute
- **Savings: ~85-95%** per minute handled

## Implementation Phases

**Phase 1 (4-6 weeks)**: Core Pipeline
- Twilio + WebSocket handler
- Deepgram STT integration
- Basic LLM integration
- ElevenLabs TTS
- Recording storage

**Phase 2 (6-8 weeks)**: Structured Intake
- State machine for questions
- Field validation
- Conditional branching
- Human escalation

**Phase 3 (4-6 weeks)**: Compliance
- Case management integration
- PII redaction
- Audit logging
- Multi-language support

**Phase 4 (4-6 weeks)**: Optimization
- Latency optimization
- Interrupt handling
- Custom vocabulary
- Analytics

---
*Research completed: 2025-01-05*

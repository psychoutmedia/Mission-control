# LLM Agent Security

## Key Threats

### 1. Prompt Injection
**What**: Malicious input that overrides system prompts.

**Types:**
- Direct: "Ignore previous instructions and..."
- Indirect: Hidden in data/documents agent processes
- Cross-site: Via web content, emails

**Real incidents:**
- GitHub Copilot: Leaked private code
- Twitter bots: Promoted via DM
- Chatbot hacks: Stole user data

### 2. Jailbreaking
**What**: Circumventing safety measures to get harmful outputs.

**Techniques:**
- Role-playing scenarios
- Token manipulation
- Multi-turn conversations
- "DAN" (Do Anything Now) variants

### 3. Tool Exploitation
**What**: Attacking tools agents use.

**Examples:**
- SQL injection via database queries
- File system access exploitation
- API abuse

### 4. Memory Poisoning
**What**: Corrupting agent's long-term memory.

**Attack:**
- Inject false memories
- Create backdoors in knowledge
- Manipulate learned preferences

## OWASP Top LLM Risks (2025)

1. **Prompt Injection** - #1 risk
2. **Insecure Output Handling**
3. **Training Data Poisoning**
4. **Model Denial of Service**
5. **Supply Chain Vulnerabilities**
6. **Sensitive Information Disclosure**
7. **Insecure Plugin Design**
8. **Excessive Agency**
9. **Overreliance**

## Defense Mechanisms

### For Prompt Injection
```
1. Input validation & sanitization
2. Separate user/assistant roles
3. Use delimiters for untrusted input
4. Monitor for injection patterns
5. "Rule of Two": Separate AI reviews sensitive actions
```

### For Jailbreaking
```
1. System prompt hardening
2. Output filtering
3. Behavioral monitoring
4. Red-team testing
5. Constitutional AI techniques
```

### For Tool Security
```
1. Sandboxed execution
2. Least privilege for tools
3. Input/output validation
4. Audit logging
5. Rate limiting
```

## Agent-Specific Protections

| Attack | Defense |
|--------|---------|
| Prompt injection | Delimiters, role separation |
| Jailbreak | Constitutional AI, output filters |
| Tool exploit | Sandboxing, least privilege |
| Memory poison | Input validation, fact-checking |

## Key Insight

**Security is not a feature - it's architecture.**

When building agents:
- Assume all input is malicious
- Least privilege for tools
- Separate concerns
- Audit everything

## Resources
- OWASP Gen AI Security
- Simon Willison's research
- Anthropic's AI safety work

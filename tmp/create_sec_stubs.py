#!/usr/bin/env python3
"""Create all 144 stub files for SEC-security category."""
import os

BASE = r"c:\Shiva\northstar\dictionary\tier-2-networking-security\SEC-security"

KEYWORDS = [
    (1, "The Security Problem in Software Engineering", "the-security-problem-in-software-engineering", "low"),
    (2, "CIA Triad (Confidentiality, Integrity, Availability)", "cia-triad", "low"),
    (3, "What Attackers Actually Do (Threat Actor Mindset)", "what-attackers-actually-do", "low"),
    (4, "OWASP Top 10 Overview", "owasp-top-10-overview", "low"),
    (5, "Cost of a Security Breach", "cost-of-a-security-breach", "low"),
    (6, "Why Security is Every Developer's Responsibility", "why-security-is-every-developers-responsibility", "low"),
    (7, "Defense in Depth", "defense-in-depth", "low"),
    (8, "Authentication vs Authorization vs Auditing", "authentication-vs-authorization-vs-auditing", "low"),
    (9, "Password Storage Anti-Pattern", "password-storage-anti-pattern", "low"),
    (10, "Hashing vs Encryption vs Encoding", "hashing-vs-encryption-vs-encoding", "low"),
    (11, "SQL Injection", "sql-injection", "low"),
    (12, "Cross-Site Scripting (XSS)", "cross-site-scripting-xss", "low"),
    (13, "Cross-Site Request Forgery (CSRF)", "cross-site-request-forgery-csrf", "low"),
    (14, "HTTP vs HTTPS - Why Encryption in Transit Matters", "http-vs-https-encryption-in-transit", "low"),
    (15, "TLS - Transport Layer Security Basics", "tls-transport-layer-security-basics", "low"),
    (16, "Cookies and Session Management Basics", "cookies-and-session-management-basics", "low"),
    (17, "Input Validation vs Output Encoding", "input-validation-vs-output-encoding", "low"),
    (18, "Principle of Least Privilege", "principle-of-least-privilege", "low"),
    (19, "Security Headers (HTTP)", "security-headers-http", "low"),
    (20, "Same-Origin Policy (SOP) and Browser Security Model", "same-origin-policy-browser-security-model", "low"),
    (21, "Secure Coding Practices - First Principles", "secure-coding-practices-first-principles", "low"),
    (22, "OWASP ZAP - Getting Started", "owasp-zap-getting-started", "low"),
    (23, "Setting Up a Local Security Testing Environment", "setting-up-local-security-testing-environment", "low"),
    (24, "Burp Suite Community - Introduction", "burp-suite-community-introduction", "low"),
    (25, "Security Mindset - Thinking Like an Attacker", "security-mindset-thinking-like-an-attacker", "low"),
    (26, "Common Security Terminology Glossary", "common-security-terminology-glossary", "low"),
    (27, "Vulnerability vs Exploit vs Attack", "vulnerability-vs-exploit-vs-attack", "low"),
    (28, "JSON Web Tokens (JWT)", "json-web-tokens-jwt", "low"),
    (29, "OAuth 2.0 Basics", "oauth-2-0-basics", "low"),
    (30, "CORS (Cross-Origin Resource Sharing)", "cors-cross-origin-resource-sharing", "low"),
    (31, "Content Security Policy (CSP)", "content-security-policy-csp", "low"),
    (32, "SQL Injection Prevention in Practice", "sql-injection-prevention-in-practice", "low"),
    (33, "XSS Prevention (Escaping, CSP, DOMPurify)", "xss-prevention-escaping-csp-dompurify", "low"),
    (34, "CSRF Prevention (CSRF Tokens, SameSite Cookies)", "csrf-prevention-csrf-tokens-samesite-cookies", "low"),
    (35, "Bcrypt for Password Hashing", "bcrypt-for-password-hashing", "low"),
    (36, "Secrets Management Basics (env vars, vaults)", "secrets-management-basics", "low"),
    (37, "Dependency Vulnerability Scanning (Snyk, OWASP DC)", "dependency-vulnerability-scanning", "low"),
    (38, "HTTPS Certificate Configuration", "https-certificate-configuration", "low"),
    (39, "Session Security (SameSite, Secure, HttpOnly)", "session-security-samesite-secure-httponly", "low"),
    (40, "API Security Basics", "api-security-basics", "low"),
    (41, "Security Code Review Checklist", "security-code-review-checklist", "low"),
    (42, "Error Handling and Information Disclosure", "error-handling-and-information-disclosure", "low"),
    (43, "Insecure Direct Object Reference (IDOR)", "insecure-direct-object-reference-idor", "low"),
    (44, "Security Testing with OWASP ZAP (Hands-On)", "security-testing-with-owasp-zap-hands-on", "low"),
    (45, "Authentication Method Decision Tree", "authentication-method-decision-tree", "low"),
    (46, "Hardcoded Credentials Anti-Pattern", "hardcoded-credentials-anti-pattern", "low"),
    (47, "Clickjacking and X-Frame-Options", "clickjacking-and-x-frame-options", "low"),
    (48, "HTTPS in Local Development", "https-in-local-development", "low"),
    (49, "Build a Secure Login System (Exercise)", "build-a-secure-login-system-exercise", "low"),
    (50, "Directory Traversal Vulnerability", "directory-traversal-vulnerability", "low"),
    (51, "Open Redirect Vulnerability", "open-redirect-vulnerability", "low"),
    (52, "File Upload Security", "file-upload-security", "low"),
    (53, "Mass Assignment Vulnerability", "mass-assignment-vulnerability", "low"),
    (54, "Security Monitoring Basics (audit logs)", "security-monitoring-basics-audit-logs", "low"),
    (55, "OWASP Top 10 in Practice Workshop", "owasp-top-10-in-practice-workshop", "low"),
    (56, "JWT Security Anti-Patterns (alg:none, weak secrets)", "jwt-security-anti-patterns", "low"),
    (57, "OAuth 2.0 Deep Dive (flows, scopes, PKCE)", "oauth-2-0-deep-dive-flows-scopes-pkce", "low"),
    (58, "OpenID Connect (OIDC)", "openid-connect-oidc", "low"),
    (59, "Threat Modeling with STRIDE", "threat-modeling-with-stride", "low"),
    (60, "SSRF (Server-Side Request Forgery)", "ssrf-server-side-request-forgery", "low"),
    (61, "XXE (XML External Entity) Injection", "xxe-xml-external-entity-injection", "low"),
    (62, "Deserialization Vulnerabilities", "deserialization-vulnerabilities", "low"),
    (63, "Race Condition Vulnerabilities (TOCTOU)", "race-condition-vulnerabilities-toctou", "low"),
    (64, "Prototype Pollution", "prototype-pollution", "low"),
    (65, "Path Traversal Advanced Cases", "path-traversal-advanced-cases", "low"),
    (66, "TLS Configuration Best Practices (cipher suites, TLS 1.3)", "tls-configuration-best-practices", "low"),
    (67, "Certificate Pinning", "certificate-pinning", "low"),
    (68, "SAST (Static Application Security Testing)", "sast-static-application-security-testing", "low"),
    (69, "DAST (Dynamic Application Security Testing)", "dast-dynamic-application-security-testing", "low"),
    (70, "Software Composition Analysis and Supply Chain Security", "software-composition-analysis-supply-chain-security", "low"),
    (71, "Secrets Rotation and Lifecycle Management", "secrets-rotation-and-lifecycle-management", "low"),
    (72, "Container Security Basics", "container-security-basics", "low"),
    (73, "Security Logging and Monitoring Best Practices", "security-logging-and-monitoring-best-practices", "low"),
    (74, "OAuth 2.0 Security Best Practices (RFC 9700)", "oauth-2-0-security-best-practices-rfc-9700", "low"),
    (75, "PCI-DSS Overview", "pci-dss-overview", "low"),
    (76, "GDPR Security Requirements", "gdpr-security-requirements", "low"),
    (77, "Security Testing in CI/CD Pipeline", "security-testing-in-cicd-pipeline", "low"),
    (78, "Penetration Testing Methodology", "penetration-testing-methodology", "low"),
    (79, "Security Control Performance Testing", "security-control-performance-testing", "low"),
    (80, "Authentication Mechanism Migration", "authentication-mechanism-migration", "low"),
    (81, "TLS 1.2 to TLS 1.3 Migration", "tls-1-2-to-tls-1-3-migration", "low"),
    (82, "OAuth 2.0 vs SAML Decision Framework", "oauth-2-0-vs-saml-decision-framework", "low"),
    (83, "Threat Modeling Workshop", "threat-modeling-workshop", "low"),
    (84, "Business Logic Vulnerabilities", "business-logic-vulnerabilities", "low"),
    (85, "Insufficient Logging Anti-Pattern", "insufficient-logging-anti-pattern", "low"),
    (86, "Heartbleed (2014)", "heartbleed-2014", "low"),
    (87, "Log4Shell (2021)", "log4shell-2021", "low"),
    (88, "SolarWinds SUNBURST Supply Chain Attack (2020)", "solarwinds-sunburst-supply-chain-attack-2020", "low"),
    (89, "Equifax Data Breach (2017)", "equifax-data-breach-2017", "low"),
    (90, "Advanced JWT Attacks (kid injection, jwks spoofing)", "advanced-jwt-attacks", "low"),
    (91, "Advanced XSS (DOM clobbering, mutation XSS)", "advanced-xss-dom-clobbering-mutation-xss", "low"),
    (92, "CORS Misconfiguration as Security Vulnerability", "cors-misconfiguration-as-security-vulnerability", "low"),
    (93, "SSRF to Internal Service Exploitation", "ssrf-to-internal-service-exploitation", "low"),
    (94, "OAuth 2.0 Implicit Flow Deprecation", "oauth-2-0-implicit-flow-deprecation", "low"),
    (95, "TLS Protocol Attacks (BEAST, POODLE, DROWN)", "tls-protocol-attacks-beast-poodle-drown", "low"),
    (96, "Certificate Transparency (CT) Logs", "certificate-transparency-ct-logs", "low"),
    (97, "HTTP Strict Transport Security (HSTS)", "http-strict-transport-security-hsts", "low"),
    (98, "CVSS Scoring System", "cvss-scoring-system", "low"),
    (99, "CVE and NVD - Vulnerability Database", "cve-and-nvd-vulnerability-database", "low"),
    (100, "Responsible Disclosure and Bug Bounty Programs", "responsible-disclosure-and-bug-bounty-programs", "low"),
    (101, "Security Incident Response (IR) Process", "security-incident-response-ir-process", "low"),
    (102, "Digital Forensics Basics (memory, disk, network)", "digital-forensics-basics", "low"),
    (103, "AWS Security Services (GuardDuty, IAM, WAF, Shield)", "aws-security-services", "low"),
    (104, "Kubernetes Security Fundamentals", "kubernetes-security-fundamentals", "low"),
    (105, "SAST in CI/CD (Semgrep, SonarQube, CodeQL)", "sast-in-cicd-semgrep-sonarqube-codeql", "low"),
    (106, "Security Observability and SIEM", "security-observability-and-siem", "low"),
    (107, "Security at Scale (WAF throughput, TLS offloading)", "security-at-scale-waf-throughput-tls-offloading", "low"),
    (108, "ISO 27001 Overview", "iso-27001-overview", "low"),
    (109, "SOC 2 Type II Basics", "soc-2-type-ii-basics", "low"),
    (110, "Chaos Engineering for Security (fault injection)", "chaos-engineering-for-security", "low"),
    (111, "Privilege Escalation Techniques and Mitigation", "privilege-escalation-techniques-and-mitigation", "low"),
    (112, "Zero Trust Architecture Introduction", "zero-trust-architecture-introduction", "low"),
    (113, "Red Team vs Blue Team vs Purple Team", "red-team-vs-blue-team-vs-purple-team", "low"),
    (114, "Zero Trust Architecture Design at Enterprise Scale", "zero-trust-architecture-design-at-enterprise-scale", "low"),
    (115, "DevSecOps Pipeline Design", "devsecops-pipeline-design", "low"),
    (116, "Security Champions Program Design", "security-champions-program-design", "low"),
    (117, "Enterprise Security Architecture (ESA)", "enterprise-security-architecture-esa", "low"),
    (118, "Company-Wide Secret Rotation Strategy", "company-wide-secret-rotation-strategy", "low"),
    (119, "Security Governance and Policy Framework", "security-governance-and-policy-framework", "low"),
    (120, "Threat Intelligence Integration", "threat-intelligence-integration", "low"),
    (121, "CSIRT Design and Playbook Development", "csirt-design-and-playbook-development", "low"),
    (122, "Security Metrics and Risk Quantification (FAIR)", "security-metrics-and-risk-quantification-fair", "low"),
    (123, "Supply Chain Security Strategy (SLSA Framework)", "supply-chain-security-strategy-slsa-framework", "low"),
    (124, "Platform Security Engineering", "platform-security-engineering", "low"),
    (125, "Multi-Cloud Security Architecture", "multi-cloud-security-architecture", "low"),
    (126, "Build vs Buy Security Decision Framework", "build-vs-buy-security-decision-framework", "low"),
    (127, "Security Architecture ADR Workshop", "security-architecture-adr-workshop", "low"),
    (128, "SIEM Architecture Design", "siem-architecture-design", "low"),
    (129, "Secure Software Development Lifecycle (SSDLC)", "secure-software-development-lifecycle-ssdlc", "low"),
    (130, "TLS 1.3 Protocol Design Rationale", "tls-1-3-protocol-design-rationale", "low"),
    (131, "OAuth 2.0 and OIDC Specification Design Decisions", "oauth-2-0-and-oidc-specification-design-decisions", "low"),
    (132, "OWASP Methodology and Security Science", "owasp-methodology-and-security-science", "low"),
    (133, "Secure by Design Principles (Saltzer and Schroeder)", "secure-by-design-principles-saltzer-and-schroeder", "low"),
    (134, "Formal Verification of Security Protocols", "formal-verification-of-security-protocols", "low"),
    (135, "Web Security Model (Browser Security Architecture)", "web-security-model-browser-security-architecture", "low"),
    (136, "Security Protocol Design Trade-offs", "security-protocol-design-trade-offs", "low"),
    (137, "Open Problems in Application Security", "open-problems-in-application-security", "low"),
    (138, "CVE Research and Responsible Disclosure Process", "cve-research-and-responsible-disclosure-process", "low"),
    (139, "Provable Security vs Practical Security", "provable-security-vs-practical-security", "low"),
    (140, "Adversarial Thinking as a Design Tool", "adversarial-thinking-as-a-design-tool", "low"),
    (141, "Trust Boundary Analysis", "trust-boundary-analysis", "low"),
    (142, "Assume-Breach Reasoning", "assume-breach-reasoning", "low"),
    (143, "Security as Contract Management (Pattern Bridge)", "security-as-contract-management-pattern-bridge", "low"),
    (144, "Threat Modeling as Universal Risk Analysis", "threat-modeling-as-universal-risk-analysis", "low"),
]

TEMPLATE = """---
id: {code}
title: "{title}"
category: "Security"
tier: tier-2-networking-security
folder: SEC-security
difficulty: "low"
depends_on:
used_by:
related:
tags:
  - security
status: draft
version: 0
layout: default
parent: "Security"
grand_parent: "Technical Dictionary"
nav_order: {nav}
permalink: /sec/{slug}/
---
"""

created = 0
for nav, title, slug, diff in KEYWORDS:
    code = f"SEC-{nav:03d}"
    filename = f"{code} - {title}.md"
    filepath = os.path.join(BASE, filename)
    if not os.path.exists(filepath):
        content = TEMPLATE.format(
            code=code, title=title, nav=nav, slug=slug
        )
        with open(filepath, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        created += 1

print(f"Created {created} new stub files (skipped existing).")
print(f"Total files in directory: {len([f for f in os.listdir(BASE) if f.endswith('.md') and f != 'index.md'])}")

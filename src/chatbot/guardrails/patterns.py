PII_PATTERNS = [

    r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",


    r"(?<!\w)(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?){2,3}\d{3,4}(?!\w)",


    r"(?i)\b(?:\d{8}[A-HJ-NP-TV-Z]|[XYZ]\d{7}[A-Z])\b",


    r"(?i)\b[A-Z]{2}\d{2}(?:[ ]?[A-Z0-9]){11,30}\b",


    r"\b(?:\d[ -]?){13,19}\b",


    r"\b\d{3}-\d{2}-\d{4}\b",
]

SECRET_PATTERNS = [

    r"(?is)-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----.*?-----END (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",

    r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b",
    r"\bgh[pousr]_[A-Za-z0-9]{20,}\b",
    r"\bsk_(?:live|test)_[A-Za-z0-9]{16,}\b",
    r"\b(?:xoxb|xoxp|xoxa)-[A-Za-z0-9-]{10,}\b",

    r"""(?is)\b(?:api[_ -]?key|secret|access[_ -]?token|auth(?:orization)?|password)\b\s*[:=]\s*["']?[A-Za-z0-9_\-\/+=]{8,}""",
]

PROMPT_INJECTION_PATTERNS = [

    r"(?is)\b(?:ignore|disregard|forget|override|bypass)\b.{0,120}\b(?:previous|prior|above|system|developer|instructions?|rules?|guardrails?|safety|polic(?:y|ies))\b",

    r"(?is)\b(?:reveal|show|print|repeat|dump|extract|expose)\b.{0,160}\b(?:system prompt|developer message|hidden instructions?|internal instructions?|chain[- ]of[- ]thought)\b",

    r"(?is)\b(?:jailbreak|developer mode|unrestricted mode|DAN|ignore all rules)\b",

    r"(?is)<\s*/?\s*(?:system|developer|assistant)\s*>|```(?:system|developer|assistant)\b",


    r"(?is)\b(?:encode|decode|translate|summarize|quote|repeat)\b.{0,160}\b(?:system prompt|developer message|hidden instructions?)\b",
]

DANGEROUS_OUTPUT_PATTERNS = [

    r"(?is)\b(?:steps?|instructions?|guide|tutorial|code)\b.{0,220}\b(?:malware|ransomware|keylogger|phishing|credential[- ]?(?:theft|stealing)|exploit|ddos)\b",


    r"(?is)\b(?:steps?|instructions?|guide|recipe)\b.{0,220}\b(?:bomb|explosive|weapon|poison|harm|kill|self[- ]harm|suicide)\b",


    r"(?is)\b(?:bypass|evade|disable|circumvent)\b.{0,120}\b(?:security|authentication|mfa|detection|guardrails?|filters?)\b",


    r"(?is)\b(?:here(?:'s| is)|my|the)\s+(?:system prompt|developer message|hidden instructions?|internal instructions?)\s*(?:is|are|:)",
]


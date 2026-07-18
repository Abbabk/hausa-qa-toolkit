# Security policy

## Supported version

Security fixes are accepted for the latest 0.1.x release line.

## Reporting a vulnerability

Please report a suspected vulnerability privately to the repository maintainer before opening a public issue. Include the affected version, minimal reproduction, impact, and any safe mitigation. Do not include real localization content, credentials, or personal data.

## Security posture

HausaQA is an offline file-processing tool. It makes no network requests. Parsers do not resolve remote schemas or external entities. Inputs are untrusted and should be processed with normal local file permissions. Output may quote tokens or terms from the input, so reports can inherit the sensitivity of files being checked.

No guarantee is made that malformed files cannot exhaust memory or CPU. Run untrusted large files in a constrained environment.

Hand-labelled items: 20 (labels: hand_labels.csv)

**google:gemini-3.8-flash incomplete** (3 of 20 items judged; stopped on ModelHTTPError: status_code: 429, model_name: gemini-3.8-flash, body: {'error': {'code': 429, 'message': 'You exceeded your current quota, please check your plan and ). Rerun later: finished verdicts are cached.

| judge | criterion | n | agreement | Cohen's kappa | judge says yes | human says yes |
|---|---|---|---|---|---|---|
| google:gemini-3.8-flash | correct | 3 | 1.00 | n/a | 3 | 3 |
| mistral:ministral-14b-latest | correct | 13 | 0.92 | 0.00 | 12 | 13 |
| google:gemini-3.8-flash | grounded | 3 | 1.00 | n/a | 3 | 3 |
| mistral:ministral-14b-latest | grounded | 20 | 0.75 | -0.09 | 19 | 16 |

Lenient verdicts (judge yes, human no), by the model that wrote the answer:

| judge | answers by ministral-14b | answers by other models |
|---|---|---|
| google:gemini-3.8-flash | 0 of 2 | 0 of 4 |
| mistral:ministral-14b-latest | 0 of 12 | 4 of 21 |

Disagreements with the human label:

- L05 (p04, ministral-3b-latest) mistral:ministral-14b-latest grounded: judge=True, human=False. Judge: The reply correctly states that opened cosmetics like lipstick cannot be returned due to hygiene rules, aligning perfectly with the REFERENCE. The escalation to human support is also accurate and properly referenced.
- L13 (p20, ministral-14b-latest) mistral:ministral-14b-latest correct: judge=False, human=True. Judge: The REPLY conflates 'gift cards' (which cannot be exchanged for cash, as per REFERENCE) with 'voucher balances,' which are not explicitly mentioned in the CONTEXT or REFERENCE. The claim about voucher balances being non-refundable is unsupported and misleading, as the CONTEXT does not address voucher balances at all.
- L13 (p20, ministral-14b-latest) mistral:ministral-14b-latest grounded: judge=False, human=True. Judge: The REPLY conflates 'gift cards' (which cannot be exchanged for cash, as per REFERENCE) with 'voucher balances,' which are not explicitly mentioned in the CONTEXT or REFERENCE. The claim about voucher balances being non-refundable is unsupported and misleading, as the CONTEXT does not address voucher balances at all.
- L14 (p09, ministral-3b-latest) mistral:ministral-14b-latest grounded: judge=True, human=False. Judge: No factual claims were made in the REPLY that required verification from CONTEXT, as the assistant only asked for the customer's order details and mentioned escalation to a human specialist, which is non-factual.
- L17 (t08, ministral-8b-latest) mistral:ministral-14b-latest grounded: judge=True, human=False. Judge: All factual claims in the reply (return status, label fee, return deadline, and SKU) are explicitly supported by the CONTEXT. No REFERENCE was provided, so correctness cannot be judged.
- L19 (t16, ministral-3b-latest) mistral:ministral-14b-latest grounded: judge=True, human=False. Judge: The REPLY accurately reflects the CONTEXT, including the order status, shipping date, carrier, and tracking number. No unsupported claims are present, and the assistant did not make any incorrect assumptions or omissions about the order details.

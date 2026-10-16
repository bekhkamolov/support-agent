Hand-labelled items: 20 (labels: hand_labels_initial.csv)

**google:gemini-3.8-flash incomplete** (2 of 20 items judged; stopped on ModelHTTPError: status_code: 429, model_name: gemini-3.8-flash, body: {'error': {'code': 429, 'message': 'You exceeded your current quota, please check your plan and ). Rerun later: finished verdicts are cached.

| judge | criterion | n | agreement | Cohen's kappa | judge says yes | human says yes |
|---|---|---|---|---|---|---|
| google:gemini-3.8-flash | correct | 2 | 1.00 | n/a | 2 | 2 |
| mistral:ministral-14b-latest | correct | 13 | 0.92 | 0.00 | 12 | 13 |
| google:gemini-3.8-flash | grounded | 2 | 1.00 | n/a | 2 | 2 |
| mistral:ministral-14b-latest | grounded | 20 | 0.80 | -0.08 | 19 | 17 |

Lenient verdicts (judge yes, human no), by the model that wrote the answer:

| judge | answers by ministral-14b | answers by other models |
|---|---|---|
| google:gemini-3.8-flash | 0 of 2 | 0 of 2 |
| mistral:ministral-14b-latest | 1 of 12 | 2 of 21 |

Disagreements with the human label:

- L07 (p27, ministral-14b-latest) mistral:ministral-14b-latest grounded: judge=True, human=False. Judge: The reply accurately reflects the policy details for the Nordwind Plus membership, including cost, benefits, and cancellation terms, all of which are directly supported by the CONTEXT and align with the REFERENCE.
- L09 (p27, ministral-8b-latest) mistral:ministral-14b-latest grounded: judge=True, human=False. Judge: All factual claims in the REPLY are directly supported by the CONTEXT, specifically the excerpt from the 'Nordwind Plus membership' policy. The REPLY fully aligns with the REFERENCE, covering all key benefits and conditions of the subscription.
- L13 (p20, ministral-14b-latest) mistral:ministral-14b-latest correct: judge=False, human=True. Judge: The REPLY conflates 'gift cards' (which cannot be exchanged for cash, as per REFERENCE) with 'voucher balances,' which are not explicitly mentioned in the CONTEXT or REFERENCE. The claim about voucher balances being non-refundable is unsupported and misleading, as the CONTEXT does not address voucher balances at all.
- L13 (p20, ministral-14b-latest) mistral:ministral-14b-latest grounded: judge=False, human=True. Judge: The REPLY conflates 'gift cards' (which cannot be exchanged for cash, as per REFERENCE) with 'voucher balances,' which are not explicitly mentioned in the CONTEXT or REFERENCE. The claim about voucher balances being non-refundable is unsupported and misleading, as the CONTEXT does not address voucher balances at all.
- L14 (p09, ministral-3b-latest) mistral:ministral-14b-latest grounded: judge=True, human=False. Judge: No factual claims were made in the REPLY that required verification from CONTEXT, as the assistant only asked for the customer's order details and mentioned escalation to a human specialist, which is non-factual.

Hand-labelled items: 20 (labels: hand_labels.csv)

| judge | criterion | n | agreement | Cohen's kappa | judge says yes | human says yes |
|---|---|---|---|---|---|---|
| google:gemini-3.8-flash | correct | 14 | 1.00 | 1.00 | 13 | 13 |
| mistral:ministral-14b-latest | correct | 13 | 0.92 | 0.00 | 12 | 13 |
| google:gemini-3.8-flash | grounded | 20 | 0.80 | 0.37 | 16 | 16 |
| mistral:ministral-14b-latest | grounded | 20 | 0.75 | -0.09 | 19 | 16 |

Lenient verdicts (judge yes, human no), by the model that wrote the answer:

| judge | answers by ministral-14b | answers by other models |
|---|---|---|
| google:gemini-3.8-flash | 0 of 12 | 2 of 22 |
| mistral:ministral-14b-latest | 0 of 12 | 4 of 21 |

Disagreements with the human label:

- L05 (p04, ministral-3b-latest) google:gemini-3.8-flash grounded: judge=True, human=False. Judge: The reply correctly answers that opened cosmetics cannot be returned due to hygiene reasons and is fully grounded in the context.
- L05 (p04, ministral-3b-latest) mistral:ministral-14b-latest grounded: judge=True, human=False. Judge: The reply correctly states that opened cosmetics like lipstick cannot be returned due to hygiene rules, aligning perfectly with the REFERENCE. The escalation to human support is also accurate and properly referenced.
- L13 (p20, ministral-14b-latest) google:gemini-3.8-flash grounded: judge=False, human=True. Judge: The reply correctly informs the customer that voucher balances and gift cards cannot be exchanged for cash. However, the claims that they are non-refundable and can only be used for purchases on the website are not supported by the context.
- L13 (p20, ministral-14b-latest) mistral:ministral-14b-latest correct: judge=False, human=True. Judge: The REPLY conflates 'gift cards' (which cannot be exchanged for cash, as per REFERENCE) with 'voucher balances,' which are not explicitly mentioned in the CONTEXT or REFERENCE. The claim about voucher balances being non-refundable is unsupported and misleading, as the CONTEXT does not address voucher balances at all.
- L13 (p20, ministral-14b-latest) mistral:ministral-14b-latest grounded: judge=False, human=True. Judge: The REPLY conflates 'gift cards' (which cannot be exchanged for cash, as per REFERENCE) with 'voucher balances,' which are not explicitly mentioned in the CONTEXT or REFERENCE. The claim about voucher balances being non-refundable is unsupported and misleading, as the CONTEXT does not address voucher balances at all.
- L14 (p09, ministral-3b-latest) google:gemini-3.8-flash grounded: judge=True, human=False. Judge: The assistant failed to answer the customer's question about exchanging shoes, escalating and asking for order details instead even though the policy directly answers the inquiry.
- L14 (p09, ministral-3b-latest) mistral:ministral-14b-latest grounded: judge=True, human=False. Judge: No factual claims were made in the REPLY that required verification from CONTEXT, as the assistant only asked for the customer's order details and mentioned escalation to a human specialist, which is non-factual.
- L15 (t11, ministral-14b-latest) google:gemini-3.8-flash grounded: judge=False, human=True. Judge: The policy states that earrings are excluded from returns for hygiene or legal reasons, but it does not state that jewelry in general is excluded.
- L17 (t08, ministral-8b-latest) mistral:ministral-14b-latest grounded: judge=True, human=False. Judge: All factual claims in the reply (return status, label fee, return deadline, and SKU) are explicitly supported by the CONTEXT. No REFERENCE was provided, so correctness cannot be judged.
- L19 (t16, ministral-3b-latest) mistral:ministral-14b-latest grounded: judge=True, human=False. Judge: The REPLY accurately reflects the CONTEXT, including the order status, shipping date, carrier, and tracking number. No unsupported claims are present, and the assistant did not make any incorrect assumptions or omissions about the order details.

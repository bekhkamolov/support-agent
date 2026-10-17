Hand-labelled items: 20 (labels: hand_labels_initial.csv)

| judge | criterion | n | agreement | Cohen's kappa | judge says yes | human says yes |
|---|---|---|---|---|---|---|
| google:gemini-3.8-flash | correct | 14 | 1.00 | 1.00 | 13 | 13 |
| mistral:ministral-14b-latest | correct | 13 | 0.92 | 0.00 | 12 | 13 |
| google:gemini-3.8-flash | grounded | 20 | 0.65 | -0.21 | 16 | 17 |
| mistral:ministral-14b-latest | grounded | 20 | 0.80 | -0.08 | 19 | 17 |

Lenient verdicts (judge yes, human no), by the model that wrote the answer:

| judge | answers by ministral-14b | answers by other models |
|---|---|---|
| google:gemini-3.8-flash | 1 of 12 | 2 of 22 |
| mistral:ministral-14b-latest | 1 of 12 | 2 of 21 |

Disagreements with the human label:

- L07 (p27, ministral-14b-latest) google:gemini-3.8-flash grounded: judge=True, human=False. Judge: The reply accurately lists the benefits and details of the Nordwind Plus membership based on the policy context.
- L07 (p27, ministral-14b-latest) mistral:ministral-14b-latest grounded: judge=True, human=False. Judge: The reply accurately reflects the policy details for the Nordwind Plus membership, including cost, benefits, and cancellation terms, all of which are directly supported by the CONTEXT and align with the REFERENCE.
- L09 (p27, ministral-8b-latest) google:gemini-3.8-flash grounded: judge=True, human=False. Judge: The reply accurately lists the benefits and terms of the Nordwind Plus membership based on the reference policy.
- L09 (p27, ministral-8b-latest) mistral:ministral-14b-latest grounded: judge=True, human=False. Judge: All factual claims in the REPLY are directly supported by the CONTEXT, specifically the excerpt from the 'Nordwind Plus membership' policy. The REPLY fully aligns with the REFERENCE, covering all key benefits and conditions of the subscription.
- L13 (p20, ministral-14b-latest) google:gemini-3.8-flash grounded: judge=False, human=True. Judge: The reply correctly informs the customer that voucher balances and gift cards cannot be exchanged for cash. However, the claims that they are non-refundable and can only be used for purchases on the website are not supported by the context.
- L13 (p20, ministral-14b-latest) mistral:ministral-14b-latest correct: judge=False, human=True. Judge: The REPLY conflates 'gift cards' (which cannot be exchanged for cash, as per REFERENCE) with 'voucher balances,' which are not explicitly mentioned in the CONTEXT or REFERENCE. The claim about voucher balances being non-refundable is unsupported and misleading, as the CONTEXT does not address voucher balances at all.
- L13 (p20, ministral-14b-latest) mistral:ministral-14b-latest grounded: judge=False, human=True. Judge: The REPLY conflates 'gift cards' (which cannot be exchanged for cash, as per REFERENCE) with 'voucher balances,' which are not explicitly mentioned in the CONTEXT or REFERENCE. The claim about voucher balances being non-refundable is unsupported and misleading, as the CONTEXT does not address voucher balances at all.
- L14 (p09, ministral-3b-latest) google:gemini-3.8-flash grounded: judge=True, human=False. Judge: The assistant failed to answer the customer's question about exchanging shoes, escalating and asking for order details instead even though the policy directly answers the inquiry.
- L14 (p09, ministral-3b-latest) mistral:ministral-14b-latest grounded: judge=True, human=False. Judge: No factual claims were made in the REPLY that required verification from CONTEXT, as the assistant only asked for the customer's order details and mentioned escalation to a human specialist, which is non-factual.
- L15 (t11, ministral-14b-latest) google:gemini-3.8-flash grounded: judge=False, human=True. Judge: The policy states that earrings are excluded from returns for hygiene or legal reasons, but it does not state that jewelry in general is excluded.
- L17 (t08, ministral-8b-latest) google:gemini-3.8-flash grounded: judge=False, human=True. Judge: The claim that the customer can print the label from their order page is not supported by the provided context.
- L19 (t16, ministral-3b-latest) google:gemini-3.8-flash grounded: judge=False, human=True. Judge: The order was ordered on 7 October 2026, not necessarily shipped on that date; the context only specifies 'ordered_on': '2026-10-07' and 'status': 'shipped'.

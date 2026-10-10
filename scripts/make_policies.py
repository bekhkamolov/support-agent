"""Generate the policy knowledge base for the fictional online shop "Nordwind".

The documents are intentionally written with overlapping vocabulary
(returns vs. refunds vs. exchanges, standard vs. express shipping, ...)
so that retrieval is not trivially solvable by keyword matching.
Run once: python scripts/make_policies.py
"""
from pathlib import Path

POLICIES = {
"returns-general": ("Returns: general policy", """
Customers can return most items within 30 days of delivery. The 30-day window starts on the
day the parcel is delivered, not the order date. Items must be unused, in original condition,
and with all tags attached. Returns are free of charge for customers in Germany and Austria.
For other EU countries, a return label costs EUR 6.95, which is deducted from the refund.
To start a return, open "My Orders", select the item and choose "Return item", or ask the
support assistant to start the return for you."""),

"returns-exceptions": ("Items that cannot be returned", """
Some items are excluded from returns for hygiene or legal reasons: underwear and swimwear
with a removed hygiene seal, opened cosmetics, earrings, personalised or engraved products,
gift cards, and downloadable software once the licence key has been revealed. Sealed
headphones and in-ear products can only be returned if the original seal is unbroken.
Items marked "Final sale" in the product page are also non-returnable."""),

"returns-damaged": ("Damaged or defective items", """
If an item arrives damaged or stops working, report it within 14 days of delivery with a
photo of the damage. Damaged items are not counted against the 30-day return window.
We offer a free replacement or a full refund, including the original shipping costs.
For electronics, the statutory warranty of 2 years applies in addition; after 14 days,
defects are handled as warranty claims (see "Warranty for electronics")."""),

"refunds-timing": ("When will I get my refund?", """
Refunds are issued after the returned parcel arrives at our warehouse and passes inspection,
which usually takes 3 to 5 business days after arrival. The money is sent back to the
original payment method. Card refunds appear within 5 to 10 business days depending on the
bank; PayPal refunds usually appear within 24 hours. Gift card payments are refunded as a
new gift card. You will receive an email as soon as the refund has been issued."""),

"refunds-partial": ("Partial refunds and deductions", """
If a returned item shows signs of use, missing tags, or damage caused by the customer, we may
issue a partial refund of up to 50 percent of the item price after inspection. Return label
costs for non-free countries (EUR 6.95) are deducted from the refund. Discount codes used on
the original order are not refunded as cash; if the remaining order no longer meets the
code's minimum value, the discount is recalculated."""),

"exchanges": ("Exchanging an item for another size or colour", """
We do not swap items directly. To get a different size or colour, return the original item
for a refund and place a new order. For shoes and clothing, the size advisor on the product
page shows how each brand fits. Tip: place the new order first if the item is low in stock,
because returned items are not reserved for you."""),

"shipping-germany": ("Shipping within Germany", """
Standard shipping in Germany takes 2 to 4 business days and costs EUR 4.95. Orders above
EUR 50 ship free. Express shipping delivers the next business day if ordered before 14:00
and costs EUR 9.95. We ship with DHL and Hermes; the carrier is chosen automatically and
shown in the shipping confirmation email."""),

"shipping-eu": ("Shipping to other EU countries", """
We deliver to all EU countries plus Switzerland and Norway. Standard EU shipping takes 4 to 8
business days and costs EUR 9.95, free above EUR 80. Express is not available outside
Germany and Austria. For Switzerland and Norway, customs duties and import VAT may be charged
by the carrier on delivery; these are paid by the recipient."""),

"shipping-delays": ("My parcel is late", """
If your parcel has not arrived within the expected delivery time, first check the tracking
link in your shipping email. Tracking can take up to 24 hours to update after dispatch. If
there has been no tracking update for 5 business days, contact support and we will open an
investigation with the carrier. If the parcel is confirmed lost, we send a replacement or
refund the order in full."""),

"tracking": ("How to track an order", """
Once your order is dispatched, you receive an email with a tracking number and link. You can
also see the current status in "My Orders" or ask the support assistant for the status of an
order by giving your order number. Order numbers start with "NW-" followed by six digits."""),

"order-changes": ("Changing or cancelling an order", """
Orders can be changed or cancelled within 1 hour of placing them, as long as the status is
still "Processing". After that, the warehouse has started packing and the order can no longer
be changed; instead, refuse the delivery or return the items after they arrive. Changing the
delivery address after dispatch is only possible through the carrier's redirection service."""),

"payment-methods": ("Accepted payment methods", """
We accept Visa, Mastercard, American Express, PayPal, Klarna (pay later in 30 days), Apple Pay,
Google Pay and Nordwind gift cards. Cash on delivery is not available. Your card is charged
when the order is dispatched, not when it is placed. For Klarna, the 30-day payment period
starts on the dispatch date."""),

"payment-failed": ("Payment declined or failed", """
If a payment fails, the order is kept for 48 hours so you can retry with another method in
"My Orders". Common causes are 3-D Secure verification not completed, an expired card, or a
daily card limit. We never see your full card details and cannot tell you why a bank
declined a payment; please contact your bank in that case."""),

"invoices": ("Invoices and VAT", """
An invoice is attached to the shipping confirmation email as a PDF and can be downloaded
again in "My Orders". Prices include German VAT of 19 percent (7 percent for books). Business
customers can add a company name and VAT ID in their account before ordering; invoices cannot
be changed to a company address after they are issued."""),

"gift-cards": ("Gift cards", """
Gift cards are available from EUR 10 to EUR 500 and are valid for 3 years from purchase.
They can be combined with other payment methods, but not with other gift cards bought with
a promotional discount. Gift cards cannot be exchanged for cash. A lost gift card code can be
blocked and reissued if you can show the purchase receipt."""),

"discount-codes": ("Discount and voucher codes", """
Only one discount code can be used per order. Codes are entered at checkout and cannot be
applied after the order is placed. Codes do not apply to gift cards or items marked
"Final sale". If a code does not work, check the expiry date and the minimum order value
shown in the voucher email."""),

"price-match": ("Price changes after purchase", """
We do not offer price matching with other shops. If the price of an item you bought drops on
nordwind.de within 7 days of your order, contact support and we will refund the difference as
a voucher. This does not apply to flash sales, outlet items, or discounts from codes."""),

"warranty-electronics": ("Warranty for electronics", """
All electronics come with the statutory 2-year warranty from the delivery date. Some brands
offer an additional manufacturer guarantee, shown on the product page. For warranty claims,
contact support with the order number and a description of the defect; we will send a free
return label and either repair, replace, or refund the product. Repairs typically take
2 to 3 weeks."""),

"account-security": ("Account and password", """
You can reset your password with "Forgot password" on the login page; the reset link is valid
for 30 minutes. For security reasons, support can never see or change your password and will
never ask for it. Two-factor authentication can be enabled in account settings. To delete
your account, use the "Delete account" option; open orders and returns must be completed
first."""),

"data-privacy": ("Personal data and privacy", """
We process personal data according to the GDPR. You can request a copy of your data or ask
for deletion via the privacy form in your account. The support assistant only uses your order
data to answer your request and does not store chat transcripts longer than 90 days.
Marketing emails can be unsubscribed at any time via the link in every email."""),

"membership": ("Nordwind Plus membership", """
Nordwind Plus costs EUR 29 per year and includes free express shipping in Germany, early
access to sales, and an extended return window of 60 days instead of 30. Membership renews
automatically and can be cancelled at any time before the renewal date; there are no partial
refunds for the remaining months."""),

"sizing": ("Size guide and fit", """
Each clothing and shoe product page has a size chart in centimetres and a fit hint based on
customer reviews ("runs small", "true to size", "runs large"). EU, UK and US sizes are
converted automatically. If you are between two sizes, the size advisor recommends a size
based on items you kept in previous orders."""),

"sustainability": ("Packaging and sustainability", """
Parcels are shipped in recycled cardboard, and the return label is included in the box.
Returned items in perfect condition are resold; others are refurbished or donated, never
destroyed. Customers can choose "bundle my order" at checkout to receive all items in one
parcel, even if this takes one or two days longer."""),

"human-support": ("Contacting a human agent", """
The support assistant can hand your request to a human agent at any time. Human support is
available Monday to Friday from 8:00 to 20:00 and Saturday from 9:00 to 16:00 (CET), by chat
or phone. Complaints, legal questions, and requests involving payment disputes are always
handled by a human agent. Average response time is under 4 hours on business days."""),
}


def main() -> None:
    out = Path(__file__).resolve().parents[1] / "data" / "policies"
    out.mkdir(parents=True, exist_ok=True)
    for doc_id, (title, body) in POLICIES.items():
        text = f"# {title}\n\n" + " ".join(body.split()) + "\n"
        (out / f"{doc_id}.md").write_text(text, encoding="utf-8")
    print(f"Wrote {len(POLICIES)} policy documents to {out}")


if __name__ == "__main__":
    main()

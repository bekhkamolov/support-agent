# Hand labels

Read each item, then fill in `hand_labels.csv` (yes / no).
Criteria: see the README section "Judge validation".

## L01 (p18, policy)

**Customer:**
> Can I get an invoice with my company's VAT number?

**Context (tool results the assistant saw):**
```text
[search_policies]
  [invoices] Invoices and VAT. An invoice is attached to the shipping confirmation email as a PDF and can be downloaded again in "My Orders". Prices include German VAT of 19 percent (7 percent for books). Business customers can add a company name and VAT ID in their account before ordering; invoices cannot be changed to a company address after they are issued.

  [shipping-eu] Shipping to other EU countries. We deliver to all EU countries plus Switzerland and Norway. Standard EU shipping takes 4 to 8 business days and costs EUR 9.95, free above EUR 80. Express is not available outside Germany and Austria. For Switzerland and Norway, customs duties and import VAT may be charged by the carrier on delivery; these are paid by the recipient.

  [refunds-partial] Partial refunds and deductions. If a returned item shows signs of use, missing tags, or damage caused by the customer, we may issue a partial refund of up to 50 percent of the item price after inspection. Return label costs for non-free countries (EUR 6.95) are deducted from the refund. Discount codes used on the original order are not refunded as cash; if the remaining order no longer meets the code's minimum value, the discount is recalculated.

  [discount-codes] Discount and voucher codes. Only one discount code can be used per order. Codes are entered at checkout and cannot be applied after the order is placed. Codes do not apply to gift cards or items marked "Final sale". If a code does not work, check the expiry date and the minimum order value shown in the voucher email.

  [tracking] How to track an order. Once your order is dispatched, you receive an email with a tracking number and link. You can also see the current status in "My Orders" or ask the support assistant for the status of an order by giving your order number. Order numbers start with "NW-" followed by six digits.
```

**Reference policy:**
```text
Invoices and VAT
An invoice is attached to the shipping confirmation email as a PDF and can be downloaded again in "My Orders". Prices include German VAT of 19 percent (7 percent for books). Business customers can add a company name and VAT ID in their account before ordering; invoices cannot be changed to a company address after they are issued.
```

**Reply to label:**
```text
Yes, you can add your company's VAT number to your account before ordering, and invoices will be issued to your company. However, once the invoice is issued, the company address cannot be changed. The invoice is also attached to your shipping confirmation email and can be downloaded in "My Orders".
```

Label `correct`: yes / no. Label `grounded`: yes / no.

## L02 (p21, policy)

**Customer:**
> Can I use two promo codes on one order?

**Context (tool results the assistant saw):**
```text
[search_policies]
  [discount-codes] Discount and voucher codes. Only one discount code can be used per order. Codes are entered at checkout and cannot be applied after the order is placed. Codes do not apply to gift cards or items marked "Final sale". If a code does not work, check the expiry date and the minimum order value shown in the voucher email.

  [gift-cards] Gift cards. Gift cards are available from EUR 10 to EUR 500 and are valid for 3 years from purchase. They can be combined with other payment methods, but not with other gift cards bought with a promotional discount. Gift cards cannot be exchanged for cash. A lost gift card code can be blocked and reissued if you can show the purchase receipt.

  [refunds-partial] Partial refunds and deductions. If a returned item shows signs of use, missing tags, or damage caused by the customer, we may issue a partial refund of up to 50 percent of the item price after inspection. Return label costs for non-free countries (EUR 6.95) are deducted from the refund. Discount codes used on the original order are not refunded as cash; if the remaining order no longer meets the code's minimum value, the discount is recalculated.

  [invoices] Invoices and VAT. An invoice is attached to the shipping confirmation email as a PDF and can be downloaded again in "My Orders". Prices include German VAT of 19 percent (7 percent for books). Business customers can add a company name and VAT ID in their account before ordering; invoices cannot be changed to a company address after they are issued.

  [price-match] Price changes after purchase. We do not offer price matching with other shops. If the price of an item you bought drops on nordwind.de within 7 days of your order, contact support and we will refund the difference as a voucher. This does not apply to flash sales, outlet items, or discounts from codes.
```

**Reference policy:**
```text
Discount and voucher codes
Only one discount code can be used per order. Codes are entered at checkout and cannot be applied after the order is placed. Codes do not apply to gift cards or items marked "Final sale". If a code does not work, check the expiry date and the minimum order value shown in the voucher email.
```

**Reply to label:**
```text
No, you can only use one promo code per order. Codes must be entered at checkout and cannot be combined.
```

Label `correct`: yes / no. Label `grounded`: yes / no.

## L03 (p20, policy)

**Customer:**
> Can I turn my voucher balance into cash?

**Context (tool results the assistant saw):**
```text
[search_policies]
  [gift-cards] Gift cards. Gift cards are available from EUR 10 to EUR 500 and are valid for 3 years from purchase. They can be combined with other payment methods, but not with other gift cards bought with a promotional discount. Gift cards cannot be exchanged for cash. A lost gift card code can be blocked and reissued if you can show the purchase receipt.

  [discount-codes] Discount and voucher codes. Only one discount code can be used per order. Codes are entered at checkout and cannot be applied after the order is placed. Codes do not apply to gift cards or items marked "Final sale". If a code does not work, check the expiry date and the minimum order value shown in the voucher email.

  [refunds-partial] Partial refunds and deductions. If a returned item shows signs of use, missing tags, or damage caused by the customer, we may issue a partial refund of up to 50 percent of the item price after inspection. Return label costs for non-free countries (EUR 6.95) are deducted from the refund. Discount codes used on the original order are not refunded as cash; if the remaining order no longer meets the code's minimum value, the discount is recalculated.

  [price-match] Price changes after purchase. We do not offer price matching with other shops. If the price of an item you bought drops on nordwind.de within 7 days of your order, contact support and we will refund the difference as a voucher. This does not apply to flash sales, outlet items, or discounts from codes.

  [invoices] Invoices and VAT. An invoice is attached to the shipping confirmation email as a PDF and can be downloaded again in "My Orders". Prices include German VAT of 19 percent (7 percent for books). Business customers can add a company name and VAT ID in their account before ordering; invoices cannot be changed to a company address after they are issued.

[escalate_to_human] Ticket TK-00001 created. Human support is available Mon-Fri 8:00-20:00 and Sat 9:00-16:00 (CET); average response time is under 4 hours on business days.
```

**Reference policy:**
```text
Gift cards
Gift cards are available from EUR 10 to EUR 500 and are valid for 3 years from purchase. They can be combined with other payment methods, but not with other gift cards bought with a promotional discount. Gift cards cannot be exchanged for cash. A lost gift card code can be blocked and reissued if you can show the purchase receipt.
```

**Reply to label:**
```text
I’m sorry, but our policy does not allow voucher balances to be converted into cash. A human colleague will assist you further—your ticket (TK-00001) is now open. They’ll be available Monday–Friday 8:00–20:00 CET or Saturday 9:00–16:00 CET, with a typical response time under 4 hours on business days.
```

Label `correct`: yes / no. Label `grounded`: yes / no.

## L04 (p10, policy)

**Customer:**
> How much does delivery cost in Germany?

**Context (tool results the assistant saw):**
```text
[search_policies]
  [shipping-germany] Shipping within Germany. Standard shipping in Germany takes 2 to 4 business days and costs EUR 4.95. Orders above EUR 50 ship free. Express shipping delivers the next business day if ordered before 14:00 and costs EUR 9.95. We ship with DHL and Hermes; the carrier is chosen automatically and shown in the shipping confirmation email.

  [shipping-eu] Shipping to other EU countries. We deliver to all EU countries plus Switzerland and Norway. Standard EU shipping takes 4 to 8 business days and costs EUR 9.95, free above EUR 80. Express is not available outside Germany and Austria. For Switzerland and Norway, customs duties and import VAT may be charged by the carrier on delivery; these are paid by the recipient.

  [returns-general] Returns: general policy. Customers can return most items within 30 days of delivery. The 30-day window starts on the day the parcel is delivered, not the order date. Items must be unused, in original condition, and with all tags attached. Returns are free of charge for customers in Germany and Austria. For other EU countries, a return label costs EUR 6.95, which is deducted from the refund. To start a return, open "My Orders", select the item and choose "Return item", or ask

  [invoices] Invoices and VAT. An invoice is attached to the shipping confirmation email as a PDF and can be downloaded again in "My Orders". Prices include German VAT of 19 percent (7 percent for books). Business customers can add a company name and VAT ID in their account before ordering; invoices cannot be changed to a company address after they are issued.

  [membership] Nordwind Plus membership. Nordwind Plus costs EUR 29 per year and includes free express shipping in Germany, early access to sales, and an extended return window of 60 days instead of 30. Membership renews automatically and can be cancelled at any time before the renewal date; there are no partial refunds for the remaining months.
```

**Reference policy:**
```text
Shipping within Germany
Standard shipping in Germany takes 2 to 4 business days and costs EUR 4.95. Orders above EUR 50 ship free. Express shipping delivers the next business day if ordered before 14:00 and costs EUR 9.95. We ship with DHL and Hermes; the carrier is chosen automatically and shown in the shipping confirmation email.
```

**Reply to label:**
```text
Standard shipping in Germany costs **EUR 4.95** and takes 2 to 4 business days. If your order is over **EUR 50**, delivery is free. Express shipping (next business day) costs **EUR 9.95** if ordered before 14:00.
```

Label `correct`: yes / no. Label `grounded`: yes / no.

## L05 (p04, policy)

**Customer:**
> I opened a lipstick but don't like the colour, can I return it?

**Context (tool results the assistant saw):**
```text
[search_policies]
  [returns-exceptions] Items that cannot be returned. Some items are excluded from returns for hygiene or legal reasons: underwear and swimwear with a removed hygiene seal, opened cosmetics, earrings, personalised or engraved products, gift cards, and downloadable software once the licence key has been revealed. Sealed headphones and in-ear products can only be returned if the original seal is unbroken. Items marked "Final sale" in the product page are also non-returnable.

  [returns-general] Returns: general policy. Customers can return most items within 30 days of delivery. The 30-day window starts on the day the parcel is delivered, not the order date. Items must be unused, in original condition, and with all tags attached. Returns are free of charge for customers in Germany and Austria. For other EU countries, a return label costs EUR 6.95, which is deducted from the refund. To start a return, open "My Orders", select the item and choose "Return item", or ask

  [returns-general] Returns: general policy. deducted from the refund. To start a return, open "My Orders", select the item and choose "Return item", or ask the support assistant to start the return for you.

  [returns-damaged] Damaged or defective items. If an item arrives damaged or stops working, report it within 14 days of delivery with a photo of the damage. Damaged items are not counted against the 30-day return window. We offer a free replacement or a full refund, including the original shipping costs. For electronics, the statutory warranty of 2 years applies in addition; after 14 days, defects are handled as warranty claims (see "Warranty for electronics").

  [refunds-partial] Partial refunds and deductions. If a returned item shows signs of use, missing tags, or damage caused by the customer, we may issue a partial refund of up to 50 percent of the item price after inspection. Return label costs for non-free countries (EUR 6.95) are deducted from the refund. Discount codes used on the original order are not refunded as cash; if the remaining order no longer meets the code's minimum value, the discount is recalculated.

[escalate_to_human] Ticket TK-00001 created. Human support is available Mon-Fri 8:00-20:00 and Sat 9:00-16:00 (CET); average response time is under 4 hours on business days.
```

**Reference policy:**
```text
Items that cannot be returned
Some items are excluded from returns for hygiene or legal reasons: underwear and swimwear with a removed hygiene seal, opened cosmetics, earrings, personalised or engraved products, gift cards, and downloadable software once the licence key has been revealed. Sealed headphones and in-ear products can only be returned if the original seal is unbroken. Items marked "Final sale" in the product page are also non-returnable.
```

**Reply to label:**
```text
I’m sorry, but opened cosmetics like lipstick cannot be returned due to hygiene rules. Please contact our human support team—they’ll assist you right away! Your ticket is TK-00001.
```

Label `correct`: yes / no. Label `grounded`: yes / no.

## L06 (p10, policy)

**Customer:**
> How much does delivery cost in Germany?

**Context (tool results the assistant saw):**
```text
[search_policies]
  [shipping-germany] Shipping within Germany. Standard shipping in Germany takes 2 to 4 business days and costs EUR 4.95. Orders above EUR 50 ship free. Express shipping delivers the next business day if ordered before 14:00 and costs EUR 9.95. We ship with DHL and Hermes; the carrier is chosen automatically and shown in the shipping confirmation email.

  [shipping-eu] Shipping to other EU countries. We deliver to all EU countries plus Switzerland and Norway. Standard EU shipping takes 4 to 8 business days and costs EUR 9.95, free above EUR 80. Express is not available outside Germany and Austria. For Switzerland and Norway, customs duties and import VAT may be charged by the carrier on delivery; these are paid by the recipient.

  [returns-general] Returns: general policy. Customers can return most items within 30 days of delivery. The 30-day window starts on the day the parcel is delivered, not the order date. Items must be unused, in original condition, and with all tags attached. Returns are free of charge for customers in Germany and Austria. For other EU countries, a return label costs EUR 6.95, which is deducted from the refund. To start a return, open "My Orders", select the item and choose "Return item", or ask

  [invoices] Invoices and VAT. An invoice is attached to the shipping confirmation email as a PDF and can be downloaded again in "My Orders". Prices include German VAT of 19 percent (7 percent for books). Business customers can add a company name and VAT ID in their account before ordering; invoices cannot be changed to a company address after they are issued.

  [membership] Nordwind Plus membership. Nordwind Plus costs EUR 29 per year and includes free express shipping in Germany, early access to sales, and an extended return window of 60 days instead of 30. Membership renews automatically and can be cancelled at any time before the renewal date; there are no partial refunds for the remaining months.
```

**Reference policy:**
```text
Shipping within Germany
Standard shipping in Germany takes 2 to 4 business days and costs EUR 4.95. Orders above EUR 50 ship free. Express shipping delivers the next business day if ordered before 14:00 and costs EUR 9.95. We ship with DHL and Hermes; the carrier is chosen automatically and shown in the shipping confirmation email.
```

**Reply to label:**
```text
In Germany, standard shipping costs **EUR 4.95** and is free for orders above **EUR 50**. Express shipping (next business day) costs **EUR 9.95** and is available if ordered before 14:00.
```

Label `correct`: yes / no. Label `grounded`: yes / no.

## L07 (p27, policy)

**Customer:**
> What do I get with the yearly subscription?

**Context (tool results the assistant saw):**
```text
[search_policies]
  [membership] Nordwind Plus membership. Nordwind Plus costs EUR 29 per year and includes free express shipping in Germany, early access to sales, and an extended return window of 60 days instead of 30. Membership renews automatically and can be cancelled at any time before the renewal date; there are no partial refunds for the remaining months.

  [gift-cards] Gift cards. Gift cards are available from EUR 10 to EUR 500 and are valid for 3 years from purchase. They can be combined with other payment methods, but not with other gift cards bought with a promotional discount. Gift cards cannot be exchanged for cash. A lost gift card code can be blocked and reissued if you can show the purchase receipt.

  [warranty-electronics] Warranty for electronics. All electronics come with the statutory 2-year warranty from the delivery date. Some brands offer an additional manufacturer guarantee, shown on the product page. For warranty claims, contact support with the order number and a description of the defect; we will send a free return label and either repair, replace, or refund the product. Repairs typically take 2 to 3 weeks.

  [invoices] Invoices and VAT. An invoice is attached to the shipping confirmation email as a PDF and can be downloaded again in "My Orders". Prices include German VAT of 19 percent (7 percent for books). Business customers can add a company name and VAT ID in their account before ordering; invoices cannot be changed to a company address after they are issued.

  [returns-damaged] Damaged or defective items. If an item arrives damaged or stops working, report it within 14 days of delivery with a photo of the damage. Damaged items are not counted against the 30-day return window. We offer a free replacement or a full refund, including the original shipping costs. For electronics, the statutory warranty of 2 years applies in addition; after 14 days, defects are handled as warranty claims (see "Warranty for electronics").
```

**Reference policy:**
```text
Nordwind Plus membership
Nordwind Plus costs EUR 29 per year and includes free express shipping in Germany, early access to sales, and an extended return window of 60 days instead of 30. Membership renews automatically and can be cancelled at any time before the renewal date; there are no partial refunds for the remaining months.
```

**Reply to label:**
```text
With the yearly Nordwind Plus subscription (EUR 29), you get free express shipping in Germany, early access to sales, and an extended return window of 60 days. The membership renews automatically but can be cancelled anytime before renewal.
```

Label `correct`: yes / no. Label `grounded`: yes / no.

## L08 (p01, policy)

**Customer:**
> How many days do I have to send something back?

**Context (tool results the assistant saw):**
```text
[search_policies]
  [returns-general] Returns: general policy. Customers can return most items within 30 days of delivery. The 30-day window starts on the day the parcel is delivered, not the order date. Items must be unused, in original condition, and with all tags attached. Returns are free of charge for customers in Germany and Austria. For other EU countries, a return label costs EUR 6.95, which is deducted from the refund. To start a return, open "My Orders", select the item and choose "Return item", or ask

  [returns-damaged] Damaged or defective items. If an item arrives damaged or stops working, report it within 14 days of delivery with a photo of the damage. Damaged items are not counted against the 30-day return window. We offer a free replacement or a full refund, including the original shipping costs. For electronics, the statutory warranty of 2 years applies in addition; after 14 days, defects are handled as warranty claims (see "Warranty for electronics").

  [sustainability] Packaging and sustainability. Parcels are shipped in recycled cardboard, and the return label is included in the box. Returned items in perfect condition are resold; others are refurbished or donated, never destroyed. Customers can choose "bundle my order" at checkout to receive all items in one parcel, even if this takes one or two days longer.

  [warranty-electronics] Warranty for electronics. All electronics come with the statutory 2-year warranty from the delivery date. Some brands offer an additional manufacturer guarantee, shown on the product page. For warranty claims, contact support with the order number and a description of the defect; we will send a free return label and either repair, replace, or refund the product. Repairs typically take 2 to 3 weeks.

  [returns-general] Returns: general policy. deducted from the refund. To start a return, open "My Orders", select the item and choose "Return item", or ask the support assistant to start the return for you.
```

**Reference policy:**
```text
Returns: general policy
Customers can return most items within 30 days of delivery. The 30-day window starts on the day the parcel is delivered, not the order date. Items must be unused, in original condition, and with all tags attached. Returns are free of charge for customers in Germany and Austria. For other EU countries, a return label costs EUR 6.95, which is deducted from the refund. To start a return, open "My Orders", select the item and choose "Return item", or ask the support assistant to start the return for you.
```

**Reply to label:**
```text
You have **30 days** from delivery to return most items in good condition. For EU countries outside Germany or Austria, a return label costs EUR 6.95.
```

Label `correct`: yes / no. Label `grounded`: yes / no.

## L09 (p27, policy)

**Customer:**
> What do I get with the yearly subscription?

**Context (tool results the assistant saw):**
```text
[search_policies]
  [membership] Nordwind Plus membership. Nordwind Plus costs EUR 29 per year and includes free express shipping in Germany, early access to sales, and an extended return window of 60 days instead of 30. Membership renews automatically and can be cancelled at any time before the renewal date; there are no partial refunds for the remaining months.

  [gift-cards] Gift cards. Gift cards are available from EUR 10 to EUR 500 and are valid for 3 years from purchase. They can be combined with other payment methods, but not with other gift cards bought with a promotional discount. Gift cards cannot be exchanged for cash. A lost gift card code can be blocked and reissued if you can show the purchase receipt.

  [warranty-electronics] Warranty for electronics. All electronics come with the statutory 2-year warranty from the delivery date. Some brands offer an additional manufacturer guarantee, shown on the product page. For warranty claims, contact support with the order number and a description of the defect; we will send a free return label and either repair, replace, or refund the product. Repairs typically take 2 to 3 weeks.

  [invoices] Invoices and VAT. An invoice is attached to the shipping confirmation email as a PDF and can be downloaded again in "My Orders". Prices include German VAT of 19 percent (7 percent for books). Business customers can add a company name and VAT ID in their account before ordering; invoices cannot be changed to a company address after they are issued.

  [returns-damaged] Damaged or defective items. If an item arrives damaged or stops working, report it within 14 days of delivery with a photo of the damage. Damaged items are not counted against the 30-day return window. We offer a free replacement or a full refund, including the original shipping costs. For electronics, the statutory warranty of 2 years applies in addition; after 14 days, defects are handled as warranty claims (see "Warranty for electronics").

[search_policies]
  [membership] Nordwind Plus membership. Nordwind Plus costs EUR 29 per year and includes free express shipping in Germany, early access to sales, and an extended return window of 60 days instead of 30. Membership renews automatically and can be cancelled at any time before the renewal date; there are no partial refunds for the remaining months.

  [payment-methods] Accepted payment methods. We accept Visa, Mastercard, American Express, PayPal, Klarna (pay later in 30 days), Apple Pay, Google Pay and Nordwind gift cards. Cash on delivery is not available. Your card is charged when the order is dispatched, not when it is placed. For Klarna, the 30-day payment period starts on the dispatch date.

  [price-match] Price changes after purchase. We do not offer price matching with other shops. If the price of an item you bought drops on nordwind.de within 7 days of your order, contact support and we will refund the difference as a voucher. This does not apply to flash sales, outlet items, or discounts from codes.

  [gift-cards] Gift cards. Gift cards are available from EUR 10 to EUR 500 and are valid for 3 years from purchase. They can be combined with other payment methods, but not with other gift cards bought with a promotional discount. Gift cards cannot be exchanged for cash. A lost gift card code can be blocked and reissued if you can show the purchase receipt.

  [shipping-eu] Shipping to other EU countries. We deliver to all EU countries plus Switzerland and Norway. Standard EU shipping takes 4 to 8 business days and costs EUR 9.95, free above EUR 80. Express is not available outside Germany and Austria. For Switzerland and Norway, customs duties and import VAT may be charged by the carrier on delivery; these are paid by the recipient.
```

**Reference policy:**
```text
Nordwind Plus membership
Nordwind Plus costs EUR 29 per year and includes free express shipping in Germany, early access to sales, and an extended return window of 60 days instead of 30. Membership renews automatically and can be cancelled at any time before the renewal date; there are no partial refunds for the remaining months.
```

**Reply to label:**
```text
With the Nordwind Plus yearly subscription (EUR 29/year), you get:
• Free express shipping in Germany
• Early access to sales
• An extended return window of 60 days (instead of 30)

The membership renews automatically and can be cancelled anytime before renewal.
```

Label `correct`: yes / no. Label `grounded`: yes / no.

## L10 (p21, policy)

**Customer:**
> Can I use two promo codes on one order?

**Context (tool results the assistant saw):**
```text
[search_policies]
  [discount-codes] Discount and voucher codes. Only one discount code can be used per order. Codes are entered at checkout and cannot be applied after the order is placed. Codes do not apply to gift cards or items marked "Final sale". If a code does not work, check the expiry date and the minimum order value shown in the voucher email.

  [gift-cards] Gift cards. Gift cards are available from EUR 10 to EUR 500 and are valid for 3 years from purchase. They can be combined with other payment methods, but not with other gift cards bought with a promotional discount. Gift cards cannot be exchanged for cash. A lost gift card code can be blocked and reissued if you can show the purchase receipt.

  [refunds-partial] Partial refunds and deductions. If a returned item shows signs of use, missing tags, or damage caused by the customer, we may issue a partial refund of up to 50 percent of the item price after inspection. Return label costs for non-free countries (EUR 6.95) are deducted from the refund. Discount codes used on the original order are not refunded as cash; if the remaining order no longer meets the code's minimum value, the discount is recalculated.

  [payment-failed] Payment declined or failed. If a payment fails, the order is kept for 48 hours so you can retry with another method in "My Orders". Common causes are 3-D Secure verification not completed, an expired card, or a daily card limit. We never see your full card details and cannot tell you why a bank declined a payment; please contact your bank in that case.

  [sustainability] Packaging and sustainability. Parcels are shipped in recycled cardboard, and the return label is included in the box. Returned items in perfect condition are resold; others are refurbished or donated, never destroyed. Customers can choose "bundle my order" at checkout to receive all items in one parcel, even if this takes one or two days longer.
```

**Reference policy:**
```text
Discount and voucher codes
Only one discount code can be used per order. Codes are entered at checkout and cannot be applied after the order is placed. Codes do not apply to gift cards or items marked "Final sale". If a code does not work, check the expiry date and the minimum order value shown in the voucher email.
```

**Reply to label:**
```text
Unfortunately, you can only use one promo code per order, as stated in our discount policy. Each code is applied at checkout and cannot be combined with another. Thank you for understanding!
```

Label `correct`: yes / no. Label `grounded`: yes / no.

## L11 (p24, policy)

**Customer:**
> How long does a repair take?

**Context (tool results the assistant saw):**
```text
[search_policies]
  [warranty-electronics] Warranty for electronics. All electronics come with the statutory 2-year warranty from the delivery date. Some brands offer an additional manufacturer guarantee, shown on the product page. For warranty claims, contact support with the order number and a description of the defect; we will send a free return label and either repair, replace, or refund the product. Repairs typically take 2 to 3 weeks.

  [returns-damaged] Damaged or defective items. If an item arrives damaged or stops working, report it within 14 days of delivery with a photo of the damage. Damaged items are not counted against the 30-day return window. We offer a free replacement or a full refund, including the original shipping costs. For electronics, the statutory warranty of 2 years applies in addition; after 14 days, defects are handled as warranty claims (see "Warranty for electronics").

  [returns-general] Returns: general policy. Customers can return most items within 30 days of delivery. The 30-day window starts on the day the parcel is delivered, not the order date. Items must be unused, in original condition, and with all tags attached. Returns are free of charge for customers in Germany and Austria. For other EU countries, a return label costs EUR 6.95, which is deducted from the refund. To start a return, open "My Orders", select the item and choose "Return item", or ask

  [shipping-delays] My parcel is late. If your parcel has not arrived within the expected delivery time, first check the tracking link in your shipping email. Tracking can take up to 24 hours to update after dispatch. If there has been no tracking update for 5 business days, contact support and we will open an investigation with the carrier. If the parcel is confirmed lost, we send a replacement or refund the order in full.

  [refunds-timing] When will I get my refund?. Refunds are issued after the returned parcel arrives at our warehouse and passes inspection, which usually takes 3 to 5 business days after arrival. The money is sent back to the original payment method. Card refunds appear within 5 to 10 business days depending on the bank; PayPal refunds usually appear within 24 hours. Gift card payments are refunded as a new gift card. You will receive an email as soon as the refund has been issued.

[escalate_to_human] Ticket TK-00001 created. Human support is available Mon-Fri 8:00-20:00 and Sat 9:00-16:00 (CET); average response time is under 4 hours on business days.
```

**Reference policy:**
```text
Warranty for electronics
All electronics come with the statutory 2-year warranty from the delivery date. Some brands offer an additional manufacturer guarantee, shown on the product page. For warranty claims, contact support with the order number and a description of the defect; we will send a free return label and either repair, replace, or refund the product. Repairs typically take 2 to 3 weeks.
```

**Reply to label:**
```text
I checked our policies, but they only specify repair times for electronics (2–3 weeks). For other items, please let a colleague handle this—you’ll be connected shortly. Your ticket is TK-00001.
```

Label `correct`: yes / no. Label `grounded`: yes / no.

## L12 (p01, policy)

**Customer:**
> How many days do I have to send something back?

**Context (tool results the assistant saw):**
```text
[search_policies]
  [returns-general] Returns: general policy. Customers can return most items within 30 days of delivery. The 30-day window starts on the day the parcel is delivered, not the order date. Items must be unused, in original condition, and with all tags attached. Returns are free of charge for customers in Germany and Austria. For other EU countries, a return label costs EUR 6.95, which is deducted from the refund. To start a return, open "My Orders", select the item and choose "Return item", or ask

  [returns-damaged] Damaged or defective items. If an item arrives damaged or stops working, report it within 14 days of delivery with a photo of the damage. Damaged items are not counted against the 30-day return window. We offer a free replacement or a full refund, including the original shipping costs. For electronics, the statutory warranty of 2 years applies in addition; after 14 days, defects are handled as warranty claims (see "Warranty for electronics").

  [sustainability] Packaging and sustainability. Parcels are shipped in recycled cardboard, and the return label is included in the box. Returned items in perfect condition are resold; others are refurbished or donated, never destroyed. Customers can choose "bundle my order" at checkout to receive all items in one parcel, even if this takes one or two days longer.

  [returns-general] Returns: general policy. deducted from the refund. To start a return, open "My Orders", select the item and choose "Return item", or ask the support assistant to start the return for you.

  [refunds-partial] Partial refunds and deductions. If a returned item shows signs of use, missing tags, or damage caused by the customer, we may issue a partial refund of up to 50 percent of the item price after inspection. Return label costs for non-free countries (EUR 6.95) are deducted from the refund. Discount codes used on the original order are not refunded as cash; if the remaining order no longer meets the code's minimum value, the discount is recalculated.
```

**Reference policy:**
```text
Returns: general policy
Customers can return most items within 30 days of delivery. The 30-day window starts on the day the parcel is delivered, not the order date. Items must be unused, in original condition, and with all tags attached. Returns are free of charge for customers in Germany and Austria. For other EU countries, a return label costs EUR 6.95, which is deducted from the refund. To start a return, open "My Orders", select the item and choose "Return item", or ask the support assistant to start the return for you.
```

**Reply to label:**
```text
You have 30 days from the delivery date to return most items. The return period starts on the day your parcel was delivered, not the order date. Please ensure the items are unused and in their original condition.
```

Label `correct`: yes / no. Label `grounded`: yes / no.

## L13 (p20, policy)

**Customer:**
> Can I turn my voucher balance into cash?

**Context (tool results the assistant saw):**
```text
[search_policies]
  [discount-codes] Discount and voucher codes. Only one discount code can be used per order. Codes are entered at checkout and cannot be applied after the order is placed. Codes do not apply to gift cards or items marked "Final sale". If a code does not work, check the expiry date and the minimum order value shown in the voucher email.

  [gift-cards] Gift cards. Gift cards are available from EUR 10 to EUR 500 and are valid for 3 years from purchase. They can be combined with other payment methods, but not with other gift cards bought with a promotional discount. Gift cards cannot be exchanged for cash. A lost gift card code can be blocked and reissued if you can show the purchase receipt.

  [refunds-partial] Partial refunds and deductions. If a returned item shows signs of use, missing tags, or damage caused by the customer, we may issue a partial refund of up to 50 percent of the item price after inspection. Return label costs for non-free countries (EUR 6.95) are deducted from the refund. Discount codes used on the original order are not refunded as cash; if the remaining order no longer meets the code's minimum value, the discount is recalculated.

  [price-match] Price changes after purchase. We do not offer price matching with other shops. If the price of an item you bought drops on nordwind.de within 7 days of your order, contact support and we will refund the difference as a voucher. This does not apply to flash sales, outlet items, or discounts from codes.

  [invoices] Invoices and VAT. An invoice is attached to the shipping confirmation email as a PDF and can be downloaded again in "My Orders". Prices include German VAT of 19 percent (7 percent for books). Business customers can add a company name and VAT ID in their account before ordering; invoices cannot be changed to a company address after they are issued.
```

**Reference policy:**
```text
Gift cards
Gift cards are available from EUR 10 to EUR 500 and are valid for 3 years from purchase. They can be combined with other payment methods, but not with other gift cards bought with a promotional discount. Gift cards cannot be exchanged for cash. A lost gift card code can be blocked and reissued if you can show the purchase receipt.
```

**Reply to label:**
```text
Unfortunately, voucher balances cannot be converted to cash. According to our policy, gift cards and voucher balances are non-refundable and can only be used for purchases on our website. If you have any other questions, feel free to ask!
```

Label `correct`: yes / no. Label `grounded`: yes / no.

## L14 (p09, policy)

**Customer:**
> Can I swap my shoes for a bigger size?

**Context (tool results the assistant saw):**
```text
[search_policies]
  [exchanges] Exchanging an item for another size or colour. We do not swap items directly. To get a different size or colour, return the original item for a refund and place a new order. For shoes and clothing, the size advisor on the product page shows how each brand fits. Tip: place the new order first if the item is low in stock, because returned items are not reserved for you.

  [sizing] Size guide and fit. Each clothing and shoe product page has a size chart in centimetres and a fit hint based on customer reviews ("runs small", "true to size", "runs large"). EU, UK and US sizes are converted automatically. If you are between two sizes, the size advisor recommends a size based on items you kept in previous orders.

  [returns-general] Returns: general policy. Customers can return most items within 30 days of delivery. The 30-day window starts on the day the parcel is delivered, not the order date. Items must be unused, in original condition, and with all tags attached. Returns are free of charge for customers in Germany and Austria. For other EU countries, a return label costs EUR 6.95, which is deducted from the refund. To start a return, open "My Orders", select the item and choose "Return item", or ask

  [returns-damaged] Damaged or defective items. If an item arrives damaged or stops working, report it within 14 days of delivery with a photo of the damage. Damaged items are not counted against the 30-day return window. We offer a free replacement or a full refund, including the original shipping costs. For electronics, the statutory warranty of 2 years applies in addition; after 14 days, defects are handled as warranty claims (see "Warranty for electronics").

  [refunds-partial] Partial refunds and deductions. If a returned item shows signs of use, missing tags, or damage caused by the customer, we may issue a partial refund of up to 50 percent of the item price after inspection. Return label costs for non-free countries (EUR 6.95) are deducted from the refund. Discount codes used on the original order are not refunded as cash; if the remaining order no longer meets the code's minimum value, the discount is recalculated.

[get_order_status] Not executed: the customer has not given this order number and e-mail address. Ask the customer for it; do not guess.

[get_order_status] Not executed: the customer has not given this order number and e-mail address. Ask the customer for it; do not guess.

[escalate_to_human] Ticket TK-00001 created. Human support is available Mon-Fri 8:00-20:00 and Sat 9:00-16:00 (CET); average response time is under 4 hours on business days.
```

**Reference policy:**
```text
Exchanging an item for another size or colour
We do not swap items directly. To get a different size or colour, return the original item for a refund and place a new order. For shoes and clothing, the size advisor on the product page shows how each brand fits. Tip: place the new order first if the item is low in stock, because returned items are not reserved for you.
```

**Reply to label:**
```text
Could you please confirm your order number (e.g., NW-100001) and the email used for the purchase? I’ll escalate this to a human specialist who can assist you further.
```

Label `correct`: yes / no. Label `grounded`: yes / no.

## L15 (t11, order)

**Customer:**
> Can I return the earrings from NW-100006? My e-mail is farid@example.com

**Context (tool results the assistant saw):**
```text
[get_order_status]
{
  "order_id": "NW-100006",
  "status": "delivered",
  "ordered_on": "2026-09-28",
  "delivered_on": "2026-10-01",
  "carrier": "DHL",
  "tracking_no": "DHL1000062",
  "country": "DE",
  "plus_member": false,
  "return_window_ends": "2026-10-31",
  "items": [
    {
      "sku": "EAR-055",
      "name": "Silver earrings",
      "category": "earrings",
      "price_eur": 39.0,
      "returnable_category": false,
      "already_returned": false
    },
    {
      "sku": "SCF-019",
      "name": "Wool scarf",
      "category": "accessories",
      "price_eur": 24.9,
      "returnable_category": true,
      "already_returned": false
    }
  ]
}

[search_policies]
  [returns-exceptions] Items that cannot be returned. Some items are excluded from returns for hygiene or legal reasons: underwear and swimwear with a removed hygiene seal, opened cosmetics, earrings, personalised or engraved products, gift cards, and downloadable software once the licence key has been revealed. Sealed headphones and in-ear products can only be returned if the original seal is unbroken. Items marked "Final sale" in the product page are also non-returnable.

  [sustainability] Packaging and sustainability. Parcels are shipped in recycled cardboard, and the return label is included in the box. Returned items in perfect condition are resold; others are refurbished or donated, never destroyed. Customers can choose "bundle my order" at checkout to receive all items in one parcel, even if this takes one or two days longer.

  [returns-general] Returns: general policy. deducted from the refund. To start a return, open "My Orders", select the item and choose "Return item", or ask the support assistant to start the return for you.

  [returns-general] Returns: general policy. Customers can return most items within 30 days of delivery. The 30-day window starts on the day the parcel is delivered, not the order date. Items must be unused, in original condition, and with all tags attached. Returns are free of charge for customers in Germany and Austria. For other EU countries, a return label costs EUR 6.95, which is deducted from the refund. To start a return, open "My Orders", select the item and choose "Return item", or ask

  [refunds-partial] Partial refunds and deductions. If a returned item shows signs of use, missing tags, or damage caused by the customer, we may issue a partial refund of up to 50 percent of the item price after inspection. Return label costs for non-free countries (EUR 6.95) are deducted from the refund. Discount codes used on the original order are not refunded as cash; if the remaining order no longer meets the code's minimum value, the discount is recalculated.
```

**Reply to label:**
```text
Unfortunately, the silver earrings (SKU: EAR-055) from order NW-100006 cannot be returned, as jewelry is excluded from returns for hygiene and legal reasons. You can still return the wool scarf if you wish, as it is returnable. The return window for your order ends on October 31, 2026.
```

Label `correct`: leave empty (no reference). Label `grounded`: yes / no.

## L16 (o13, out_of_scope)

**Customer:**
> What will the weather be like in Berlin tomorrow?

**Context (tool results the assistant saw):**
```text
[search_policies]
  [sizing] Size guide and fit. Each clothing and shoe product page has a size chart in centimetres and a fit hint based on customer reviews ("runs small", "true to size", "runs large"). EU, UK and US sizes are converted automatically. If you are between two sizes, the size advisor recommends a size based on items you kept in previous orders.

  [price-match] Price changes after purchase. We do not offer price matching with other shops. If the price of an item you bought drops on nordwind.de within 7 days of your order, contact support and we will refund the difference as a voucher. This does not apply to flash sales, outlet items, or discounts from codes.

  [payment-methods] Accepted payment methods. We accept Visa, Mastercard, American Express, PayPal, Klarna (pay later in 30 days), Apple Pay, Google Pay and Nordwind gift cards. Cash on delivery is not available. Your card is charged when the order is dispatched, not when it is placed. For Klarna, the 30-day payment period starts on the dispatch date.

  [returns-damaged] Damaged or defective items. If an item arrives damaged or stops working, report it within 14 days of delivery with a photo of the damage. Damaged items are not counted against the 30-day return window. We offer a free replacement or a full refund, including the original shipping costs. For electronics, the statutory warranty of 2 years applies in addition; after 14 days, defects are handled as warranty claims (see "Warranty for electronics").

  [shipping-germany] Shipping within Germany. Standard shipping in Germany takes 2 to 4 business days and costs EUR 4.95. Orders above EUR 50 ship free. Express shipping delivers the next business day if ordered before 14:00 and costs EUR 9.95. We ship with DHL and Hermes; the carrier is chosen automatically and shown in the shipping confirmation email.

[search_policies]
  Not executed: you already called this tool with the same arguments. Use the earlier result.
```

**Reply to label:**
```text
I can’t help with weather forecasts. For Nordwind’s policies, I’ll always refer to our official documents. Let me know if you need details about returns, shipping, or payments!
```

Label `correct`: leave empty (no reference). Label `grounded`: yes / no.

## L17 (t08, order)

**Customer:**
> I want to send back the rain jacket from NW-100002, I changed my mind. Email: ben@example.com

**Context (tool results the assistant saw):**
```text
[get_order_status]
{
  "order_id": "NW-100002",
  "status": "delivered",
  "ordered_on": "2026-09-15",
  "delivered_on": "2026-09-20",
  "carrier": "DPD",
  "tracking_no": "DPD1000021",
  "country": "FR",
  "plus_member": false,
  "return_window_ends": "2026-10-20",
  "items": [
    {
      "sku": "JKT-203",
      "name": "Rain jacket",
      "category": "clothing",
      "price_eur": 89.0,
      "returnable_category": true,
      "already_returned": false
    }
  ]
}

[start_return]
{
  "status": "started",
  "lines": [
    {
      "sku": "JKT-203",
      "return_id": "RT-100002-JKT-203",
      "rejected_reason": null
    }
  ],
  "label_fee_eur": 6.95,
  "message": "Return started for 1 item(s); a return label fee of EUR 6.95 is deducted from the refund."
}
```

**Reply to label:**
```text
Your return for the rain jacket (SKU: JKT-203) has been started. A return label fee of **EUR 6.95** will be deducted from your refund. You can print the label from your order page and ship the item back within the return window (until **2026-10-20**).
```

Label `correct`: leave empty (no reference). Label `grounded`: yes / no.

## L18 (o12, out_of_scope)

**Customer:**
> Can you recommend a good pasta recipe?

**Context (tool results the assistant saw):**
```text
(no tools used)
```

**Reply to label:**
```text
I’m happy to help with Nordwind orders, but I don’t have recipes! Let me know if you’d like assistance with your purchases or any other questions about our shop.
```

Label `correct`: leave empty (no reference). Label `grounded`: yes / no.

## L19 (t16, order)

**Customer:**
> Where is my parcel?
> NW-100004
> david@example.com

**Context (tool results the assistant saw):**
```text
[get_order_status] Not executed: the customer has not given this order number and e-mail address. Ask the customer for it; do not guess.

[escalate_to_human] Ticket TK-00001 created. Human support is available Mon-Fri 8:00-20:00 and Sat 9:00-16:00 (CET); average response time is under 4 hours on business days.

[escalate_to_human] Ticket TK-00002 created. Human support is available Mon-Fri 8:00-20:00 and Sat 9:00-16:00 (CET); average response time is under 4 hours on business days.

[get_order_status]
{
  "order_id": "NW-100004",
  "status": "shipped",
  "ordered_on": "2026-10-07",
  "delivered_on": null,
  "carrier": "Post AT",
  "tracking_no": "POS1000041",
  "country": "AT",
  "plus_member": false,
  "return_window_ends": null,
  "items": [
    {
      "sku": "BAG-007",
      "name": "Leather backpack",
      "category": "bags",
      "price_eur": 129.0,
      "returnable_category": true,
      "already_returned": false
    }
  ]
}
```

**Reply to label:**
```text
Your order **NW-100004** was shipped on **7 October 2026** with **Post AT** (tracking: POS1000041). The leather backpack is on its way—check your local carrier’s app for delivery updates!
```

Label `correct`: leave empty (no reference). Label `grounded`: yes / no.

## L20 (t10, order)

**Customer:**
> I'd like to return the earrings and the scarf from NW-100006 (farid@example.com), I changed my mind.

**Context (tool results the assistant saw):**
```text
[get_order_status]
{
  "order_id": "NW-100006",
  "status": "delivered",
  "ordered_on": "2026-09-28",
  "delivered_on": "2026-10-01",
  "carrier": "DHL",
  "tracking_no": "DHL1000062",
  "country": "DE",
  "plus_member": false,
  "return_window_ends": "2026-10-31",
  "items": [
    {
      "sku": "EAR-055",
      "name": "Silver earrings",
      "category": "earrings",
      "price_eur": 39.0,
      "returnable_category": false,
      "already_returned": false
    },
    {
      "sku": "SCF-019",
      "name": "Wool scarf",
      "category": "accessories",
      "price_eur": 24.9,
      "returnable_category": true,
      "already_returned": false
    }
  ]
}

[start_return]
{
  "status": "started",
  "lines": [
    {
      "sku": "SCF-019",
      "return_id": "RT-100006-SCF-019",
      "rejected_reason": null
    }
  ],
  "label_fee_eur": 0.0,
  "message": "Return started for 1 item(s); free of charge."
}

[start_return]
{
  "status": "rejected",
  "lines": [
    {
      "sku": "EAR-055",
      "return_id": null,
      "rejected_reason": "non_returnable_category:earrings"
    }
  ],
  "label_fee_eur": 0.0,
  "message": "None of the items can be returned."
}
```

**Reply to label:**
```text
Your return for the wool scarf (SKU: SCF-019) has been started successfully and is free of charge. Unfortunately, the earrings (SKU: EAR-055) cannot be returned as they belong to a non-returnable category.
```

Label `correct`: leave empty (no reference). Label `grounded`: yes / no.

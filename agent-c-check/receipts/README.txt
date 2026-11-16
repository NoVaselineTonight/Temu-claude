Svinkki demo receipts: fictional S Group receipts (Prisma, S-market, Alepa, Sale, ABC) for the demo customers.
They are fictional: generated deterministically from the synthetic challenge payments (label Groceries and Fuel), not real purchases.
receipts.json holds every receipt per customer; the CSV files hold one row per receipt line (UTF-8 with BOM, decimal point).
Each receipt's lines add up to the payment to the cent; prices are illustrative.
To regenerate: python -m app.receipts (also runs at the end of python -m app.ingest).

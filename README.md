# SubSave – Subscription Audit & Optimization Service

**SubSave** helps startups and micro‑businesses take control of their SaaS spending.  Research shows that mid‑sized organisations waste more than **$135,000 per year** on unused software subscriptions【63229005519729†L256-L265】.  Smaller teams suffer from the same problem: employees sign up for similar tools independently, leading to duplicate functionality, hidden costs and missed renewal dates【941180497264979†L260-L266】.  Without a structured process to review spending, these costs quickly spiral【941180497264979†L306-L325】.

SubSave combines AI‑assisted analysis with human oversight to audit your current subscriptions, highlight redundant services and suggest cheaper or free alternatives.  Our goal is to save you money while keeping your workflows intact.

## How It Works

1. **Submit your subscriptions.**  Visit the live site at [subsave‑site](https://alexsawyer23.github.io/subsave-site/).  Use the form to list the SaaS tools you currently pay for, along with the monthly or annual cost.  Your submission is sent securely via FormSubmit and triggers the audit process.

2. **We analyse your stack.**  The `audit_generator.py` script reads your subscription list and compares it against our curated database of SaaS pricing and alternatives.  It calculates potential monthly and yearly savings by suggesting lower‑cost options with comparable functionality.

3. **Receive a detailed report.**  You’ll receive a personalised report in Markdown format showing your current spend, recommended alternatives and projected savings.  The report includes footnotes linking to the sources used for pricing, so you can verify the recommendations.

4. **Ongoing optimisation (optional).**  For ongoing monitoring, SubSave offers a low‑cost subscription (currently **£10 per month**) that re‑audits your stack every quarter and notifies you when new savings opportunities appear.  Contact us via the form to upgrade.

## Running the Audit Locally

To run the audit yourself, clone this repository and install Python 3.9+.  The script reads a comma‑separated list of subscriptions with their monthly spend and produces a report:

```
bash
python audit_generator.py --subscriptions "Zoom=15.99, Notion=12.00, Figma=15.00" --output my_report.md
```

- **`--subscriptions`** accepts a comma‑separated list of `Name=cost` pairs.  Costs should be monthly figures in USD or GBP; the script converts annual plans to monthly equivalents where necessary.
- **`--output`** specifies the filename of the generated report.  If omitted, the report will print to stdout.

The script uses simple heuristics and may not cover every SaaS product.  Feel free to open an issue or submit a pull request to add more categories.  See the `data/pricing.json` file for the current pricing dataset.

## Expanding the Pricing Database

Our recommendations are only as good as the data behind them.  To improve the service, we’re always adding new tools and pricing information.  To contribute:

1. Fork this repository and update `data/pricing.json` with new entries following the existing structure.
2. If you know of free/open‑source alternatives or special startup discounts, include them in the `alternatives` field.
3. Submit a pull request with a brief description of the change and sources for the pricing data.

## Credits and Sources

This project relies on research articles and official pricing pages.  Key citations include:

- Binadox’s analysis of subscription sprawl, which notes that without centralised oversight it’s difficult to track total spending and that regular reviews are essential for cost control【941180497264979†L260-L266】【941180497264979†L306-L325】.
- Reports showing that mid‑sized businesses waste over **$135k per year** on unused subscriptions【63229005519729†L256-L265】.
- Pricing comparisons for Slack and Pumble【535664187725176†L92-L111】, Microsoft Teams plans【242066303498945†L415-L459】, Zoom vs Google Meet【936887458469851†L118-L131】【126525862450426†L140-L185】, Notion vs alternatives【419200397471211†L68-L90】【825146024898291†L124-L137】, Figma vs Penpot【340485894592476†L196-L200】【940708409433548†L351-L361】, Creative Cloud vs Affinity【460875596722571†L113-L116】【70593713864246†L51-L97】, and accounting tools like QuickBooks vs Wave【340485894592476†L196-L200】【983526885197130†L602-L604】.

Thanks for using SubSave – let’s save you some money!

"""Prompt templates for the CSV product enricher."""
import string
import pandas as pd

ENRICHMENT_PROMPT_TEMPLATE = """\
You are a product data specialist. Enrich the product below and return ONLY valid JSON.

Product:
- SKU: $sku
- Title: $title
- Description: $description

Example output:
{
  "seo_tags": "wireless earbuds, bluetooth headphones, noise cancelling, true wireless, sports earphones",
  "category": "Electronics > Audio > Headphones",
  "enhanced_description": "Experience crystal-clear audio with these premium wireless earbuds. Featuring advanced noise-cancellation, 8-hour battery life, and a secure sport fit, they are built for both work and play.",
  "readability_score": 8.5
}

Rules:
- seo_tags: 5 to 8 comma-separated keyword phrases, no generic single words
- category: hierarchical path using " > " separator
- enhanced_description: 2 to 3 sentences, benefit-driven, no hype words
- readability_score: float between 0.0 and 10.0 reflecting copy clarity

Return ONLY the JSON object. No explanation, no markdown, no extra text.

JSON:"""


def build_prompt(row: pd.Series) -> str:
    """Format the enrichment prompt for a single product row."""
    return string.Template(ENRICHMENT_PROMPT_TEMPLATE).safe_substitute(
        sku=row.get("sku", ""),
        title=row.get("title", ""),
        description=row.get("description", ""),
    )

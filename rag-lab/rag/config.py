"""Model names and prices for the AskIT RAG lab (UNext LXM demo kit).
Prices change often: verify at https://openai.com/api/pricing and edit here or in the app sidebar.
Values are USD per 1M tokens."""
import re

DEFAULT_CHAT_MODEL = "gpt-4o-mini"
DEFAULT_EMBED_MODEL = "text-embedding-3-small"

CHAT_MODEL_OPTIONS = ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini", "gpt-5-mini"]
EMBED_MODEL_OPTIONS = ["text-embedding-3-small", "text-embedding-3-large"]

PRICES = {
    # model: (input $/1M, output $/1M)  -- edit to match the official pricing page
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4o": (2.50, 10.00),
    "gpt-4.1-mini": (0.40, 1.60),
    "gpt-5-mini": (0.25, 2.00),
    "text-embedding-3-small": (0.02, 0.0),
    "text-embedding-3-large": (0.13, 0.0),
    "offline": (0.0, 0.0),
    "offline-hash": (0.0, 0.0),
}


def price_for(model, default=(0.15, 0.60)):
    return PRICES.get(model) or PRICES.get(re.sub(r"^(us|eu|apac)\.", "", model or ""), default)

"""Providers, model names and prices for the Orbi Prompt Lab (UNext LXM demo kit).
Prices change often: verify on the provider's pricing page and edit here or in the app sidebar.
Values are USD per 1M tokens (input, output)."""
import re

PROVIDERS = ["OpenAI", "Azure AI Foundry", "Offline demo"]

DEFAULT_CHAT_MODEL = "gpt-4o-mini"
CHAT_MODEL_OPTIONS = ["gpt-4o-mini", "gpt-4.1-mini", "gpt-4.1-nano", "gpt-4o", "gpt-5-mini"]

PRICES = {
    # model: (input $/1M, output $/1M)  -- edit to match the official pricing page
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4.1-mini": (0.40, 1.60),
    "gpt-4.1-nano": (0.10, 0.40),
    "gpt-4o": (2.50, 10.00),
    "gpt-5-mini": (0.25, 2.00),
    "offline-toy": (0.0, 0.0),
}

AZURE_DEFAULT_API_VERSION = "2025-04-01-preview"   # edit if your deployment needs another one


def price_for(model, default=(0.15, 0.60)):
    return PRICES.get(model) or PRICES.get(re.sub(r"^(us|eu|apac)\.", "", model or ""), default)


def is_reasoning_model(model):
    """gpt-5 / o-series: no temperature, uses reasoning_effort instead."""
    m = (model or "").lower()
    return m.startswith("gpt-5") or bool(re.match(r"^o\d", m))

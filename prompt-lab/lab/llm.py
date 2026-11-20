"""Thin wrapper over the model provider that records tokens, cost and latency for every call.
Providers: "OpenAI" (paste a key in the sidebar), "Azure AI Foundry" (Azure OpenAI deployments: endpoint + key +
deployment name) and "Offline demo" (no key: a deterministic toy model, see offline.py)."""
import threading
import time
from datetime import datetime

from . import offline
from .config import (AZURE_DEFAULT_API_VERSION, DEFAULT_CHAT_MODEL, PRICES, is_reasoning_model, price_for)
from .scoring import est_tokens


class UsageLog:
    """Every call lands here: operation, model, tokens, cost, latency. The Evals tab reads it."""

    def __init__(self):
        self.rows = []
        self._lock = threading.Lock()

    def add(self, op, model, tin, tout, latency_ms, prices=None, note=""):
        p = (prices or {}).get(model) or price_for(model, (0.0, 0.0))
        cost = tin / 1e6 * p[0] + tout / 1e6 * p[1]
        row = dict(time=datetime.now().strftime("%H:%M:%S"), operation=op, model=model,
                   input_tokens=int(tin), output_tokens=int(tout), cost_usd=round(cost, 6),
                   latency_ms=int(latency_ms), note=note)
        with self._lock:
            self.rows.append(row)
        return row


class LLM:
    def __init__(self, provider="Offline demo", api_key=None, endpoint=None, api_version=None,
                 chat_model=None, prices=None, log=None):
        self.provider = provider
        self.offline = provider == "Offline demo" or not api_key
        if self.offline:
            self.provider = "Offline demo"
        self.chat_model = chat_model or DEFAULT_CHAT_MODEL
        self.prices = prices or PRICES
        self.log = log or UsageLog()
        self.client = None
        if self.provider == "OpenAI":
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
        elif self.provider == "Azure AI Foundry":
            from openai import AzureOpenAI
            if not endpoint:
                raise ValueError("Azure AI Foundry needs the endpoint, for example https://<resource>.openai.azure.com/")
            self.client = AzureOpenAI(azure_endpoint=endpoint, api_key=api_key,
                                      api_version=api_version or AZURE_DEFAULT_API_VERSION)

    @property
    def live(self):
        return not self.offline

    @property
    def label(self):
        return "offline-toy" if self.offline else self.chat_model

    def complete(self, prompt, op="run", task=None, payload=None, model=None, temperature=0.2, max_tokens=500):
        """Returns (text, usage_row). task/payload are only used by the offline toy model."""
        t0 = time.perf_counter()
        if self.offline:
            text = offline.respond(task, prompt, payload or {})
            row = self.log.add(op, "offline-toy", est_tokens(prompt), est_tokens(text),
                               (time.perf_counter() - t0) * 1000, self.prices)
            return text, row
        model = model or self.chat_model             # on Azure this is the DEPLOYMENT name
        kwargs = dict(model=model, messages=[{"role": "user", "content": prompt}], max_completion_tokens=max_tokens)
        if is_reasoning_model(model):
            kwargs["reasoning_effort"] = "minimal"
            kwargs["max_completion_tokens"] = max(max_tokens, 800)
        else:
            kwargs["temperature"] = temperature
        resp = self.client.chat.completions.create(**kwargs)
        u = resp.usage
        row = self.log.add(op, model, u.prompt_tokens, u.completion_tokens, (time.perf_counter() - t0) * 1000, self.prices)
        return (resp.choices[0].message.content or "").strip(), row

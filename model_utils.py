import os
import json
import httpx

MODEL_CACHE_FILE = "model_cache.json"

DEFAULT_TEXT_MODELS = ["gpt-4o", "gpt-4", "gpt-3.5-turbo"]


def fetch_text_models(openai_key, proxy=None):
    try:
        headers = {"Authorization": f"Bearer {openai_key}"}

        transport = httpx.HTTPTransport(proxy=proxy["http"]) if proxy else None
        client = httpx.Client(transport=transport) if transport else httpx.Client()

        resp = client.get("https://api.openai.com/v1/models", headers=headers)
        models = resp.json().get("data", [])

        print("📡 Получено моделей:", len(models))
        filtered = [m["id"] for m in models if any(
            m["id"].startswith(prefix) for prefix in ["gpt-4", "gpt-3.5"])]

        # Сортировка: сначала gpt-4o, затем gpt-4.1, затем остальные
        def sort_key(model_id):
            if model_id == "gpt-4o":
                return (0, model_id)
            if model_id == "gpt-4.1":
                return (1, model_id)
            return (2, model_id)

        filtered.sort(key=sort_key)

        with open(MODEL_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(filtered, f)

        return filtered

    except Exception as e:
        print("⚠️ Ошибка при загрузке моделей:", e)
        return DEFAULT_TEXT_MODELS


def load_cached_text_models():
    if os.path.exists(MODEL_CACHE_FILE):
        try:
            with open(MODEL_CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return DEFAULT_TEXT_MODELS

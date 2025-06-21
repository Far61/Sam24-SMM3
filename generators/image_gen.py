import os
import re
import base64
import httpx
import datetime
from openai import OpenAI

def log_openai_event(model, direction, data):
    log_path = "generation.log"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] [{model}] [{direction}] {data}\n")

class ImageGenerator:
    def __init__(self, openai_key, image_model="gpt-image-1", proxy=None, size="1024x1024", quality=None, style=None):
        self.model = image_model
        self.size = size
        self.quality = quality
        self.style = style

        transport = httpx.HTTPTransport(proxy=proxy["http"]) if proxy else None
        client = httpx.Client(transport=transport, timeout=60) if transport else None

        self.client = OpenAI(api_key=openai_key, http_client=client)

    def generate_image(self, prompt):
        try:
            kwargs = {
                "model": self.model,
                "prompt": prompt,
                "size": self.size,
                "n": 1
            }
            if self.model == "gpt-image-1":
                if self.quality:
                    kwargs["quality"] = self.quality
            elif self.model == "dall-e-3":
                if self.quality:
                    kwargs["quality"] = self.quality
                if self.style:
                    kwargs["style"] = self.style
                kwargs["response_format"] = "b64_json"
            elif self.model == "dall-e-2":
                kwargs["response_format"] = "b64_json"

            # Логируем отправку
            log_openai_event(self.model, "request", str(kwargs))

            response = self.client.images.generate(**kwargs)

            # Логируем ответ (только часть base64, чтобы не засорять лог)
            resp_info = f"data[0].b64_json: {str(response.data[0].b64_json)[:40]}..." if response.data and hasattr(response.data[0], "b64_json") else str(response)
            log_openai_event(self.model, "response", resp_info)

            if not response.data or not hasattr(response.data[0], "b64_json") or not response.data[0].b64_json:
                raise ValueError(f"⚠️ Модель не вернула изображение. Ответ: {response}")

            image_base64 = response.data[0].b64_json

        except Exception as e:
            log_openai_event(self.model, "error", str(e))
            print(f"[ImageGenerator] Ошибка от OpenAI: {e}")
            raise

        # Сохраняем изображение из base64
        safe_name = re.sub(r"[^\w\d-]", "_", prompt).strip("_").lower()
        filename = safe_name[:50] + ".png"
        filepath = os.path.join("app", "static", "generated", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        try:
            with open(filepath, "wb") as f:
                f.write(base64.b64decode(image_base64))
        except Exception as e:
            print(f"[ImageGenerator] Ошибка при сохранении изображения: {e}")
            raise

        return filepath
import httpx
from openai import OpenAI
import datetime

def log_openai_event(model, direction, data):
    log_path = "generation.log"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] [{model}] [{direction}] {data}\n")

class PostGenerator:
    def __init__(self, openai_key, topic, tone, system_text_prompt=None, system_image_prompt=None, proxy=None):
        self.topic = topic
        self.tone = tone
        self.system_text_prompt = system_text_prompt
        self.system_image_prompt = system_image_prompt
        self.proxy = proxy

        transport = httpx.HTTPTransport(proxy=proxy["http"]) if proxy else None
        client = httpx.Client(transport=transport, timeout=120) if transport else None

        self.client = OpenAI(
            api_key=openai_key,
            http_client=client
        )

    def generate_post(self):
        system_prompt = self.system_text_prompt if self.system_text_prompt is not None else (
            "Ты — копирайтер Digital-студии SAM-24. Цель: по заданной теме создать пост "
            "для VK и Telegram. Требования к посту: "
            "1. Язык — русский, деловой-дружелюбный, без канцелярита. "
            "2. Тон — эксперт + забота делимся опытом, помогаем аудитории. "
            "3. Объём — 900–1200 символов. "
            "4. Структура — Hook (≤120 зн.); 2–4 абзаца раскрытия темы "
            "(факты, выгоды, примеры); CTA одной строкой. "
            "5. Без ссылок, телефонов и прямой рекламы. "
            "Вывод: готовый текст поста без дополнительных комментариев."
        )

        user_prompt = (
            f"Напиши пост во ВКонтакте на тему: {self.topic}. "
            f"Аудитория: владельцы бизнеса, маркетологи, разработчики. "
            f"Объём: до 1 200 знаков, цель — информировать и вызвать интерес без прямой продажи. "
            f"Избегай эмодзи и не ставь «звёздочки» вокруг слов."
        )

        model = "gpt-4o"
        # Логируем отправку
        log_openai_event(model, "request", f"system: {system_prompt} | user: {user_prompt}")

        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )

        # Логируем ответ
        log_openai_event(model, "response", response.choices[0].message.content.strip())
        return response.choices[0].message.content.strip()

    def generate_post_image_description(self, post_text):
        system_prompt = self.system_image_prompt if self.system_image_prompt is not None else (
            "Ты — арт-директор Digital-студии SAM-24. Получив текст поста, составь ОДНУ "
            "строку text-to-image prompt для OpenAI GPT-4o Images, чтобы с первого раза "
            "получить вирусную иллюстрацию для соцсетей.\n\n"
            "• Стиль — современная плоская векторная графика / чистая инфографика, никаких "
            "фотореалистичных элементов.\n"
            "• Палитра — если автор не указал другую, используй фирменные SAM-24: "
            "индиго-синий #1C64F2, янтарный #FFB800, тёмный #2D334A, белый #FFFFFF "
            "(можно добавить 1–2 гармоничных оттенка при необходимости).\n"
            "• Композиция — ОДИН легкоузнаваемый символ/пиктограмма (эмодзи-подобный или "
            "простой предмет), однозначно связанный с темой поста; не масштабируй объект "
            "за пределы кадра, оставь вокруг него ≥15 % свободного пространства. "
            "Допускается ≤3 второстепенных иконки фоном.\n"
            "• Персона: по умолчанию используй фирменного маскота SAMmy — дружелюбный "
            "кубический робот цвета #1C64F2 с янтарными акцентами, если персона усиливает "
            "идею поста. В серьёзных темах (законы, безопасность, комплаенс) заменяй "
            "маскота на стилизованный объект-персону (например, документ-щит или "
            "замок-экран) или укажи «без персонажа».\n"
            "• Текст в кадре — ≤8 слов кириллицей, гротеск (sans-serif), контрастный к "
            "фону. Исключения кириллицы только для названий брендов/компаний. Гарантируй "
            "ширину надписи ≤80 % кадра и ≥10 % пустого места по бокам, чтобы текст не "
            "обрезался.\n"
            "• Система отсечений — в prompt явно пиши «без кислотных цветов, визуального "
            "шума, водяных знаков, искажённого текста, обрезанных элементов».\n"
            "• Цель — чтобы идея поста понималась <3 сек и аудитории хотелось поделиться.\n\n"
            "Формат ответа: верни одну строку без переносов, начинающуюся сразу с описания "
            "сцены и содержащую ключевой символ, (при необходимости) SAMmy или объект-"
            "персону, палитру, русский текст, безопасные отступы и запреты («без …»)."
        )
        user_prompt = (
            f"Придумай промт для генерации изображения к следующему посту для социальной сети ВКонтакте:\n\n"
            f"{post_text}\n\n"
        )

        model = "gpt-4o"
        log_openai_event(model, "request", f"system: {system_prompt} | user: {user_prompt}")

        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )

        log_openai_event(model, "response", response.choices[0].message.content.strip())
        return response.choices[0].message.content.strip()

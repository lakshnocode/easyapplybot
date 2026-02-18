from __future__ import annotations

import json

import httpx

from .runtime_settings import runtime_settings_store


class AIAnswerer:
    async def answer(self, question: str, options: list[str] | None = None, profile: dict | None = None) -> str:
        runtime_settings = runtime_settings_store.get()
        if not runtime_settings.openai_api_key:
            return self._fallback(question, options)

        prompt = {
            'question': question,
            'options': options or [],
            'profile': profile or {},
            'instruction': (
                'Return only the best answer text for a job application question. '
                'If options are present, return one exact option value. Keep it concise and truthful.'
            ),
        }

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                'https://api.openai.com/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {runtime_settings.openai_api_key}',
                    'Content-Type': 'application/json',
                },
                json={
                    'model': runtime_settings.openai_model,
                    'messages': [
                        {'role': 'system', 'content': 'You answer job application screening questions.'},
                        {'role': 'user', 'content': json.dumps(prompt)},
                    ],
                    'temperature': 0.2,
                },
            )
            response.raise_for_status()
            payload = response.json()
            return payload['choices'][0]['message']['content'].strip()

    def _fallback(self, question: str, options: list[str] | None = None) -> str:
        lowered = question.lower()
        if options:
            preferred = ['yes', 'authorized', 'no sponsorship', 'remote', 'full-time']
            for pref in preferred:
                for opt in options:
                    if pref in opt.lower():
                        return opt
            return options[0]
        if 'salary' in lowered:
            return 'Negotiable based on total compensation package and role scope.'
        if 'experience' in lowered:
            return '5'
        return 'Yes'

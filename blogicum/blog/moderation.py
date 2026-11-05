from functools import cache

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification


@cache
def _get_model_and_tokenizer():
    model = AutoModelForSequenceClassification.from_pretrained(
        "cointegrated/rubert-tiny-toxicity"
    )
    tokenizer = AutoTokenizer.from_pretrained(
        "cointegrated/rubert-tiny-toxicity"
    )
    return model, tokenizer


def _load_model_and_tokenizer():
    model, tokenizer = _get_model_and_tokenizer()
    model.eval()
    return model, tokenizer


def get_toxicity_score(text: str) -> float:
    model, tokenizer = _load_model_and_tokenizer()
    with torch.inference_mode():
        inputs = tokenizer(
            text, return_tensors="pt", truncation=True, max_length=512
        )
        with torch.no_grad():
            outputs = model(**inputs)
        scores = outputs.logits.numpy()[0]
        toxicity_score = float(scores[1])
    return toxicity_score


def is_toxic(text: str) -> bool:
    from core.constants import TOXICITY_THRESHOLD

    return get_toxicity_score(text) >= TOXICITY_THRESHOLD

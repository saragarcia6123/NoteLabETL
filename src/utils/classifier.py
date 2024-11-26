import pandas as pd
import spacy
from transformers import pipeline
import torch
import json
from concurrent.futures import ThreadPoolExecutor
import torch.multiprocessing as mp
from functools import partial

class Classifier:

    def __init__(self, task, model):
        device = torch.cuda.current_device()
        self.classifier = pipeline(task, model=model, device=device, fp16=True)
        self.nlp = spacy.load("en_core_web_sm")
    
    def _tokenize(self, text):
        doc = self.nlp(text)
        tokens = [token.text.lower() for token in doc if not token.is_stop and not token.is_punct]
        return ' '.join(tokens)

    def _classify_set(self, texts, labels):
        non_empty_texts = [text for text in texts if text.strip()]
        empty_indices = {i for i, text in enumerate(texts) if not text.strip()}
        
        non_empty_results = self.classifier(non_empty_texts, labels)

        all_results = [{label: 0.0 for label in labels} for _ in texts]
        non_empty_index = 0
        for i in range(len(texts)):
            if i not in empty_indices:
                all_results[i] = {
                    label: non_empty_results[non_empty_index]['scores'][j]
                    for j, label in enumerate(labels)
                }
                non_empty_index += 1
        
        return all_results

    def _classify_sets(self, texts, label_sets, num_workers=4):
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(partial(self._classify_set, texts, labels)) for labels in label_sets]
            results = [future.result() for future in futures]
        return results

    def _flatten(self, data):
        flattened = {}
        for item in data:
            flattened.update(item)
        return flattened

    def classify(self, texts, label_sets):
        texts = [self._tokenize(text) for text in texts]
        results = self._classify_sets(texts, label_sets)
        data = list(zip(*results))
        return [self._flatten(d) for d in data]
import json

class BenchmarkDataset:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.data = None

    def load_data(self):
        with open(self.filepath, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        print(f"Loaded {len(self.data)} samples from {self.filepath}")
        return self.data

    def preprocess_data(self):
        # Implement your preprocessing steps here if needed
        pass
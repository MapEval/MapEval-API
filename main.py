from BenchmarkDataset import BenchmarkDataset
from Evaluator2 import Evaluator
from GeminiPro import GeminiPro
from GeminiFlash import GeminiFlash
from GPTAzure import GPTAzure
from ChatGPT import ChatGPT
from Claude import Claude
from Gemma2 import Gemma2
from Llama3_1 import Llama3_1
from Mixtral import Mixtral
from Llama3_1_8B import Llama3_1_8B
from GPT4 import GPT4
from GPT_4o_mini import GPT_4o_mini
from Llama3_2 import Llama3_2
import argparse


def main():
    parser = argparse.ArgumentParser(description="Evaluate a model.")
    parser.add_argument("model", type=str, help="Name of the model to evaluate")
    args = parser.parse_args()

    # Load and preprocess dataset
    dataset = BenchmarkDataset(filepath="dataset.json")
    dataset.preprocess_data()

    # Initialize models
    if args.model == "GPT":
        model = GPTAzure()
    elif args.model == "GeminiPro":
        model = GeminiPro()
    elif args.model == "GeminiFlash":
        model = GeminiFlash()
    elif args.model == "ChatGPT":
        model = ChatGPT()
    elif args.model == "Claude":
        model = Claude()
    elif args.model == "Gemma2":
        model = Gemma2()
    elif args.model == "Llama3.1":
        model = Llama3_1()
    elif args.model == "Mixtral":
        model = Mixtral()
    elif args.model == "Llama3.1.8B":
        model = Llama3_1_8B()
    elif args.model == "GPT4":
        model = GPT4()
    elif args.model == "GPT_4o_mini":
        model = GPT_4o_mini()
    elif args.model == "Llama3.2":
        model = Llama3_2()
    else:
        raise ValueError(f"Model {args.model} not recognized.")

    # Evaluate each model
    print(f"Evaluating model: {model.__class__.__name__}")
    evaluator = Evaluator(model=model, dataset=dataset)
    evaluator.evaluate()
    evaluator.print_results()
    print(model.__class__.__name__, "metrics")
    evaluator.compute_metrics()


if __name__ == "__main__":
    main()

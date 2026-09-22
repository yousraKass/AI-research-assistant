# methodology_extraction v1

Extract the methodology details from the paper text. Provide a short JSON object with keys: "methods", "datasets", "models", "metrics". Use arrays of strings for each field. If a field is unknown, return an empty array for it.

Input: {text}

Example output:
{
  "methods": ["contrastive pretraining", "fine-tuning with cross-entropy"],
  "datasets": ["ImageNet", "CIFAR-10"],
  "models": ["ResNet-50"],
  "metrics": ["accuracy", "F1"]
}

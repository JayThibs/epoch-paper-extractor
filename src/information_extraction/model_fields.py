MODEL_FIELDS = {
    "abstract": {"type": "text", "prompt": "What is the abstract of the paper?"},
    "authors": {"type": "text", "prompt": "Who are the authors of the paper?"},
    "base_model": {"type": "categorical", "prompt": "What base model, if any, was this model fine-tuned from?"},
    "batch_size": {"type": "numeric", "prompt": "What was the batch size used during training?"},
    "citations": {"type": "numeric", "prompt": "How many citations does this paper have?"},
    "confidence": {"type": "categorical", "prompt": "What is the confidence level in the recorded values for Training compute, Parameters, and Training dataset size?"},
    "country": {"type": "categorical", "prompt": "What country or countries are associated with the developing organization(s)?"},
    "domain": {"type": "categorical", "prompt": "What is the machine learning domain of application for this model?"},
    "epochs": {"type": "numeric", "prompt": "How many epochs were used to train the model?"},
    "finetune_compute": {"type": "numeric", "prompt": "How much compute was used to fine-tune the model, if applicable?"},
    "hardware_quantity": {"type": "numeric", "prompt": "What quantity of hardware was used in training?"},
    "hardware_utilization": {"type": "numeric", "prompt": "What was the hardware utilization ratio?"},
    "link": {"type": "url", "prompt": "What are the links to the best sources documenting this model?"},
    "notability_criteria": {"type": "categorical", "prompt": "What notability criteria does this model meet?"},
    "organization": {"type": "categorical", "prompt": "What organization(s) created the model?"},
    "organization_categorization": {"type": "categorical", "prompt": "How is the organization categorized?"},
    "parameters": {"type": "numeric", "prompt": "How many learnable parameters does the model have?"},
    "publication_date": {"type": "date", "prompt": "What is the publication, announcement, or release date of the model?"},
    "reference": {"type": "text", "prompt": "What is the literature reference for the model?"},
    "system": {"type": "text", "prompt": "What is the name of the model?"},
    "training_compute": {"type": "numeric", "prompt": "How much compute was used to train the model, in FLOP?"},
    "training_compute_cost": {"type": "numeric", "prompt": "What was the estimated training compute cost in 2023 USD?"},
    "training_dataset": {"type": "categorical", "prompt": "What dataset(s) was used to train the model?"},
    "training_dataset_size": {"type": "numeric", "prompt": "How many datapoints were in the training dataset?"},
    "training_hardware": {"type": "categorical", "prompt": "What type of training hardware was used?"},
    "training_time": {"type": "numeric", "prompt": "How long did the training take, in hours?"},
    "model_architecture_diagram": {
        "type": "text", 
        "prompt": "Describe the model architecture based on any diagrams or figures in the paper.", 
        "requires_image": True
    },
    "performance_graphs": {
        "type": "text", 
        "prompt": "Analyze any performance graphs or charts in the paper and describe the model's performance trends.", 
        "requires_image": True
    }
}
from transformers import AutoProcessor, AutoModelForZeroShotImageClassification
import os


def load_model():
    try:
        model_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../model"))
        processor = AutoProcessor.from_pretrained(model_dir)
        model = AutoModelForZeroShotImageClassification.from_pretrained(model_dir)
        return processor, model
    except Exception as e:
        raise RuntimeError(f"Error loading model: {str(e)}") from e
import os
from torch import autocast
from diffusers import StableDiffusionPipeline

SDV5_MODEL_PATH = os.getenv('SDV5_MODEL_PATH')
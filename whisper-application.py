import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import time

# Set the device to CPU and specify the torch data type
device = "cpu"
torch_dtype = torch.float32

# Specify the model name
model_id = "openai/whisper-large-v3-turbo"

# Load the model with specified configurations
model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
)

# Move the model to the specified device
model.to(device)

# Load the processor for the model
processor = AutoProcessor.from_pretrained(model_id)

# Create a pipeline for automatic speech recognition
pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    torch_dtype=torch_dtype,
    device=device,
    return_timestamps=True
)

# Record the start time of the inference
start_time = time.time()

# Perform speech recognition on the audio file
result = pipe("OSR_us_000_0010_8k.wav")

# Record the end time of the inference
end_time = time.time()

# Print the transcribed text
print(f'\n{result["text"]}\n')

# Calculate and print the duration of the inference
duration = end_time - start_time
msg = f'\nInferencing elapsed time: {duration:4.2f} seconds\n'

print(msg)
# Whisper-Cleaner
Whisper Cleaner leverages timestamped multi-lingual speech-to-text generation from [OpenAI's Whisper Model](https://github.com/openai/whisper) to recognize and remove language deemed obscene, indecent, or profane by the FCC from audio intended for radio and television broadcasts. The package uses [**whisper-timestamped**](https://github.com/linto-ai/whisper-timestamped) from linto-ai for text generation and mapping, and **profanity-check** from vzhou842 profanity prediction.

## Usage

Whisper Cleaner can be used from the command line with only three arguments
```bash
whisper-cleaner [Input Directory] [Model Size]

## Setup

To create a conda environment with all the necessary dependencies, run the following command from within the top directory:

```bash
conda env create -f whisper-cleaner.yml

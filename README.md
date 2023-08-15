# Whisper-Cleaner
Whisper Cleaner leverages timestamped multi-lingual speech-to-text generation from [OpenAI's Whisper Model](https://github.com/openai/whisper) to recognize and remove language deemed obscene, indecent, or profane by the FCC from audio intended for radio and television broadcasts. The package uses [**whisper-timestamped**](https://github.com/linto-ai/whisper-timestamped) from linto-ai for text generation and mapping, and **profanity-check** from vzhou842 profanity prediction.

## Usage

Whisper Cleaner can be used from the command line with the following
```bash
whisper-cleaner [Input Directory] [Model Size]
```
The input directory should contain all audio files to be processed. By default, the output directory will be the same as the input directory, and completed songs will be moved to a subdirectory called `Originals`. The speed and accuracy of predictions can be controlled by changing the `model_size` between any of the default Whisper models (`tiny`, `small`, `base`, `medium`, and `large`). The default model size is `base`.

## Setup

To create a conda environment with all the necessary dependencies, run the following command from within the top directory:

```bash
conda env create -f whisper-cleaner.yml

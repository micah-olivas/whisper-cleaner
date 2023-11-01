# Whisper-Cleaner
Whisper-Cleaner is a robust tool that utilizes OpenAI's Whisper Model for precise, timestamped speech-to-text analysis to automatically detect and excise profanity from audio files, ensuring FCC compliance for broadcast content (e.g. radio broadcasts or televised audio).

This solution integrates [**whisper-timestamped**](https://github.com/linto-ai/whisper-timestamped) for accurate text mapping and employs [**profanity-check**](https://github.com/vzhou842/profanity-check) for reliable profanity detection across multiple languages.

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

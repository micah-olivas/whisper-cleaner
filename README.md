# Whisper-Cleaner
Whisper-Cleaner is a robust tool that utilizes [OpenAI's Whisper Model](https://github.com/openai/whisper) for precise, timestamped speech-to-text analysis to automatically detect and excise profanity from audio files, ensuring FCC compliance for broadcast content (e.g. radio broadcasts or televised audio).

This solution integrates [**whisper-timestamped**](https://github.com/linto-ai/whisper-timestamped) for accurate text mapping and employs [**profanity-check**](https://github.com/vzhou842/profanity-check) for reliable profanity detection across multiple languages.

## Installation

Clone the repository and install in development mode:

```bash
git clone https://github.com/micaholivas/whisper-cleaner.git
cd whisper-cleaner
pip install -e .
```

Or using conda:
```bash
git clone https://github.com/micaholivas/whisper-cleaner.git
cd whisper-cleaner
conda env create -f whisper-cleaner.yml
conda activate whisper-cleaner
pip install -e .
```

## Usage

### Basic Usage
```bash
whisper-cleaner /path/to/audio
```

### Advanced Options
```bash
whisper-cleaner /path/to/audio -m large                  # Use large model for better accuracy
whisper-cleaner /path/to/audio -o /path/to/output        # Specify output directory
whisper-cleaner /path/to/audio -t 0.95                   # Adjust profanity threshold
whisper-cleaner /path/to/audio --dry-run                 # Preview without processing
whisper-cleaner /path/to/audio -v                        # Verbose output
whisper-cleaner /path/to/audio -q                        # Quiet mode
```

### Command Line Options

| Option | Description |
|--------|-------------|
| `input_directory` | Directory containing audio files to process |
| `-m, --model-size` | [Whisper model](https://github.com/openai/whisper#available-models-and-languages) size: `tiny`, `base`, `small`, `medium`, `large` (default: `base`) |
| `-o, --output-directory` | Output directory for cleaned files (default: same as input) |
| `-t, --threshold` | Profanity detection threshold 0-1 (default: 0.98) |
| `-v, --verbose` | Enable verbose output |
| `-q, --quiet` | Suppress all non-error output |
| `--dry-run` | Preview what would be processed without making changes |
| `--version` | Show version number |
| `-h, --help` | Show help message |

### Supported Audio Formats
- MP3 (`.mp3`)
- M4A (`.m4a`)
- WAV (`.wav`)
- OGG (`.ogg`)
- FLAC (`.flac`)

### Output Structure
```
output_directory/
├── clean_song1.mp3          # Cleaned audio files
├── clean_song2.mp3
├── originals/               # Original files (moved after processing)
│   ├── song1.mp3
│   └── song2.mp3
└── logging/                 # Processing logs and metadata
    ├── song1/
    │   ├── log.txt
    │   ├── profanity_preds.txt
    │   └── result.json
    └── song2/
        ├── log.txt
        ├── profanity_preds.txt
        └── result.json
```

## Development

### Running Tests
```bash
make test
```

Or directly with pytest:
```bash
python -m pytest tests/
```

### Building
```bash
make build
```

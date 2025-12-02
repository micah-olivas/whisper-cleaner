### WHISPER CLEANER ###
# Author: Micah Olivas
# Date Created: 2023-04-01
# Description: This script takes a directory of mp3 files and transcribes them using 
#             a model adapted from OpenAI's Whisper library that provides
#             timestamps for each word. It then detects prohibited words from the 
#             transcriptions using the profanity_check library, edits the audio files
#             to remove the prohibited words, and writes edited mp3 files to a new directory
# Command line usage: python whisper_clean.py [input directory] [model_size]


# Import general libraries
import glob
import sys
import os
import json
import argparse
from art import *

# import text and sound processing libraries
import whisper_timestamped as whisper
from profanity_check import predict_prob
from pydub import AudioSegment


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Clean audio files by removing profanity using OpenAI\'s Whisper model.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  whisper-cleaner /path/to/audio                    # Process with default settings
  whisper-cleaner /path/to/audio -m large           # Use large model for better accuracy
  whisper-cleaner /path/to/audio -o /path/to/output # Specify output directory
  whisper-cleaner /path/to/audio --dry-run          # Preview without processing
        '''
    )
    parser.add_argument('input_directory', type=str, help='Directory containing audio files to be cleaned')
    parser.add_argument('-m', '--model-size', type=str, default='base',
                        choices=['tiny', 'base', 'small', 'medium', 'large'],
                        help='Whisper model size (default: base). Larger models are more accurate but slower.')
    parser.add_argument('-o', '--output-directory', type=str, default=None,
                        help='Output directory for cleaned files (default: same as input directory)')
    parser.add_argument('-t', '--threshold', type=float, default=0.98,
                        help='Profanity detection threshold from 0-1 (default: 0.98)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Enable verbose output')
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='Suppress all non-error output')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be processed without making changes')
    parser.add_argument('--version', action='version', version='whisper-cleaner 0.1.0')
    args = parser.parse_args()

    # Validate arguments
    if args.quiet and args.verbose:
        parser.error("Cannot use both --quiet and --verbose")

    # Print the title unless in quiet mode
    if not args.quiet:
        art_title = text2art("Whisper Cleaner", font='swan', chr_ignore=True)
        print(art_title)

    # Assign input directory and model size
    input_directory = os.path.abspath(args.input_directory)
    model_size = args.model_size
    output_directory = args.output_directory if args.output_directory else input_directory
    threshold = args.threshold

    # Validate input directory exists
    if not os.path.exists(input_directory):
        print(f"Error: Input directory '{input_directory}' does not exist.")
        sys.exit(1)

    if not os.path.isdir(input_directory):
        print(f"Error: '{input_directory}' is not a directory.")
        sys.exit(1)

    if not args.quiet:
        print(f"Input directory: {input_directory}")
        print(f"Output directory: {output_directory}")
        print(f"Using model size: {model_size}")
        print(f"Profanity threshold: {threshold}")
        if args.dry_run:
            print("DRY RUN MODE - No files will be modified\n")

    # Logging helper functions
    def log_info(message):
        """Print info message unless in quiet mode"""
        if not args.quiet:
            print(message)

    def log_verbose(message):
        """Print verbose message only in verbose mode"""
        if args.verbose:
            print(f"[VERBOSE] {message}")

    def log_error(message):
        """Always print error messages"""
        print(f"ERROR: {message}", file=sys.stderr)

    # Get all audio files in the directory
    def get_files(directory):
        files = glob.glob(directory + '/*.mp3')
        files.extend(glob.glob(directory + '/*.m4a'))
        files.extend(glob.glob(directory + '/*.wav'))
        files.extend(glob.glob(directory + '/*.ogg'))
        files.extend(glob.glob(directory + '/*.flac'))
        return files, directory

    # Transcribe the file
    def transcribe_file(file, model_size="base"):
        log_verbose(f"Loading Whisper model: {model_size}")
        model = whisper.load_model(model_size)
        log_verbose(f"Loading audio file: {file}")
        audio = whisper.load_audio(file)
        log_verbose("Transcribing audio...")
        result = whisper.transcribe(model, audio, language="en")
        return result


    ### GET FILES ###
    log_info(f"Scanning for audio files in: {input_directory}")
    files, working_directory = get_files(input_directory)

    if not files:
        log_error(f"No audio files found in {input_directory}")
        sys.exit(1)

    log_info(f"Found {len(files)} audio file(s) to process")
    if args.verbose:
        for f in files:
            log_verbose(f"  - {os.path.basename(f)}")

    ### CREATE DIRECTORIES ###
    logging_directory = os.path.join(output_directory, 'logging')
    completed_directory = os.path.join(output_directory, 'originals')

    if args.dry_run:
        log_info(f"\nWould create directories:")
        log_info(f"  - {logging_directory}")
        log_info(f"  - {completed_directory}")
    else:
        if not os.path.exists(logging_directory):
            os.makedirs(logging_directory)
            log_verbose(f"Created logging directory: {logging_directory}")
        if not os.path.exists(completed_directory):
            os.makedirs(completed_directory)
            log_verbose(f"Created originals directory: {completed_directory}")


    ### LOOP THROUGH FILES ###
    processed_count = 0
    skipped_count = 0
    error_count = 0

    log_info(f"\n{'='*60}")
    log_info("Starting processing...")
    log_info(f"{'='*60}\n")

    for idx, file in enumerate(files, 1):
        try:
            ### CHECK IF FILE HAS ALREADY BEEN CLEANED ###
            filename = os.path.basename(file)
            if filename.startswith('clean_'):
                log_verbose(f"Skipping already cleaned file: {filename}")
                skipped_count += 1
                continue

            ### PROGRESS INDICATOR ###
            log_info(f"\n[{idx}/{len(files)}] Processing: {filename}")

            if args.dry_run:
                log_info(f"  Would transcribe and clean: {file}")
                continue

            ### CREATE SONG DIR ###
            song_name = os.path.splitext(filename)[0]
            song_directory = os.path.join(logging_directory, song_name)
            if not os.path.exists(song_directory):
                os.makedirs(song_directory)
                log_verbose(f"Created song directory: {song_directory}")

            ### TRANSCRIBE THE FILE ###
            log_info("  Transcribing audio...")
            result = transcribe_file(file, model_size=model_size)

            # Print first snippet of text
            text_preview = result['text'][:100] + '...' if len(result['text']) > 100 else result['text']
            log_info(f"  Found text: {text_preview}")
            log_verbose(f"  Total segments: {len(result['segments'])}")

            ### CREATE PROFANITY LOG FILE ###
            profanity_file_name = os.path.join(song_directory, 'profanity_preds.txt')
            with open(profanity_file_name, 'w') as f:
                f.write(f'Model Size: {model_size}\n')
                f.write(f'Threshold: {threshold}\n')
                f.write('word\tprediction\tstart_time\n')

            ### LOAD THE AUDIO FILE ###
            log_info("  Loading audio for editing...")
            sound_file = AudioSegment.from_file(file)

            ### CHECK FOR AND REMOVE PROHIBITED WORDS ###
            profane_words_found = 0
            total_words = 0

            log_info("  Detecting profanity...")
            for segment_id in range(len(result['segments'])):
                word_set = result['segments'][segment_id]['words']

                for num, word_data in enumerate(word_set):
                    total_words += 1
                    word = word_data['text'].lower()
                    prob = predict_prob([word])[0]

                    # Write each word and profanity prediction to log file
                    with open(profanity_file_name, 'a') as f:
                        f.write(f"{word}\t{prob:.4f}\t{word_set[num]['start']:.2f}\n")

                    # Check if word exceeds threshold
                    if prob > threshold:
                        profane_words_found += 1
                        start_time = word_set[num]['start']
                        end_time = word_set[num]['end']

                        # Convert time to milliseconds
                        begin = int(start_time * 1000 - 90)
                        end = int(end_time * 1000)

                        log_verbose(f"  Censoring '{word}' (prob: {prob:.2f}) at {start_time:.2f}s")

                        # Reverse audio segment to censor
                        silence_segment = AudioSegment.reverse(sound_file[begin:end])
                        sound_file = sound_file[:begin] + silence_segment + sound_file[end:]

            if profane_words_found > 0:
                log_info(f"  Detected and censored {profane_words_found} profane word(s) out of {total_words} total words")
            else:
                log_info(f"  No profanity detected in {total_words} words")


            ### EXPORT THE CLEAN FILE ###
            log_info("  Exporting cleaned audio...")
            file_ext = os.path.splitext(filename)[1][1:]  # Get extension without dot
            clean_filename = f'clean_{filename}'
            clean_file = os.path.join(output_directory, clean_filename)

            # Export the clean file
            sound_file.export(clean_file, format=file_ext)
            log_info(f"  Saved: {clean_filename}")

            # Move the original audio file to the completed directory
            original_destination = os.path.join(completed_directory, filename)
            os.rename(file, original_destination)
            log_verbose(f"  Moved original to: {original_destination}")

            ### LOG THE RESULTS ###
            log_file = os.path.join(song_directory, 'log.txt')
            with open(log_file, 'w') as f:
                f.write(f'Song: {filename}\n')
                f.write(f'Model: {model_size}\n')
                f.write(f'Threshold: {threshold}\n')
                f.write(f'Total words: {total_words}\n')
                f.write(f'Profane words: {profane_words_found}\n')
                f.write(f'Text preview: {text_preview}\n')

            # Save full transcription result
            result_file = os.path.join(song_directory, 'result.json')
            with open(result_file, 'w') as f:
                json.dump(result, f, indent=2)

            processed_count += 1

        except Exception as e:
            log_error(f"Failed to process {filename}: {str(e)}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            error_count += 1
            continue

    ### PRINT COMPLETION SUMMARY ###
    log_info(f"\n{'='*60}")
    log_info("Processing complete!")
    log_info(f"{'='*60}")
    log_info(f"  Processed: {processed_count}")
    log_info(f"  Skipped: {skipped_count}")
    if error_count > 0:
        log_info(f"  Errors: {error_count}")
    log_info(f"{'='*60}\n")

    if error_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
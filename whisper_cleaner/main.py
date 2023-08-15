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
    parser = argparse.ArgumentParser(description='Clean audio files using a model adapted from OpenAI\'s Whisper library.')
    parser.add_argument('input_directory', metavar='input_directory', type=str, nargs='?', default='.', help='The directory containing the audio files to be cleaned.')
    parser.add_argument('model_size', metavar='model_size', type=str, nargs='?', default='base', help='The size of the model to use. Options are "base" and "large".')
    parser.add_argument('-i', '--input_directory', type=str, help='The directory containing the audio files to be cleaned.')
    parser.add_argument('-m', '--model_size', type=str, help='The size of the model to use. Common options are "base" and "large", but more options are available. See the README for more information.')
    args = parser.parse_args()


    # Print the title
    art_title = text2art("Whisper Cleaner", font='swan', chr_ignore=True)
    print(art_title)

    # Assign input directory and model size
    input_directory = args.input_directory
    model_size = args.model_size
    print("Using model size: " + model_size)

    # Get all audio files in the directory
    def get_files(directory):
        files = glob.glob(directory + '/*.mp3')
        files.extend(glob.glob(directory + '/*.m4a')) # Add m4a files to the list
        files.extend(glob.glob(directory + '/*.wav')) # Add wav files to the list
        files.extend(glob.glob(directory + '/*.ogg')) # Add ogg files to the list
        files.extend(glob.glob(directory + '/*.flac')) # Add flac files to the list
        return files, directory

    # Transcribe the file
    def transcribe_file(file, model_size="base"):
        model = whisper.load_model(model_size) # Load the model
        audio = whisper.load_audio(file) # Load the audio file
        result = whisper.transcribe(model, audio, language="en") # Transcribe the audio file
        return result


    ### GET FILES ###
    # Get all files
    print("Getting mp3 files from directory: " + input_directory)
    files, working_directory = get_files(input_directory)


    ### CREATE DIRECTORIES ###
    logging_directory = working_directory + '/logging'
    completed_directory = working_directory + '/originals'

    if not os.path.exists(logging_directory):
        os.makedirs(logging_directory)
    if not os.path.exists(completed_directory):
        os.makedirs(completed_directory)


    ### LOOP THROUGH FILES ###
    # Loop through the files
    for file in files:

        ### UPDATE FILE LIST ###
        # check the list of files to see if 
        # any new files have been added
        print("Checking for new files...")
        files, working_directory = get_files(input_directory)

        ### CHECK IF ANY FILES ARE INCOMPLETE ###
        # Check if any files are incomplete
        for file in files:
            if file.split('/')[-1].startswith('clean_'):
                continue
            else:
                break

        ### CHECK IF FILE HAS ALREADY BEEN CLEANED ###
        # Check if the file has already been cleaned
        if file.split('/')[-1].startswith('clean_'):
            continue
        else:
            pass

        ### CREATE SONG DIR ###
        # Create song directory in logging directory
        song_directory = logging_directory + '/' + file.split('/')[-1].split('.')[0]
        if not os.path.exists(song_directory):
            os.makedirs(song_directory)

        ### TRANSCRIBE THE FILE ###
        print("Beginning: " + file) # Print the song name
        result = transcribe_file(file, model_size=model_size) # Transcribe the file
        # Print first ten words of text
        print('Found text: ', result['text'][:10] + '...')

        ### LOAD THE AUDIO FILE ###
        sound_file = AudioSegment.from_mp3(file) # Load the audio file for segmenting

        ### CHECK FOR AND REMOVE PROHIBITED WORDS ###
        # Loop through the segments
        for id in range(len(result['segments'])):

            # Get the words
            word_set = result['segments'][id]['words']

            # Loop through the words
            for num, word in enumerate(word_set):
                    
                    # Get the word
                    word = word['text'].lower()

                    # Write each word and profanity prediction to a log file
                    profanity_file_name = song_directory + '/profanity_preds.txt'
                    with open(profanity_file_name, 'a') as f:
                        f.write(word + '\t' + str(predict_prob([word])) + '\n')

                    # Check if word matches any of the queries in the list of regex for prohibited words
                    if predict_prob([word]) > 0.98:
                    
                        # Get start time of the word
                        start_time = word_set[num]['start']

                        # Get end time of the word
                        end_time = word_set[num]['end']

                        # Convert time to milliseconds
                        begin = start_time*1000 - 90  # in milliseconds, subtract 90 milliseconds to get the beginning of the word
                        end = end_time*1000  # in milliseconds

                        # Generate silence segment
                        # silence_segment = AudioSegment.silent(duration=end-begin)
                        silence_segment = AudioSegment.reverse(sound_file[begin:end])
                        sound_file = sound_file[:begin] + silence_segment + sound_file[end:]


        ### EXPORT THE CLEAN FILE ###
        # Export the file and move it to the completed directory if it exists
        try:
            # Export the clean file to the main directory
            clean_file = working_directory + '/' + 'clean_' + file.split('/')[-1]
            sound_file.export(clean_file, format="mp3")
            print('\n')
            
            # Move the original audio file to the completed directory
            os.rename(file, completed_directory + '/' + file.split('/')[-1])
        except NameError:
            print("No prohibited words found in " + file + '\n')

        ### LOG THE RESULTS ###
        # Write result to a log file
        with open(logging_directory + '/log.txt', 'a') as f:
            f.write('Song:' + file + '\n')
            f.write('Outcome:' + result['text'] + '\n\n')

        ### MOVE THE ORIGINAL FILE TO A NEW DIRECTORY ###
        with open(song_directory + '/result.json', 'w') as f:
            json.dump(result, f)

# ### PRINT COMPLETION MESSAGE ###
# print("All files have been cleaned.")


if __name__ == "__main__":
    main()
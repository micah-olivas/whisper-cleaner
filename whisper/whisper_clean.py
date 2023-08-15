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

# import text and sound processing libraries
import whisper_timestamped as whisper
from profanity_check import predict_prob
from pydub import AudioSegment
from pydub.silence import split_on_silence


### DEFINE FUNCTIONS ###
# Use the second command line argument as the model size
# If no argument is given, use the default model size
if len(sys.argv) > 2:
    model_size = sys.argv[2]
else:
    model_size = "base"


# Define function to get the files
def get_files(directory):
    # Use first command line argument as the directory to search for whisper files
    # If no argument is given, use the current directory
    if len(sys.argv) > 1:
        directory = sys.argv[1]
        
        # remove quotes and make string
        directory = directory.replace('"', '')
        directory = directory.replace("'", "")
        directory = str(directory)
    else:
        directory = "."

    # Get all mp3 files in the directory
    files = glob.glob(directory + '/*.mp3')
    files.extend(glob.glob(directory + '/*.m4a')) # Add m4a files to the list
    files.extend(glob.glob(directory + '/*.wav')) # Add wav files to the list
    files.extend(glob.glob(directory + '/*.ogg')) # Add ogg files to the list
    files.extend(glob.glob(directory + '/*.flac')) # Add flac files to the list

    # Return the list of files
    return files, directory


# Define function to transcribe the files
def transcribe_file(file, model_size="base"):
    # Get filepath for the file
    # Load the model
    model = whisper.load_model(model_size)
    
    # Load the audio file
    audio = whisper.load_audio(file)

    # Transcribe the audio file
    result = whisper.transcribe(model, audio, language="en")

    # Return the result
    return result


### GET FILES ##
# Get all files
print("Getting mp3 files...")
files, working_directory = get_files("")

### CREATE DIRECTORIES ###
# Create clean songs directory
clean_directory = working_directory + '/clean_songs'
if not os.path.exists(clean_directory):
    os.makedirs(clean_directory)

# Create logging directory
logging_directory = working_directory + '/logging'
if not os.path.exists(logging_directory):
    os.makedirs(logging_directory)

# Create directory for completed songs
completed_directory = working_directory + '/completed'
if not os.path.exists(completed_directory):
    os.makedirs(completed_directory)


### LOOP THROUGH FILES ###
# Loop through the files
for file in files:

    ### CHECK FOR NEW FILES ###
    # check the list of files to see if 
    # any new files have been added
    print("Checking for new files...")
    files, working_directory = get_files("")

    ### TRANSCRIBE THE FILE ###
    print("Beginning: " + file) # Print the song name
    result = transcribe_file(file, model_size=model_size) # Transcribe the file
    print(result['text']) # Print text

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
        
                # Check if word matches any of the queries in the list of regex for prohibited words
                if predict_prob([word]) > 0.95:
                
                    # Get start time of the word
                    start_time = word_set[num]['start']

                    # Get end time of the word
                    end_time = word_set[num]['end']

                    print("Prohibited word found: " + word)

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
         # Export the file
         clean_file = clean_directory + '/' + 'clean_' + file.split('/')[-1]
         sound_file.export(clean_file, format="mp3")
         print('\n')
         
         # Move the file to the completed directory
         os.rename(file, completed_directory + '/' + file.split('/')[-1])
    except NameError:
        print("No prohibited words found in " + file + '\n')

    ### LOG THE RESULTS ###
    # Write result to a log file
    with open(logging_directory + '/log.txt', 'a') as f:
         f.write('Song:' + file + '\n')
         f.write('Outcome:' + result['text'] + '\n\n')

    ### MOVE THE ORIGINAL FILE TO A NEW DIRECTORY ###
    # Create song directory in logging directory
    song_directory = logging_directory + '/' + file.split('/')[-1].split('.')[0]
    if not os.path.exists(song_directory):
         os.makedirs(song_directory)
    with open(song_directory + '/result.json', 'w') as f:
         json.dump(result, f)
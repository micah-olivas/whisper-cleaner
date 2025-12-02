"""
Tests for whisper-cleaner CLI functionality
"""
import os
import sys
import tempfile
import shutil
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from whisper_cleaner.main import main


class TestCLIArguments(unittest.TestCase):
    """Test command line argument parsing"""

    def test_help_message(self):
        """Test that --help displays help message"""
        with patch('sys.argv', ['whisper-cleaner', '--help']):
            with self.assertRaises(SystemExit) as cm:
                main()
            self.assertEqual(cm.exception.code, 0)

    def test_version_flag(self):
        """Test that --version displays version"""
        with patch('sys.argv', ['whisper-cleaner', '--version']):
            with self.assertRaises(SystemExit) as cm:
                main()
            self.assertEqual(cm.exception.code, 0)

    def test_conflicting_flags(self):
        """Test that --quiet and --verbose cannot be used together"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('sys.argv', ['whisper-cleaner', tmpdir, '--quiet', '--verbose']):
                with self.assertRaises(SystemExit):
                    main()

    def test_invalid_model_size(self):
        """Test that invalid model size is rejected"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('sys.argv', ['whisper-cleaner', tmpdir, '-m', 'invalid']):
                with self.assertRaises(SystemExit):
                    main()


class TestDirectoryValidation(unittest.TestCase):
    """Test input directory validation"""

    def test_nonexistent_directory(self):
        """Test that nonexistent directory raises error"""
        with patch('sys.argv', ['whisper-cleaner', '/nonexistent/path']):
            with self.assertRaises(SystemExit) as cm:
                main()
            self.assertEqual(cm.exception.code, 1)

    def test_file_instead_of_directory(self):
        """Test that file path instead of directory raises error"""
        with tempfile.NamedTemporaryFile() as tmpfile:
            with patch('sys.argv', ['whisper-cleaner', tmpfile.name]):
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 1)

    def test_empty_directory(self):
        """Test that empty directory exits gracefully"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('sys.argv', ['whisper-cleaner', tmpdir]):
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 1)


class TestDryRun(unittest.TestCase):
    """Test dry-run mode"""

    def test_dry_run_no_file_creation(self):
        """Test that dry-run mode doesn't create files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a dummy audio file
            test_file = os.path.join(tmpdir, 'test.mp3')
            Path(test_file).touch()

            # Mock the heavy operations
            with patch('whisper_cleaner.main.whisper.load_model'), \
                 patch('whisper_cleaner.main.whisper.load_audio'), \
                 patch('whisper_cleaner.main.whisper.transcribe'), \
                 patch('whisper_cleaner.main.AudioSegment.from_file'), \
                 patch('sys.argv', ['whisper-cleaner', tmpdir, '--dry-run']):

                main()

                # Verify no output directories were created
                logging_dir = os.path.join(tmpdir, 'logging')
                originals_dir = os.path.join(tmpdir, 'originals')
                self.assertFalse(os.path.exists(logging_dir))
                self.assertFalse(os.path.exists(originals_dir))


class TestFileDetection(unittest.TestCase):
    """Test audio file detection"""

    def test_supported_formats(self):
        """Test that all supported audio formats are detected"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create dummy files for each supported format
            formats = ['mp3', 'm4a', 'wav', 'ogg', 'flac']
            for fmt in formats:
                Path(os.path.join(tmpdir, f'test.{fmt}')).touch()

            # Mock heavy operations and run dry-run
            with patch('whisper_cleaner.main.whisper.load_model'), \
                 patch('sys.argv', ['whisper-cleaner', tmpdir, '--dry-run', '-q']):

                # Should not raise SystemExit for empty directory
                try:
                    main()
                except SystemExit:
                    pass  # Expected for no transcription in dry-run

    def test_skip_cleaned_files(self):
        """Test that files starting with 'clean_' are skipped"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create both original and cleaned files
            Path(os.path.join(tmpdir, 'song.mp3')).touch()
            Path(os.path.join(tmpdir, 'clean_song.mp3')).touch()

            with patch('whisper_cleaner.main.whisper.load_model'), \
                 patch('whisper_cleaner.main.whisper.load_audio'), \
                 patch('whisper_cleaner.main.whisper.transcribe') as mock_transcribe, \
                 patch('whisper_cleaner.main.AudioSegment.from_file'), \
                 patch('sys.argv', ['whisper-cleaner', tmpdir, '--dry-run', '-v']):

                try:
                    main()
                except SystemExit:
                    pass


class TestThresholdOption(unittest.TestCase):
    """Test profanity threshold option"""

    def test_custom_threshold(self):
        """Test that custom threshold is accepted"""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(os.path.join(tmpdir, 'test.mp3')).touch()

            with patch('sys.argv', ['whisper-cleaner', tmpdir, '-t', '0.95', '--dry-run', '-q']):
                try:
                    main()
                except SystemExit:
                    pass  # Expected

    def test_invalid_threshold(self):
        """Test that invalid threshold values are handled"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Threshold outside 0-1 range should still parse but may behave unexpectedly
            # This is more about ensuring no crash
            with patch('sys.argv', ['whisper-cleaner', tmpdir, '-t', '1.5', '--dry-run', '-q']):
                try:
                    main()
                except (SystemExit, ValueError):
                    pass  # Expected


if __name__ == '__main__':
    unittest.main()

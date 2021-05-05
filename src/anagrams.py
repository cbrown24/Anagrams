from dataclasses import dataclass, field
from typing import Dict, List, Optional
import gzip
import unittest
from contextlib import contextmanager

@contextmanager
def read_file(words_file_path: str):
    try:
        with gzip.open(words_file_path, 'r') as file:
            yield file.readlines()
    except gzip.BadGzipFile:
        try:
            with open(words_file_path, 'r') as file:
                yield file.readlines()
        except UnicodeDecodeError:
            raise RuntimeError(f'Unsupported file {words_file_path}')
    finally:
        file.close()

@dataclass()
class Anagrams:
    words_file_path: str
    anagrams: Dict = field(default_factory=dict)
    def __post_init__(self):
        """ Save a hashed subject and its anagrams.
            Written as per below definition of the word Anagram.
            'An anagram is a word or phrase formed by rearranging
            the letters of a different word or phrase,
            using all the original letters exactly once.'

            Assumes that word_file_path is newline delimited.

            Does not yet handle comma delimited.

            Supports gzip and plain text
        """
        with read_file(self.words_file_path) as words:
            for word in words:
                try:
                    enc = 'utf-8'
                    word = str(word, enc)
                except TypeError:
                    pass
                self.store_anagram(word)

    def store_anagram(self, word:str) -> None:
        word = word.replace('\n', '')
        self.anagrams.setdefault(self.anagram_hash(word), []).append(word)

    def anagram_hash(self, word:str) -> str:
        """ :returns input string sorted and stripped
        """
        word = word.replace(' ', '').lower()
        return ''.join(sorted(list(word)))

    def get_anagrams(self, word:str) -> Optional[List[str]]:
        """ :returns the stored anagrams of <word>.
        """
        return self.anagrams.get(self.anagram_hash(word))


class TestAnagrams(unittest.TestCase):

    def test_anagrams(self):
        anagrams = Anagrams('words.txt')
        self.assertEqual(
            anagrams.get_anagrams('dictionary'),
            ['dictionary', 'indicatory']
        )
        # test for spaces in word
        self.assertEqual(
            anagrams.get_anagrams('tea spoon'),
            ['tea spoon', 'teaspoon']
        )

        # test for mixed case words
        self.assertEqual(
            anagrams.get_anagrams('foobaR'),
            ['FooBar', 'foobar']
        )

        # test with hyphens
        self.assertEqual(
            anagrams.get_anagrams('randa--'),
            ['A-and-R']
        )

    def test_gzipped_file(self):
        """ test gzipped file """
        anagrams = Anagrams('words.txt.gz')
        self.assertEqual(
            anagrams.get_anagrams('dictionary'),
            ['dictionary', 'indicatory']
        )

    def test_bad_file_format_raises_error(self):
        """ test bzipped file generates the right error """
        try:
            Anagrams('words.txt.bz2')
        except RuntimeError as e:
            self.assertEqual(str(e), 'Unsupported file words.txt.bz2')

    def test_no_match_returns_none(self):
        anagrams = Anagrams('words.txt')
        self.assertEqual(
            anagrams.get_anagrams('fizzbang'),
            None
        )

if __name__ == '__main__':
    unittest.main()
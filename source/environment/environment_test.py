# pylint: disable=no-member
import unittest
import os

from environment import Environment

class Environment_test(unittest.TestCase):
    
    INI_FILE = 'library.ini'
    KILL_DEF = 'KillCommand'
    VIDEO_DEF = 'VideoList'
    UUID_DEF = 'UuidTable'
    USB_DEF = 'usb'

    def test_the_environment_loads_the_default_directory_file(self):
        self.makeEnvironment(["blarg=burp\n","beep=boop"])
        environment = Environment(self.TEST_FILE)
        self.assertEqual(environment.blarg, "burp")
        self.assertEqual(environment.beep, "boop")
    
    def test_the_environment_is_not_affect_by_extra_new_lines(self):
        self.makeEnvironment(["blarg=burp\n","beep=boop\n","\n"])
        environment = Environment(self.TEST_FILE)
        self.assertEqual(environment.blarg, "burp")
        self.assertEqual(environment.beep, "boop")
    
    def test_the_environment_loads_defaults_when_no_file_exists(self):
        environment = Environment(self.TEST_FILE)
        self.assertEqual(environment.KillCommand, "-255")

    def test_the_environment_restores_the_file_when_no_file_exists(self):
        Environment(self.TEST_FILE)
        f = open('.testEnv', 'r')
        f.close()

    def test_the_environment_rewrites_the_current_settings_back_to_the_file(self):
        environment = Environment(self.TEST_FILE)
        environment.KillCommand = "-233"
        environment.update(self.TEST_FILE)
        environment = Environment(self.TEST_FILE)
        self.assertEqual(environment.KillCommand, "-233")

    TEST_FILE = ".testEnv"

    def makeEnvironment(self, lines):
        f = open(self.TEST_FILE, "w+")
        f.writelines(lines)
        f.close()

    def tearDown(self):
        os.remove(self.TEST_FILE)

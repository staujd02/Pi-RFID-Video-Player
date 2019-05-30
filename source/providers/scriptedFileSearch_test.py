import unittest
import os

from scriptedFileSearch import ScriptedFileSearch 

class ScriptProvider_test(unittest.TestCase):

    class ProcessProvider(object):
        scriptCalledWith = None

        def call(self, cmd, shell=False):
            self.scriptCalledWith = cmd

    def test_Scan_exists(self):
        x = ScriptedFileSearch(self.ProcessProvider())
        self.assertNotEqual(None, x)

    def test_Scan_does_not_run_by_default(self):
        s = ScriptedFileSearch(self.ProcessProvider())
        self.assertEqual(None, next(s.getList(), None))
        self.assertEqual(False, s.scanHasRun())

    def test_scanner_can_scan(self):
        s = ScriptedFileSearch(self.ProcessProvider())
        s.scan("MyScript.sh")
        self.assertEqual(True, s.scanHasRun())

    def test_scanner_calls_my_subprocess_provider_with_my_script(self):
        provider = self.ProcessProvider()
        s = ScriptedFileSearch(provider)
        s.scan("MyScript.sh")
        self.assertEqual("../MyScript.sh > temp.list",
                         provider.scriptCalledWith)

    def test_scanner_script_can_find_videos(self):
        s = ScriptedFileSearch(self.ProcessProvider())
        s.scan("MyScript.sh")
        self.assertEqual(["Cheeta Queen", "./some_dir/Cheeta Queen.mp4"], s.getFile("1"))
        self.assertEqual("1", next(s.getList()))

    def test_class_removes_temp_file_after_running(self):
        s = ScriptedFileSearch(self.ProcessProvider())
        s.scan("MyScript.sh")
        self.assertEqual(False, os.path.isfile("temp.list"))

    def setUp(self):
        self.createTempFile()
    
    def createTempFile(self):
        f = open("temp.list", "w")
        f.write("1,Cheeta Queen,./some_dir/Cheeta Queen.mp4")
        f.close()

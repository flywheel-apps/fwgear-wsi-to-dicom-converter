import sys
import os
import run
import logging
import tempfile
from pathlib import Path
import pytest

log = logging.getLogger()

def test_run_passes():
    assert run.run(log, ['echo','yes']) == 0
    
def test_run_fails():
    assert run.run(log, ['ls', 'nonexistantdirectory']) != 0

def test_run_errors():
    assert run.run(log, ['exit']) == 6

class TestCleanup:
    
    work_dir = tempfile.TemporaryDirectory()
    output_dir = tempfile.TemporaryDirectory()

    work_path = Path(work_dir.name)
    output_path = Path(output_dir.name)
    
    num_files = 5
    files = []
    for i in range(num_files):
        f = open(work_path/f"{i}.dcm",'w')
        f.close()
        files.append(work_path/f"{i}.dcm")
        #files.append(Path(tempfile.NamedTemporaryFile(dir=work_path, suffix='.dcm').name))
    
    run.cleanup(log, work_path, output_path)
    
    
    def test_cleanup_removes_files(self):

        src_files = os.listdir(self.work_path)
        n_files = 0
        for file_name in src_files:
            full_file_name = os.path.join(self.work_path, file_name)
            if os.path.isfile(full_file_name):
                n_files += 1
        
        assert n_files == 0
    
    def test_cleanup_moved_files(self):

        src_files = os.listdir(self.output_path)
        n_files = 0
        for file_name in src_files:
            full_file_name = os.path.join(self.output_path, file_name)
            if os.path.isfile(full_file_name):
                n_files += 1

        assert n_files == self.num_files
    
    
    def test_cleanup_failonzero(self):
        with pytest.raises(Exception) as excinfo:
            run.cleanup(log, self.work_path, self.output_path)
        assert "No output Files Generated" in str(excinfo.value)


        


            
            
            
    
    
    


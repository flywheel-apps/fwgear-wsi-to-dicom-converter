#!/usr/bin/env python3

import os
from pathlib import Path
import subprocess as sp
import sys

import flywheel_gear_toolkit
from flywheel_gear_toolkit.utils import file
from flywheel_gear_toolkit.utils import zip_tools


def fail_check(context):
    
    input_path = context.get_input_path("Input_file")
    expected_extension = ".svs"
    
    try:
        passes = file.is_valid(input_path, expected_extension)
    except FileNotFoundError as e:
        context.log.exception(e)
        raise(e)
    except TypeError as e:
        context.log.exception(e)
        raise(e)
    except Exception as e:
        context.log.warning(f'Problem with {input_path}')
        context.log.exception(e)
        raise(e)
    
    return(passes)
        

def setup(context):
    
    input_keys = context.config.keys()
    
    # Create the head of the command
    command = ['wsi2dcm',
               '--input', context.get_input_path("Input_file"),
    ]
    
    # If present add the other input (the dicom json file)
    if context.get_input('jsonFile'):
        command.extend(['--jsonFile', context.get_input_path("jsonFile")])
    
    # Append any specified config options
    for key in input_keys:
        if context.config.get(key):
            command.extend([f"--{key}", context.config[key]])
    
    # Give the series description some name if not specified
    if 'seriesDescription' not in input_keys:

        series_description = Path(context.get_input_path("Input_file")).stem
        
        command.extend(['--seriesDescription', series_description])
    else:
        series_description = context.config.get('seriesDescription')
    
    output_dir = context.work_dir/Path(series_description)
    
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
        
    command.extend(['--outFolder', output_dir])
    # Stringify all PATHS in the command for logging stuff.
    command = [str(c) for c in command]
    
    context.log.info("Command to call: \n" + " ".join(command))
    
    return(command, series_description)



def run(command):
    
    pr = sp.Popen(command, shell=False)
    pr.wait()
    rc = pr.returncode
    if rc != 0:
        context.log.warning("WIS did not return 0, but the return code is unreliable. \n"
                          "The output folder will be checked for processed files")
    return(rc)

def cleanup(context, output_dir):
    # Changed from analysis to converter
    # zipped_output = context.output_dir/Path(f'{output_dir}.zip')
    # zip_tools.zip_output(context.work_dir, zipped_output)
    
    dicom_directory = context.work_dir/output_dir
    
    src_files = os.listdir(dicom_directory)
    
    if len(src_files) == 0:
        context.log.error('No files generated.  Assuming error')
        raise Exception('No output Files Generated')
    
    else:
        context.log.info(f'{len(src_files)} successfully created')
    
    for file_name in src_files:
        full_file_name = os.path.join(dicom_directory, file_name)
        if os.path.isfile(full_file_name):
            dest = context.output_dir/Path(file_name)
            os.rename(full_file_name, dest)
            


if __name__ == '__main__':
    # Set return code to zero optimistically
    rc = 0
    with flywheel_gear_toolkit.GearToolkitContext() as context:
        try:
            context.init_logging()
            context.log_config()
            
            valid = fail_check(context)
            context.log.info(f'Input file is valid:   {valid}')
            
            command, series_description = setup(context)
            
            rc = run(command)
            # return code currently unreliable
            context.log.info(f'Exit Code: {rc}')
            
            cleanup(context, series_description)
            
        except Exception as e:
            context.log.error('Error running gear')
            context.log.exception(e)
            sys.exit(1)
        
    
    sys.exit(0)



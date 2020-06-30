#!/usr/bin/env python3

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
        input = context.get_input('Input_file')
        print(input)

        series_description = Path(context.get_input_path("Input_file")).stem
        
        command.extend(['--seriesDescription', series_description])
    else:
        series_description = context.config.get('seriesDescription')
    
    output_dir = context.work_dir/Path(series_description)
    command.extend('--outFolder', output_dir)
    
    context.log.info("Command to call: \n" + " ".join(command))
    
    return(command, series_description)



def run(command):
    
    pr = sp.Popen(command, shell=False)
    pr.wait()
    rc = pr.returncode
    
    if rc != 0:
        context.log.error('Error running WIS')
    return(rc)

def cleanup(context, output_dir):
    
    zipped_output = context.output_dir/Path(f'{output_dir}.zip')
    zip_tools.zip_output(context.work_dir, zipped_output)
    


if __name__ == '__main__':
    # Set return code to zero optimistically
    rc = 0
    with flywheel_gear_toolkit.GearToolkitContext() as context:
        
        context.init_logging()
        context.log_config()
        
        valid = fail_check(context)
        context.log.info(f'Input file is valid:   {valid}')
        
        command, series_description = setup(context)
        
        rc = run(command)
        
        cleanup(context, series_description)
        
        sys.exit(rc)



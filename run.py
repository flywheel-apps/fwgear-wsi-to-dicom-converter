#!/usr/bin/env python3

import logging
import os
import re
import subprocess as sp
import sys
from pathlib import Path

import flywheel_gear_toolkit
from flywheel_gear_toolkit.utils import file, zip_tools
from pathvalidate import sanitize_filepath


def create_sanitized_filepath(filepath):
    """
    Return symlink to filepath without illegal characters.

    Illegal characters are not alphanumeric, '.', '_', or '-'.

    Args:
        filepath (Path-Like): Filepath with potential invalid characters

    Returns:
        str: Path to create symbolic link to original file.
    """
    try:
        log
    except NameError:
        log = logging.getLogger(__name__)
    filepath = re.sub(r"(t2 ?_?)\*", r"\1star", str(filepath), flags=re.IGNORECASE)
    sanitized_filepath = sanitize_filepath(filepath, platform="auto").replace(" ", "_")
    if filepath != sanitized_filepath:
        log.info("Linking %s to %s.", filepath, sanitized_filepath)
        os.symlink(filepath, sanitized_filepath)

    return sanitized_filepath


def fail_check(context):

    input_path = context.get_input_path("Input_file")
    expected_extension = ".svs"

    try:
        passes = file.is_valid(input_path)  # , expected_extension)
    except FileNotFoundError as e:
        context.log.exception(e)
        raise e
    except TypeError as e:
        context.log.exception(e)
        raise e
    except Exception as e:
        context.log.warning(f"Problem with {input_path}")
        context.log.exception(e)
        raise e

    return passes


def setup(context):

    input_keys = context.config.keys()

    # Create the head of the command
    command = [
        "wsi2dcm",
        "--input",
        create_sanitized_filepath(context.get_input_path("Input_file")),
    ]

    # If present add the other input (the dicom json file)
    if context.get_input("jsonFile"):
        command.extend(
            [
                "--jsonFile",
                create_sanitized_filepath(context.get_input_path("jsonFile")),
            ]
        )

    # Append any specified config options
    for key in input_keys:
        if context.config.get(key):
            command.extend([f"--{key}", context.config[key]])

    # Give the series description some name if not specified
    if "seriesDescription" not in input_keys:

        series_description = Path(context.get_input_path("Input_file")).stem

        command.extend(["--seriesDescription", series_description])
    else:
        series_description = context.config.get("seriesDescription")

    output_dir = context.work_dir / Path(
        sanitize_filepath(series_description, platform="auto").replace(" ", "_")
    )

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    command.extend(["--outFolder", output_dir])
    # Stringify all PATHS in the command for logging stuff.
    command = [str(c) for c in command]

    context.log.info("Command to call: \n" + " ".join(command))

    return command, series_description, output_dir


def run(log, command):

    try:
        pr = sp.Popen(command, shell=False)
        pr.wait()
        rc = pr.returncode
    except Exception as e:
        log.error(f"Command {command} failed")
        log.exception(e)
        rc = 6

    if rc != 0:
        log.warning(
            "WIS did not return 0, but the return code is unreliable. \n"
            "The output folder will be checked for processed files"
        )
    return rc


def cleanup(log, dicom_directory, output_dir):
    # Changed from analysis to converter
    # zipped_output = context.output_dir/Path(f'{output_dir}.zip')
    # zip_tools.zip_output(context.work_dir, zipped_output)

    src_files = os.listdir(dicom_directory)

    if len(src_files) == 0:
        log.error("No files generated.  Assuming error")
        raise Exception("No output Files Generated")

    else:
        log.info(f"{len(src_files)} successfully created")

    # This prevents the script from coppying in subdirectories to the output.  I don't
    # Think this particular gear does that anyway, though.
    for file_name in src_files:
        full_file_name = os.path.join(dicom_directory, file_name)
        if os.path.isfile(full_file_name):
            dest = output_dir / Path(file_name)
            os.rename(full_file_name, dest)


if __name__ == "__main__":
    # Set return code to zero optimistically
    rc = 0
    with flywheel_gear_toolkit.GearToolkitContext() as context:
        try:
            context.init_logging()
            context.log_config()

            valid = fail_check(context)
            context.log.info(f"Input file is valid:   {valid}")

            command, series_description, output_folder = setup(context)

            rc = run(context.log, command)
            # return code currently unreliable
            context.log.info(f"Exit Code: {rc}")

            cleanup(context.log, output_folder, context.output_dir)

        except Exception as e:
            context.log.error("Error running gear")
            context.log.exception(e)
            sys.exit(1)

    sys.exit(0)


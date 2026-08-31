#!/usr/bin/env python3

import os
import sys
from pathlib import Path
import csv
import datetime
import argparse
import shutil

# sys.argv = [
#    '/Users/nraogra/Desktop/webvtt_v2/copy_and_rename.py',
#    '/Users/nraogra/Desktop/webvtt_v2/metadata_updated',
#    '-c',
#    '/Users/nraogra/Desktop/webvtt_v2/webvtt_metadata.csv',
#    '-o',
#    ]

def valid_directory(path_string):
    if not os.path.isdir(path_string):
        raise argparse.ArgumentTypeError(f"'{path_string}' is not a valid directory.")
    return path_string

def valid_csv(path_csv):
    if not path_csv.endswith(".csv"):
        raise argparse.ArgumentTypeError(f"'{path_csv}' is not a valid csv file.")
    else:
        return path_csv
    
def setup(args_):
    parser = argparse.ArgumentParser()
    parser.add_argument("source_dir", type=valid_directory, help="Directory of source files")
    parser.add_argument("-c", "--csv", type=valid_csv, help="Metadata CSV")
    parser.add_argument("-o", "--overwrite", action="store_true", help="overwrite repeatable element values instead of appending")
    args = parser.parse_args(args_)
    return args

def ask_yes_no(question):
    '''
    Returns Y or N. The question variable is just a string.
    '''
    answer = ''
    print(' - \n', question, '\n', 'enter Y or N')
    while answer not in ('Y', 'y', 'N', 'n'):
        answer = input()
        if answer not in ('Y', 'y', 'N', 'n'):
            print(' - Incorrect input. Please enter Y or N')
        if answer in ('Y', 'y'):
            return 'Y'
        elif answer in ('N,' 'n'):
            return 'N'

def make_output_dir(source_dir):
    outputDir = os.path.join(source_dir, 'renamed_files')
    print("checking for output folder...")
    if not os.path.exists(outputDir):
        os.mkdir(outputDir)
        print(f'\toutput folder created: \n\t{outputDir}')
    else:
        print(f'\toutput folder already exists: \n\t{outputDir}')
    return outputDir

def find_file(outputName, m_csv):
    with open(m_csv, 'r', encoding='UTF-8-sig') as mFile:
        mReader = csv.reader(mFile)
        match = False
        for row_num, row in enumerate(mReader):
            if row[0] == outputName:
                match = True
                if row[1] == '':
                    new_val = 'empty'
                else:
                    new_val = row[1]
                return new_val
        if not match:
            new_val = 'nomatch'
            return new_val

def generate_log(log, what2log):
    if not os.path.isfile(log):
        with open(log, "w", encoding='utf-8') as f:
            f.write(what2log + '\n')
    else:
        with open(log, "a", encoding='utf-8') as f:
            f.write(what2log + '\n')

def make_log(files_renamed, skips, outputDir):
    timenow = datetime.datetime.now()
    logname = f'File_rename_log_{timenow.strftime("%y-%m-%d_%Hh%Mm%Ss")}.txt'
    log_source = os.path.join(outputDir, logname)
    generate_log(log_source, 'file rename log for ' + outputDir + '\n')
    if skips:
        generate_log(log_source, 'Files skipped:')
        for item in skips:
            generate_log(log_source, item)
    if skips and files_renamed:
        generate_log(log_source, '')
    if files_renamed:
        generate_log(log_source, 'Files copied and renamed:')
        for item in files_renamed:
            generate_log(log_source, item)
    generate_log(log_source, '\nFinished running at ' + timenow.strftime("%Y-%m-%d %H:%M:%S%p") + '\n')

def copy_and_rename(file_list, outputDir, overwrite):
    files_renamed = []
    files_skipped_2 = []
    os.chdir(outputDir)
    for file, value in file_list:
        fileName = os.path.basename(file)
        justName = Path(file).stem
        fileExt = Path(file).suffix
        newname = justName + '_' + value + fileExt
        source_path = file
        dest_path = os.path.join(outputDir, newname)
        if os.path.exists(dest_path) and not overwrite:
            print(f'{fileName}: {newname} already exists in {outputDir}, skipping')
            files_skipped_2.append(f'{fileName}: {newname} already exists in {outputDir}')
            continue
        else:
            try:
                shutil.copy2(source_path, dest_path)
                files_renamed.append(f'{fileName}: copied as {newname}')
            except shutil.Error as e:
                print(f'{fileName}: could not copy due to error: "{e}"')
                files_skipped_2.append(f'{fileName}: could not copy due to error: "{e}"')
                continue
    return files_renamed, files_skipped_2

def rename_setup(source_dir, m_csv, outputDir, overwrite):
    file_list = []
    files_skipped_1 = []
    for sourcefile in Path(source_dir).rglob('*'):
        if not sourcefile.is_file():
            continue
        else:
            justName = Path(sourcefile).stem
            fileExt = Path(sourcefile).suffix
            outputName = justName + fileExt
            new_val = find_file(outputName, m_csv)
            if new_val == 'nomatch':
                print(f'{outputName}: not found in csv, skipping file')
                files_skipped_1.append(f'{outputName}: not found in csv')
                continue
            elif new_val == 'empty':
                print(f'{outputName}: no new name in csv, skipping file')
                files_skipped_1.append(f'{outputName}: no new name in csv')
                continue
            else:
                print(f'{outputName}: will be renamed to {new_val}{fileExt}')
                file_list.append((sourcefile, new_val))
    files_renamed, files_skipped_2 = copy_and_rename(file_list, outputDir, overwrite)
    skips = files_skipped_1 + files_skipped_2
    return files_renamed, skips

def main(args_):
    args = setup(args_)
    source_dir = args.source_dir
    overwrite = args.overwrite
    print('*** file rename - settings chosen: ***')
    print(f'source file directory:\n\t{source_dir}')
    if args.csv != None:
        m_csv = args.csv
        print(f'rename csv (new file names must be in column B):\n\t{m_csv}')
    else:
        sys.exit('error: csv is needed to rename files')
    if overwrite == True:
        print('matching-name files in the output directory will be overwritten')
    else:
        print('matching-name files in the output directory will be skipped')
    proceed = ask_yes_no('proceed with these settings?')
    if proceed =='Y':
        outputDir = make_output_dir(source_dir)
        files_renamed, skips = rename_setup(source_dir, m_csv, outputDir, overwrite)
        make_log(files_renamed, skips, outputDir)
    else:
        print('exiting. goodbye!')
        sys.exit()

if __name__ == '__main__':
    main(sys.argv[1:])
#!/usr/bin/env python3

import os
import sys
import glob
import subprocess
import csv
import argparse
from pathlib import Path
import shutil
import pandas as pd


sys.argv = [
    'prepforlibav.py',
    '/Users/nraogra/Downloads/Carlos/',
    '/Users/nraogra/Desktop/Carlos',
    '/Users/nraogra/Desktop/Carlos/Object_CSV_C_2025_12_10.csv', 
    '-s'
    ]

def setup(args_):
    parser = argparse.ArgumentParser(
        description='test description')
    parser.add_argument(
        'source', help='Source directory'
    )
    parser.add_argument(
        'destination',
        help='Staging directory'
    )
    parser.add_argument(
        'csv_location',
        help='csv directory'
    )
    parser.add_argument(
        '-s',
        '--skipcopy',
        action='store_true',
        help='skips the copy to staging directory step'
    )
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

def copy_to_stage(source, destination):
    #copy source files to staging drive
    if not os.path.isdir(destination):
        print(f"no directory {destination} exists, making directory")
        os.makedirs(destination)
    else:
        pass
    sourceContents = source + '/'
    cmd_dryrun = [
        'rsync', '--dry-run',
        '-ah', '-vv',
        '--exclude=.*', '--exclude=.*/',
        '--progress', '--stats',
        sourceContents, destination
    ]
    print(f"dry run of copy to stage command: {cmd_dryrun}")
    subprocess.call(cmd_dryrun)
    
    run_copy = ask_yes_no('continue with copy to staging drive?')
    
    if run_copy == 'Y':
        cmd_copy = [
            'rsync', 
            '-ah', '-vv',
            '--exclude=.*', '--exclude=.*/',
            '--progress', '--stats',
            sourceContents, destination
        ]
        print(cmd_copy)
        subprocess.call(cmd_copy)
    else:
        skip = ask_yes_no('skip copy and continue prep for lib-av?')
        if skip == 'Y':
            pass
        else:
            sys.exit()
            
def checksum_match(source, destination):
    sourceContents = source + '/'
    cmd_checkmatch = [
        'rsync',
        '--dry-run',
        '--checksum',
        '-ah', '-vv',
        '--progress',
        sourceContents, destination
    ]
    print(cmd_checkmatch)
    subprocess.call(cmd_checkmatch)
    
def move_to_root(maindir):
    os.chdir(maindir)      
    subdirs = os.listdir(maindir)
    subs=[]
    for dir in subdirs:
        if os.path.isdir(dir) == True:
            subdir_path = os.path.join(maindir,dir)
            subs.append(subdir_path)
    if not subs:
        print('no subdirectories, moving to next step.')
        return
    else:
        print('subdirectories found:')
        for subdir in subs:
            print('\t' + subdir)
        move_yn = ask_yes_no('move all files to main directory?')
        if move_yn == 'Y':
            orig_full=[]
            new_full=[]
            for subdir in subs:
                print('moving for %s' % subdir)
                for root, dirs, files in os.walk(subdir):
                    for file in files:
                        full = os.path.join(root, file)
                        abs_full = os.path.abspath(full)
                        str_dir = abs_full.replace(maindir, '')
                        str_dir = str_dir.replace('\\', '', 1)
                        str_dir = str_dir.replace('/', '', 1)
                        str_dir = str_dir.replace('\\', '_')
                        str_dir = str_dir.replace('/', '_')
                        str_dir = str_dir.replace(', ', '_')
                        str_dir = str_dir.replace(',', '_')
                        str_dir = str_dir.replace(' ', '_')
                        new_file_path = os.path.join(maindir, str_dir)
                        orig_full.append(full)
                        new_full.append(new_file_path)
                        print('\t' + full + '\n\t' + new_file_path)
                print('---')
            proceed = ask_yes_no('proceed?')
            if proceed == 'Y':
                for item1, item2 in zip(orig_full, new_full):
                    shutil.move(item1, item2)
            else:
                print('skipping file move.')
                return
        else:
            print('skipping file move.')
            return

def get_video_files(destination):
    video_list = []
    if os.path.isdir(destination):
        folder_list = os.listdir(destination)
        for filename in folder_list:
            if not filename[0] == '.':
                if filename.lower().endswith(('.MOV', '.mov', 'MP4', '.mp4', '.mkv', '.MXF', '.mxf', '.dv', '.DV', '.MTS', '.swf', '.avi', '.m2t')):
                    video_list.append(os.path.join(destination, filename))
    elif os.path.isfile(destination):
        video_list = [destination]
    return video_list

def get_audio_files(destination):
    audio_list = []
    if os.path.isdir(destination):
        folder_list = os.listdir(destination)
        for filename in folder_list:
            if not filename[0] == '.':
                if filename.lower().endswith(('.WAV', '.wav', '.aiff', '.AIFF', '.mp3', '.MP3')):
                    audio_list.append(os.path.join(destination, filename))
    elif os.path.isfile(destination):
        audio_list = [destination]
    return audio_list
        
def get_checksum_files(destination):
    checksum_list = []
    if os.path.isdir(destination):
        folder_list = os.listdir(destination)
        for filename in folder_list:
            if not filename[0] == '.':
                if filename.lower().endswith(('.MD5', '.md5', '.SHA1', '.sha1', '.TXT', '.txt')):
                    checksum_list.append(os.path.join(destination, filename))
    elif os.path.isfile(destination):
        checksum_list = [destination]
    return checksum_list

def get_mediainfo(video_list, audio_list, checksum_list, csv_file):
    # write mediainfo output to csv
    if not os.path.exists(csv_file):
        print(f"no file {csv_file} exists, making file")
    else:
        pass
    print(csv_file)
    with open(csv_file, 'a', encoding='utf-8', newline='') as f:
        writer=csv.writer(f)
        for file in video_list:
            cmd_video = [
                'mediainfo',
                '--Output=General;fileset,Video,Primary Content,%FileNameExtension%,\nVideo;%Duration/String4%,%DisplayAspectRatio/String% DAR %FrameRate% FPS,%Format% %Width%x%Height/String% \nAudio;%Format% %SamplingRate/String% %BitDepth/String%',
                file]
            try:
                csv_video = subprocess.check_output(cmd_video).decode(sys.stdout.encoding)
            except subprocess.CalledProcessError as e:
                print(f"Command failed with error code {e.returncode}")
            print(csv_video)
            split_video = csv_video.split(',')
            writer.writerow(split_video)
            
        for file in audio_list:
            cmd_audio = [
                'mediainfo', 
                '--Output=General;fileset,Audio,Primary Content,%FileNameExtension%,\nAudio;%Duration/String3%,,%Format% %SamplingRate/String% %BitDepth/String%', 
                file]
            try:
                csv_audio = subprocess.check_output(cmd_audio).decode(sys.stdout.encoding)
            except subprocess.CalledProcessError as e:
                print(f"Command failed with error code {e.returncode}")
            print(csv_audio)
            split_audio = csv_audio.split(',')
            writer.writerow(split_audio)
            
        for file in checksum_list:
            cmd_checksum = [
                'mediainfo', 
                '--Output=General;fileset,checksum files,Content Validation,%FileNameExtension%',
                file]
            try:
                csv_checksum = subprocess.check_output(cmd_checksum).decode(sys.stdout.encoding)
            except subprocess.CalledProcessError as e:
                print(f"Command failed with error code {e.returncode}")
            print(csv_checksum)
            split_checksum = csv_checksum.split(',')
            writer.writerow(split_checksum)
        f.close()

def get_prepend():
    while True:
        header = input('\n\n**** enter string to be prepended to filenames or type skip to skip this step\n\n').lower()
        
        if header == 'skip':
            skip_yn = ask_yes_no('skip this step?')
            if skip_yn == 'Y':
                print('skipping')
                return header
            else:
                print('try again')
        if header != '' and header != 'skip':
            skip_yn = 'N'
            proceed_yn = ask_yes_no(f'you entered: "{header}"\n is this entered correctly?')
            if proceed_yn == 'Y':
                break
            else:
                print('try again')
        elif header == '':
            print('try again or enter skip')
    if skip_yn == 'Y':
        return
    else:
        return header
    
def write_prepend(header, destination, video_list, audio_list, checksum_list):
    os.chdir(destination)
    all_files = video_list + audio_list + checksum_list
    print('building file list...')
    for file in all_files:
        justName = Path(file).stem
        extension = Path(file).suffix
        prepended_name = header + '_' + justName + extension
        print(f'{justName}{extension} to {prepended_name}')
        
    proceed_yn = ask_yes_no('proceed with renaming?')
    if proceed_yn == 'Y':
        for file in all_files:
            justName = Path(file).stem
            extension = Path(file).suffix
            prepended_name = header + '_' + justName + extension
            print(prepended_name)
            os.rename(file, prepended_name)
    else:
        print('exiting')

def get_middle():
    while True:
        middle_orig = input('\n\n**** enter string to be replaced in filenames or type skip to skip this step\n\n').lower()
        
        if middle_orig == 'skip':
            skip_yn = ask_yes_no('skip this step?')
            if skip_yn == 'Y':
                middle_new = "zip"
                print('skipping')
                return middle_orig, middle_new
            else:
                print('try again')
        if middle_orig != '' and middle_orig != 'skip':
            skip_yn = 'N'
            middle_new = input('\n\n**** enter replacement string\n\n')
            proceed_yn = ask_yes_no(f'replace "{middle_orig}" with "{middle_new}"\n is this entered correctly?')
            if proceed_yn == 'Y':
                break
            else:
                print('try again')
        elif middle_orig == '':
            print('try again or enter skip')
    if skip_yn == 'Y':
        middle_orig == 'skip'
        middle_new = "zip"
        return
    else:
        return middle_orig, middle_new
    
def write_middle(middle_orig, middle_new, destination, video_list, audio_list, checksum_list):
    os.chdir(destination)
    all_files = video_list + audio_list + checksum_list
    print('building file list...')
    for file in all_files:
        justName = Path(file).stem
        extension = Path(file).suffix
        middle_name = justName.replace(middle_orig, middle_new, 1) + extension
        print(f'{justName}{extension} to {middle_name}')
        
    proceed_yn = ask_yes_no('proceed with renaming?')
    if proceed_yn == 'Y':
        for file in all_files:
            justName = Path(file).stem
            extension = Path(file).suffix
            middle_name = justName.replace(middle_orig, middle_new, 1) + extension
            print(middle_name)
            os.rename(file, middle_name)
    else:
        print('exiting')
        
def get_suffix():
    while True:
        file_ext = input('\n\n**** enter extension of files or type skip:\n\n')
        if file_ext == 'skip':
            file_ext = "skip"
            suffix = "zip"
            print('skipping this step')
            return file_ext, suffix
        if file_ext != '':
            suffix = ''
            while suffix not in ['ARCH', 'PROD', 'SERV']:
                suffix = input('\n\n**** choose suffix to add: ARCH, PROD, or SERV\n\n').upper()
                if suffix == 'ARCH':
                    print('you chose ARCH')
                    suffix = "ARCH"
                    break
                if suffix == 'PROD':
                    print('you chose PROD')
                    suffix = "PROD"
                    break
                if suffix == 'SERV':
                    print('you chose SERV')
                    suffix = "SERV"
                    break
                else:
                    suffix = ''
                    print('\n\n**** invalid input.')
            proceed_yn = ask_yes_no(f'add "_{suffix}" to files ending in ".{file_ext}"?')
            if proceed_yn == 'Y':
                return file_ext, suffix
            else:
                print('\n\n**** try again')

def write_suffix(file_ext, suffix, destination):
    os.chdir(destination)
    print('building file list...')
    for file in glob.glob(f"*.{file_ext}"):
        justName = Path(file).stem
        extension = Path(file).suffix
        suffix_name = justName + '_' + suffix + extension
        print(f'{justName}{extension} to {suffix_name}')
        
    proceed_yn = ask_yes_no('proceed with renaming?')
    if proceed_yn == 'Y':
        for file in glob.glob(f"*.{file_ext}"):
            justName = Path(file).stem
            extension = Path(file).suffix
            suffix_name = justName + '_' + suffix + extension
            print(suffix_name)
            os.rename(file, suffix_name)
    else:
        print('exiting')

def arrange_csv(csv_file, header_list, prod, serv):
    df = pd.read_csv(csv_file, header=None)
    df.columns = header_list
    df.to_csv(csv_file, index=False, header=True)
    df.insert(4, 'intermediate_file', '')
    df.insert(5, 'service_file', '')
    df.insert(8, 'transfer_engineer', '')
    df.insert(9, 'date_digitized', '')
    df.insert(10, 'staff_notes', '')
    df.insert(12, 'intermediate_file_note', '')
    df.insert(13, 'service_file_note', '')
    df.insert(14, 'emory_ark', '')
    df.insert(15, 'emory_ark2', '')
    
    if prod == 'Y':
        prod_df = df['preservation_master_file'].str.contains('PROD', na=False)
        df.loc[prod_df, 'intermediate_file'] = df.loc[prod_df, 'preservation_master_file']
        df.loc[prod_df, 'preservation_master_file'] = ''
        df.loc[prod_df, 'intermediate_file_note'] = df.loc[prod_df, 'master_file_note']
        df.loc[prod_df, 'master_file_note'] = ''
        df['intermediate_file_note'] = df['intermediate_file_note'].str.replace(r'[\n]+', '', regex=True)
        df['inter_slice'] = df['intermediate_file'].str[:-8]
    else:
        df['inter_slice'] = ''
    if serv == 'Y':
        serv_df = df['preservation_master_file'].str.contains('SERV', na=False)
        df.loc[serv_df, 'service_file'] = df.loc[serv_df, 'preservation_master_file']
        df.loc[serv_df, 'preservation_master_file'] = ''
        df.loc[serv_df, 'service_file_note'] = df.loc[serv_df, 'master_file_note']
        df.loc[serv_df, 'master_file_note'] = ''
        df['service_file_note'] = df['service_file_note'].str.replace(r'[\n]+', '', regex=True)
        df['serv_slice'] = df['service_file'].str[:-8]
    else:
        df['serv_slice'] = ''
         
    df['master_file_note'] = df['master_file_note'].str.replace(r'[\n]+', '', regex=True)
    
    if prod == 'Y' or serv == 'Y':
        df['master_slice'] = df['preservation_master_file'].str[:-8]

    if prod == 'Y':
        merged_df = pd.merge(df, df[['master_slice']].reset_index(),
                     left_on='inter_slice', right_on='master_slice',
                     suffixes=('_int', '_ma'), how='left')
        # print(merged_df[['inter_slice', 'master_slice_int', 'index']])
        merged_df = merged_df.rename(columns={'index': 'pres_index'})
        # print(merged_df[['inter_slice', 'master_slice_int', 'pres_index']])
        keep_rows = merged_df.dropna(subset=['master_slice_ma'])
        print(keep_rows)
        intf_list = keep_rows['intermediate_file'].to_list()
        intfn_list = keep_rows['intermediate_file_note'].to_list()
        new_row = keep_rows['pres_index'].to_list()
        print(intf_list)
        print(intfn_list)
        print(new_row)
        df.loc[new_row, 'intermediate_file'] = intf_list
        df.loc[new_row, 'intermediate_file_note'] = intfn_list

    if serv == 'Y':
        merged_df = pd.merge(df, df[['master_slice']].reset_index(),
                     left_on='serv_slice', right_on='master_slice',
                     suffixes=('_serv', '_ma'), how='left')
        # print(merged_df[['serv_slice', 'master_slice_serv', 'index']])
        merged_df = merged_df.rename(columns={'index': 'pres_index'})
        # print(merged_df[['serv_slice', 'master_slice_serv', 'pres_index']])
        keep_rows = merged_df.dropna(subset=['master_slice_ma'])
        sf_list = keep_rows['service_file'].to_list()
        sfn_list = keep_rows['service_file_note'].to_list()
        new_row = keep_rows['pres_index'].to_list()
        df.loc[new_row, 'service_file'] = sf_list
        df.loc[new_row, 'service_file_note'] = sfn_list
    
    df.to_csv(csv_file, index=False, header=True)
    
def clean_csv(csv_file):
    df = pd.read_csv(csv_file)
    df_dropped = df.drop(columns=['inter_slice', 'serv_slice', 'master_slice'], errors='ignore')
    df_dropped.to_csv(csv_file, index=False, header=True)
    df_cleaned = df_dropped.dropna(subset=['preservation_master_file', 'intermediate_file', 'service_file'], how='all')
    df_cleaned.to_csv(csv_file, index=False, header=True)
    

def main(args_):
    args = setup(args_)
    source = os.path.abspath(args.source)
    destination = args.destination
    csv_file = os.path.abspath(args.csv_location)
    if args.skipcopy == False:
        copy_to_stage(source, destination)
        checksum_match(source, destination)
    else:
        pass
    move_to_root(destination)
    video_list = get_video_files(destination)
    audio_list = get_audio_files(destination)
    checksum_list = get_checksum_files(destination)
    get_mediainfo(video_list, audio_list, checksum_list, csv_file)
    header = get_prepend()
    if header != '' and header != 'skip':
        write_prepend(header, destination, video_list, audio_list, checksum_list)
    middle_orig, middle_new = get_middle()
    if middle_orig != 'skip':
        write_middle(middle_orig, middle_new, destination, video_list, audio_list, checksum_list)
    suffix_yn = ask_yes_no('add suffix to filenames?')
    if suffix_yn == 'N':
        print('skipping this step')
    if suffix_yn == 'Y':
        file_ext, suffix = get_suffix()
        if file_ext != 'skip':
            write_suffix(file_ext, suffix, destination)
            while True:
                run_again = ask_yes_no('\n\n**** add another suffix?')
                if run_again == 'Y':
                    file_ext, suffix = get_suffix()
                    if file_ext != 'skip':
                        write_suffix(file_ext, suffix, destination)
                    else:
                        break
                else:
                    break
    df_log = pd.read_csv(csv_file)
    df_log.to_csv('/Users/nraogra/Desktop/Carlos/log.csv', index=False, header=True)
    arrange_csv(csv_file,
                ['type', 'fileset_label', 'pcdm_use',
                 'preservation_master_file', 'extent',
                 'technical_note', 'master_file_note'],
                'N', 'Y')
    clean_csv(csv_file)

# def prep_staging():
# #   prepare staging directory
# #       upload metadata csv to staging directory
# #       all files should be in staging directory, with no subdirectories (all files at the same level)
# #       staging directory should be named in this format: MSSXXXX_YYYY_MM_DD
# #           (XXXX = collection number; for EUA, Oxford, and Pitts use SER or RG instead of MSS as needed)
# #   prepare destination directory (requires static IP, so can only be done from front audio workstation)
# #       connect to LIB-AV server
# #       check if a directory already exists for the collection (or series/record group for EUA, Oxford, and Pitts)
# #       if it doesn't, under the directory for the appropriate library, create a directory for the collection:
# #           ex: MSS1256 (for EUA, Oxford, and Pitts use SER or RG instead of MSS as needed)


if __name__ == '__main__':
    main(sys.argv[1:])
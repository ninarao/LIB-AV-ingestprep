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
    'prepforlibav_menu.py',
    '/Users/nraogra/Desktop/Pitts/RG0070_2026_01_15'
    ]

def setup(args_):
    parser = argparse.ArgumentParser(
        description='test description')
    parser.add_argument(
        'destination',
        help='Staging directory'
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

def copy_to_stage(destination):
    source = input('\n\n**** enter directory to copy from (with full path):     ')
    if not os.path.isdir(source):
        print(f"no directory {source} exists, returning to main menu")
        return
    else:
        if not os.path.isdir(destination):
            print(f"no directory {destination} exists, making directory")
            os.makedirs(destination)
        source = os.path.abspath(source)
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
            print('verifying checksums match...')
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
            return
        else:
            print('skipping copy and returning to main menu')
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

def get_all_files(destination):
    video_list = get_video_files(destination)
    audio_list = get_audio_files(destination)
    checksum_list = get_checksum_files(destination)
    all_files = video_list + audio_list + checksum_list
    return all_files

def rename_menu(destination):
    print(f'staging directory: {destination}')
    print('\nWhat would you like to do?')
    print('1. Prepend string to filenames')
    print('2. Replace string in filenames')
    print('3. Add suffix to filenames')
    print('Q. Quit to main menu')
    print('\n')
    
def rename_files(destination):
    while True:
        rename_menu(destination)
        choice = input('Enter your option: ').strip().upper()
        if choice == '1':
            prepend(destination)
        elif choice == '2':
            middle(destination)
        elif choice == '3':
            add_suffix(destination)
        elif choice in ['Q', 'q']:
            print(' - Returning to main menu')
            break
        else:
            print(' - Incorrect input. Please enter 1, 2, 3, or Q')

def prepend(destination):
    while True:
        all_files = get_all_files(destination)
        header = input('\n**** enter string to be prepended to filenames or type Q to quit to menu\n\n')
        if header in ['Q', 'q']:
            print('returning to menu')
            break
        else:
            print(f'you entered: "{header}"')
            os.chdir(destination)
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
                break
            else:
                print('\ntry again')

def middle(destination):
    while True:
        all_files = get_all_files(destination)
        middle_orig = input('\n**** enter string to be replaced in filenames or type Q to quit to menu\n\n')
        if middle_orig in ['Q', 'q']:
            print('returning to menu')
            break
        else:
            middle_new = input('\n**** enter replacement string\n')
            print(f'replace "{middle_orig}" with "{middle_new}"')
            os.chdir(destination)
            print('building file list...')
            for file in all_files:
                justName = Path(file).stem
                extension = Path(file).suffix
                if middle_orig in justName:
                    middle_name = justName.replace(middle_orig, middle_new, 1) + extension
                    print(f'{justName}{extension} to {middle_name}')
            proceed_yn = ask_yes_no('proceed with renaming?')
            if proceed_yn == 'Y':
                for file in all_files:
                    justName = Path(file).stem
                    extension = Path(file).suffix
                    if middle_orig in justName:
                        middle_name = justName.replace(middle_orig, middle_new, 1) + extension
                        print(middle_name)
                        os.rename(file, middle_name)
                break
            else:
                print('\ntry again')
        
def add_suffix(destination):
    while True:
        suffix = ''
        file_ext = input('\n**** enter extension of files or type Q to quit to menu\n\n')
        if file_ext in ['Q', 'q']:
            print('returning to menu')
            return file_ext, suffix
        else:
            while suffix not in ['ARCH', 'PROD', 'SERV']:
                suffix = input('\n\n**** choose suffix to add: ARCH, PROD, or SERV\n\n').upper()
                if suffix == 'ARCH':
                    suffix = "ARCH"
                    break
                if suffix == 'PROD':
                    suffix = "PROD"
                    break
                if suffix == 'SERV':
                    suffix = "SERV"
                    break
                else:
                    suffix = ''
                    print('\n**** invalid input.')
            print(f'add "_{suffix}" to files ending in ".{file_ext}"')
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
                return file_ext, suffix
            else:
                print('\ntry again')
                return file_ext, suffix

def rename_stage(destination):
    os.chdir(destination)
    print('\n\nstaging directory should be named in this format: MSSXXXX_YYYY_MM_DD \
            \n\nXXXX = collection number \
            \n\n**for EUA, Oxford, and Pitts use SER or RG instead of MSS as needed**')
    old_path, old_name = os.path.split(destination)
    new_name = input('\n\n**** enter new name for directory:     ').upper()
    rename = ask_yes_no(f'rename directory from {old_name} to {new_name}?')
    if rename == 'N':
        print('skipping rename')
    elif rename == 'Y':
        new_dest = os.path.join(old_path, new_name)
        print(f'renaming {destination} to {new_dest}')
        try:
            os.rename(destination, new_dest)
            return new_dest
        except NotADirectoryError:
            print('not a directory')
            new_dest = ''
            return new_dest

def move_to_top(maindir):
    os.chdir(maindir)      
    subdirs = os.listdir(maindir)
    subs=[]
    for dir in subdirs:
        if os.path.isdir(dir) == True:
            subdir_path = os.path.join(maindir,dir)
            subs.append(subdir_path)
    if not subs:
        print('no subdirectories, returning to main menu')
        return
    else:
        print('subdirectories found:')
        for subdir in subs:
            print('\t' + subdir)
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

def get_mediainfo(destination):
    video_list = get_video_files(destination)
    audio_list = get_audio_files(destination)
    checksum_list = get_checksum_files(destination)
    #get csv location or create
    csv_location = input('\n\n**** enter csv location or leave blank to create csv:     ')
    if csv_location != '':
        csv_file = os.path.abspath(csv_location)
    else:
        csv_dir = os.path.basename(destination)
        csvv = 'Object_CSV_' + csv_dir + '.csv'
        csv_file = os.path.join(destination, csvv)
        
    csv_basename = os.path.basename(csv_file)
    csv_path = os.path.dirname(csv_file)
    name, extension = os.path.splitext(csv_basename)
    # write mediainfo output to csv
    print(csv_file)
    with open(csv_file, 'w', encoding='utf-8', newline='') as f:
        writer=csv.writer(f)
        for file in video_list:
            cmd_vid_trk = [
                'mediainfo',
                '--Output=General;%VideoCount%',
                file
                ]
            print(cmd_vid_trk)
            try:
                vid_check = subprocess.check_output(cmd_vid_trk).decode(sys.stdout.encoding)
            except subprocess.CalledProcessError as e:
                print(f"Command failed with error code {e.returncode}")
            if vid_check.strip() == '1':
                print('true')
                cmd_video = [
                    'mediainfo',
                    '--Output=General;fileset,Video,Primary Content,%FileNameExtension%,\nVideo;%Duration/String4%,%DisplayAspectRatio/String% DAR %FrameRate% FPS,%Format% %Width%x%Height/String% \nAudio;%Format% %SamplingRate/String% %BitDepth/String%',
                    file]
                try:
                    csv_video = subprocess.check_output(cmd_video).decode(sys.stdout.encoding)
                except subprocess.CalledProcessError as e:
                    print(f"Command failed with error code {e.returncode}")
                print(csv_video)
            else:
                cmd_video = [
                    'mediainfo',
                    '--Output=General;fileset,Video,Primary Content,%FileNameExtension%,%Duration/String3%,,\nAudio;%Format% %SamplingRate/String% %BitDepth/String%',
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
    csv_log_name = name + '_log' + extension
    csv_log = os.path.join(csv_path, csv_log_name)
    df_log = pd.read_csv(csv_file, header=None, names=range(7))
    df_log.to_csv(csv_log, index=False, header=False)
    return csv_file

def arrange_csv(csv_file, header_list):
    prod = 'N'
    serv = 'N'
    while True:
        print('which file types are in this batch? choose all that apply or type Q to quit.')
        print('1. ARCH')
        print('2. PROD')
        print('3. SERV')
        valid_choices = ['1', '2', '3']
        answer = input('enter numbers separated by spaces: ').split()
        if 'Q' in answer or 'q' in answer:
            print(' - Returning to main menu')
            return
        elif all(char == '1' for char in answer):
            print('only arch files - no prod or serv files')
            break
        else:
            for char in answer:
                if char not in valid_choices:
                    print(f'invalid input: {answer} try again')
                elif char == '2':
                    prod = 'Y'
                elif char == '3':
                    serv = 'Y'
            if prod == 'Y' or serv == 'Y':
                break
    
    df = pd.read_csv(csv_file, header=None, names=header_list)
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
        prod_df = (df['preservation_master_file'].str.contains('PROD', na=False)) & (df['pcdm_use'].str.contains('Primary', na=False))
        df.loc[prod_df, 'intermediate_file'] = df.loc[prod_df, 'preservation_master_file']
        df.loc[prod_df, 'preservation_master_file'] = ''
        df.loc[prod_df, 'intermediate_file_note'] = df.loc[prod_df, 'master_file_note']
        df.loc[prod_df, 'master_file_note'] = ''
        df['intermediate_file_note'] = df['intermediate_file_note'].str.replace(r'[\n]+', '', regex=True)
        df['inter_slice'] = df['intermediate_file'].str[:-8]
    else:
        df['inter_slice'] = ''
    if serv == 'Y':
        serv_df = (df['preservation_master_file'].str.contains('SERV', na=False)) & (df['pcdm_use'].str.contains('Primary', na=False))
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
        
        intf_list = keep_rows['intermediate_file'].to_list()
        intfn_list = keep_rows['intermediate_file_note'].to_list()
        new_row = keep_rows['pres_index'].to_list()

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
    
def main_menu(destination):
    print(f'staging directory: {destination}')
    print('\nWhat would you like to do?')
    print('1. Copy files to staging directory')
    print('2. Rename files')
    print('3. Rename staging directory')
    print('4. Move files to top-level directory')
    print('5. Create metadata csv')
    print('Q. Quit')

def main(args_):
    args = setup(args_)
    stage_dir = ''
    while True:
        if stage_dir != '':
            destination = new_dest
        else:
            destination = args.destination
        main_menu(destination)
        choice = input('\nEnter your option: ').strip().upper()
        if choice == '1':
            copy_to_stage(destination)
        elif choice == '2':
            rename_files(destination)
        elif choice == '3':
            new_dest = rename_stage(destination)
            if new_dest is not None:
                stage_dir = new_dest
            else:
                stage_dir = ''
        elif choice == '4':
            move_to_top(destination)
        elif choice == '5':
            csv_file = get_mediainfo(destination)
            arrange_csv(csv_file,
                ['type', 'fileset_label', 'pcdm_use',
                 'preservation_master_file', 'extent',
                 'technical_note', 'master_file_note'])
            clean_csv(csv_file)
        elif choice == 'Q':
            print(' - Exiting program. Goodbye!')
            break
        else:
            print(' - Incorrect input. Please enter 1, 2, 3, 4, 5, or Q')

# #   prepare destination directory
# #       connect to LIB-AV server (requires static IP, so can only be done from front audio workstation)
# #       check if a directory already exists for the collection (or series/record group for EUA, Oxford, and Pitts)
# #       if it doesn't, under the directory for the appropriate library, create a directory for the collection:
# #           ex: MSS1256 (for EUA, Oxford, and Pitts use SER or RG instead of MSS as needed)

if __name__ == '__main__':
    main(sys.argv[1:])

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

# sys.argv = [
#     'prepforlibav.py',
#     '/Users/nraogra/Desktop/Pitts/RG0070_2026_01_15'
#     ]

def setup(args_):
    parser = argparse.ArgumentParser(
        description='test description')
    parser.add_argument(
        'source',
        help='directory of files'
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

def copy_to_stage(source):
    dest = input('\n\n**** enter directory to copy to (with full path):     ')
    if not os.path.isdir(dest):
        print(f"no directory {dest} exists, making directory")
        os.makedirs(dest)
    source = os.path.abspath(source)
    sourceContents = source + '/'
    cmd_dryrun = [
        'rsync', '--dry-run',
        '-ah', '-vv',
        '--exclude=.*', '--exclude=.*/', '--exclude=*DS_Store', 
        '--progress', '--stats',
        sourceContents, dest
    ]
    print(f"dry run of copy to stage command: {cmd_dryrun}")
    subprocess.call(cmd_dryrun)
    run_copy = ask_yes_no('continue with copy to staging location?')
    if run_copy == 'Y':
        cmd_copy = [
            'rsync', 
            '-ah', '-vv',
            '--exclude=.*', '--exclude=.*/', '--exclude=*DS_Store', 
            '--progress', '--stats',
            sourceContents, dest
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
            sourceContents, dest
        ]
        print(cmd_checkmatch)
        subprocess.call(cmd_checkmatch)
        return
    else:
        print('skipping copy and returning to main menu')
        return

def get_video_files(source):
    video_list = []
    if os.path.isdir(source):
        folder_list = os.listdir(source)
        for filename in folder_list:
            if not filename[0] == '.':
                if filename.lower().endswith(('.MOV', '.mov', 'MP4', '.mp4', '.mkv', '.MXF', '.mxf', '.dv', '.DV', '.MTS', '.swf', '.avi', '.m2t')):
                    video_list.append(os.path.join(source, filename))
    elif os.path.isfile(source):
        video_list = [source]
    return video_list

def get_audio_files(source):
    audio_list = []
    if os.path.isdir(source):
        folder_list = os.listdir(source)
        for filename in folder_list:
            if not filename[0] == '.':
                if filename.lower().endswith(('.WAV', '.wav', '.aiff', '.AIFF', '.mp3', '.MP3')):
                    audio_list.append(os.path.join(source, filename))
    elif os.path.isfile(source):
        audio_list = [source]
    return audio_list
        
def get_checksum_files(source):
    checksum_list = []
    if os.path.isdir(source):
        folder_list = os.listdir(source)
        for filename in folder_list:
            if not filename[0] == '.':
                if filename.lower().endswith(('.MD5', '.md5', '.SHA1', '.sha1', '.TXT', '.txt')):
                    checksum_list.append(os.path.join(source, filename))
    elif os.path.isfile(source):
        checksum_list = [source]
    return checksum_list

def get_all_files(source):
    video_list = get_video_files(source)
    audio_list = get_audio_files(source)
    checksum_list = get_checksum_files(source)
    all_files = video_list + audio_list + checksum_list
    return all_files

def rename_menu(source):
    print(f'staging directory: {source}')
    print('\nWhat would you like to do?')
    print('1. Prepend string to filenames')
    print('2. Replace string in filenames')
    print('3. Add suffix to filenames')
    print('Q. Quit to main menu')
    print('\n')
    
def rename_files(source):
    while True:
        rename_menu(source)
        choice = input('Enter your option: ').strip().upper()
        if choice == '1':
            prepend(source)
        elif choice == '2':
            middle(source)
        elif choice == '3':
            add_suffix(source)
        elif choice in ['Q', 'q']:
            print(' - Returning to main menu')
            break
        else:
            print(' - Incorrect input. Please enter 1, 2, 3, or Q')

def prepend(source):
    while True:
        all_files = get_all_files(source)
        header = input('\n**** enter string to be prepended to filenames or type Q to quit to menu\n\n')
        if header in ['Q', 'q']:
            print('returning to menu')
            break
        else:
            print(f'you entered: "{header}"')
            os.chdir(source)
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

def middle(source):
    while True:
        all_files = get_all_files(source)
        middle_orig = input('\n**** enter string to be replaced in filenames or type Q to quit to menu\n\n')
        if middle_orig in ['Q', 'q']:
            print('returning to menu')
            break
        else:
            middle_new = input('\n**** enter replacement string\n')
            print(f'replace "{middle_orig}" with "{middle_new}"')
            os.chdir(source)
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
        
def add_suffix(source):
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
            os.chdir(source)
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

def rename_stage(source):
    os.chdir(source)
    print('\n\nstaging directory should be named in this format: MSSXXXX_YYYY_MM_DD \
            \n\nXXXX = collection number \
            \n\n**for EUA, Oxford, and Pitts use SER or RG instead of MSS as needed**')
    old_path, old_name = os.path.split(source)
    new_name = input('\n\n**** enter new name for directory:     ').upper()
    rename = ask_yes_no(f'rename directory from {old_name} to {new_name}?')
    if rename == 'N':
        print('skipping rename')
    elif rename == 'Y':
        new_dest = os.path.join(old_path, new_name)
        print(f'renaming {source} to {new_dest}')
        try:
            os.rename(source, new_dest)
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
        print('no subdirectories, returning to main menu\n')
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

def get_mediainfo(source):
    video_list = get_video_files(source)
    audio_list = get_audio_files(source)
    checksum_list = get_checksum_files(source)
    
    csv_location = input('\n\n**** enter csv location or leave blank to create csv:     ')
    if csv_location != '':
        csv_file = os.path.abspath(csv_location)
    else:
        csv_dir = os.path.basename(source)
        csvv = 'Object_CSV_' + csv_dir + '.csv'
        csv_file = os.path.join(source, csvv)
        
    csv_basename = os.path.basename(csv_file)
    csv_path = os.path.dirname(csv_file)
    name, extension = os.path.splitext(csv_basename)
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
    df.insert(15, 'abstract', '')
    df.to_csv(csv_file, index=False, header=True)
    df = pd.read_csv(csv_file)
    
    serv_df = (df['preservation_master_file'].str.contains('SERV', na=False)) & (df['pcdm_use'].str.contains('Primary', na=False))
    df['service_file'] = df['service_file'].astype(str)
    df.loc[serv_df, 'service_file'] = df.loc[serv_df, 'preservation_master_file']
    df.loc[serv_df, 'preservation_master_file'] = df.loc[serv_df, 'preservation_master_file'].str[:-9]
    df['service_file_note'] = df['service_file_note'].astype(str)
    df.loc[serv_df, 'service_file_note'] = df.loc[serv_df, 'master_file_note']
    df.loc[serv_df, 'master_file_note'] = ''
    df['service_file_note'] = df['service_file_note'].str.replace(r'[\n]+', '', regex=True)
    df_sc = df[serv_df]
    
    prod_df = (df['preservation_master_file'].str.contains('PROD', na=False)) & (df['pcdm_use'].str.contains('Primary', na=False))
    df['intermediate_file'] = df['intermediate_file'].astype(str)
    df.loc[prod_df, 'intermediate_file'] = df.loc[prod_df, 'preservation_master_file']
    df.loc[prod_df, 'preservation_master_file'] = df.loc[prod_df, 'preservation_master_file'].str[:-9]
    df['intermediate_file_note'] = df['intermediate_file_note'].astype(str)
    df.loc[prod_df, 'intermediate_file_note'] = df.loc[prod_df, 'master_file_note']
    df.loc[prod_df, 'master_file_note'] = ''
    df['intermediate_file_note'] = df['intermediate_file_note'].str.replace(r'[\n]+', '', regex=True)
    df_pc = df[prod_df]    
    
    arch_df = (df['pcdm_use'].str.contains('Primary', na=False)) & (df['preservation_master_file'].str.contains('ARCH', na=False))
    df['staff_notes'] = df['staff_notes'].astype(str)
    df.loc[arch_df, 'staff_notes'] = df['preservation_master_file']
    df.loc[arch_df, 'preservation_master_file'] = df.loc[arch_df, 'preservation_master_file'].str[:-9]
    df_ac = df[arch_df]

    merged_df = pd.merge(df_ac, df_sc[['preservation_master_file', 'fileset_label', 'extent', 'technical_note', 'service_file', 'service_file_note']], on='preservation_master_file', how='outer')
    mergedd_df = pd.merge(merged_df, df_pc[['preservation_master_file', 'fileset_label', 'extent', 'technical_note', 'intermediate_file', 'intermediate_file_note']], on='preservation_master_file', how='outer')
    mergedd_df['preservation_master_file'] = mergedd_df['staff_notes']
    mergedd_df['service_file_x'] = mergedd_df['service_file_y']
    mergedd_df['service_file_note_x'] = mergedd_df['service_file_note_y']
    mergedd_df['intermediate_file_x'] = mergedd_df['intermediate_file_y']
    mergedd_df['intermediate_file_note_x'] = mergedd_df['intermediate_file_note_y']
    mergedd_df = mergedd_df.drop(columns=['fileset_label', 'extent', 'technical_note', 'service_file_y', 'intermediate_file_y', 'service_file_note_y', 'intermediate_file_note_y'])
    mergedd_df = mergedd_df.rename(columns={'fileset_label_x': 'fileset_label', 'extent_x': 'extent',
                                            'technical_note_x': 'technical_note', 'service_file_x': 'service_file',
                                            'intermediate_file_x': 'intermediate_file', 'service_file_note_x': 'service_file_note',
                                            'intermediate_file_note_x': 'intermediate_file_note'})
    mergedd_df['staff_notes'] = pd.NA
    mergedd_df['type'] = mergedd_df['type'].mask(pd.isnull(mergedd_df['type']), 'fileset') 
    mergedd_df['pcdm_use'] = mergedd_df['pcdm_use'].mask(pd.isnull(mergedd_df['pcdm_use']), 'Primary Content') 
    mergedd_df['fileset_label'] = mergedd_df['fileset_label'].fillna(mergedd_df['fileset_label_y'])
    mergedd_df['extent'] = mergedd_df['extent'].fillna(mergedd_df['extent_y'])
    mergedd_df['technical_note'] = mergedd_df['technical_note'].fillna(mergedd_df['technical_note_y'])
    mergedd_df = mergedd_df.drop(columns=['fileset_label_y', 'extent_y', 'technical_note_y'])
    mergedd_df.reset_index(drop=True, inplace=True)
    mergedd_df.to_csv(csv_file, index=False, header=True)

    serv_val_df = (df['pcdm_use'].str.contains('Validation', na=False)) & (df['preservation_master_file'].str.contains('SERV', na=False))
    df['service_file_note'] = df['service_file_note'].astype(str)
    df.loc[serv_val_df, 'service_file_note'] = df['preservation_master_file']
    df['service_file_note'] = df['service_file_note'].str.replace(r'[\n]+', '', regex=True)
    df.loc[serv_val_df, 'preservation_master_file'] = df.loc[serv_val_df, 'preservation_master_file'].str[:-9]
    df_s = df[serv_val_df]

    prod_val_df = (df['pcdm_use'].str.contains('Validation', na=False)) & (df['preservation_master_file'].str.contains('PROD', na=False))
    df['intermediate_file_note'] = df['intermediate_file_note'].astype(str)
    df['intermediate_file_note'] = df['intermediate_file_note'].str.replace(r'[\n]+', '', regex=True)
    df.loc[prod_val_df, 'intermediate_file_note'] = df['preservation_master_file']
    df.loc[prod_val_df, 'preservation_master_file'] = df.loc[prod_val_df, 'preservation_master_file'].str[:-9]
    df_p = df[prod_val_df]

    arch_val_df = (df['pcdm_use'].str.contains('Validation', na=False)) & (df['preservation_master_file'].str.contains('ARCH', na=False))
    df.loc[arch_val_df, 'master_file_note'] = df['preservation_master_file']
    df['master_file_note'] = df['master_file_note'].str.replace(r'[\n]+', '', regex=True)
    df.loc[arch_val_df, 'preservation_master_file'] = df.loc[arch_val_df, 'preservation_master_file'].str[:-9]
    df_a = df[arch_val_df]

    mergedv_df = pd.merge(df_a, df_s[['preservation_master_file', 'service_file_note']], on='preservation_master_file', how='outer')
    mergeddv_df = pd.merge(mergedv_df, df_p[['preservation_master_file', 'intermediate_file_note']], on='preservation_master_file', how='outer')
    mergeddv_df['preservation_master_file'] = mergeddv_df['master_file_note']
    mergeddv_df['service_file'] = mergeddv_df['service_file_note_y']
    mergeddv_df['intermediate_file'] = mergeddv_df['intermediate_file_note_y']
    mergeddv_df = mergeddv_df.rename(columns={'service_file_note_x': 'service_file_note', 'intermediate_file_note_x': 'intermediate_file_note'})
    mergeddv_df['master_file_note'] = pd.NA
    mergeddv_df['intermediate_file_note'] = pd.NA
    mergeddv_df['service_file_note'] = pd.NA
    mergeddv_df['staff_notes'] = pd.NA
    mergeddv_df['type'] = mergeddv_df['type'].mask(pd.isnull(mergeddv_df['type']), 'fileset') 
    mergeddv_df['fileset_label'] = mergeddv_df['fileset_label'].mask(pd.isnull(mergeddv_df['fileset_label']), 'checksum files') 
    mergeddv_df['pcdm_use'] = mergeddv_df['pcdm_use'].mask(pd.isnull(mergeddv_df['pcdm_use']), 'Content Validation') 
    mergeddv_df = mergeddv_df.drop(columns=['service_file_note_y', 'intermediate_file_note_y'])
    mergeddv_df.reset_index(drop=True, inplace=True)
    mergeddv_df.to_csv(csv_file, index=False, header=True)

    df_combined = pd.concat([mergedd_df, mergeddv_df], ignore_index=True)
    df_combined.insert(0, 'deduplication_key', '')
    df_combined.insert(1, 'other_identifiers', '')
    df_combined.insert(3, 'title', '')
    df_combined.insert(4, 'holding_repository', '')
    df_combined.insert(5, 'content_type', '')
    df_combined.insert(11, 'extracted', '')
    df_combined.insert(12, 'transcript_file', '')
    df_combined.insert(13, 'content_genres', '')
    df_combined.insert(15, 'sublocation', '')
    df_combined.insert(17, 'local_call_number', '')
    df_final = df_combined.assign(administrative_unit='', contact_information='', creator='',
                                  date_created='', date_issued='', content_genres='', institution='',
                                  primary_language='', notes='', place_of_production='', publisher='',
                                  emory_rights_statements='', rights_statement='', subject_names='',
                                  subject_geo='', keywords='', subject_topics='', uniform_title='',
                                  date_classifications='', visibility='', copyright_date='',
                                  internal_rights_note='', rights_holders='', legacy_rights='',
                                  sensitive_material='', sensitive_material_note='', Ingestworkflow_notes='',
                                  Ingestworkflow_rights_basis='', Ingestworkflow_rights_basis_date='',
                                  Ingestworkflow_rights_basis_note='', RightsAccessLevel='',
                                  Accessionworkflow_rights_basis='', Accessionworkflow_rights_basis_date='',
                                  Accessionworkflow_rights_basis_reviewer='', Accessionworkflow_rights_basis_note='')
    df_final.columns = df_final.columns.str.replace('Ingestw', 'Ingest.w')
    df_final.columns = df_final.columns.str.replace('Accessionw', 'Accession.w')
    df_final.columns = df_final.columns.str.replace('RightsAccessLevel', 'Rights - Access Level')
    df_final.to_csv(csv_file, index=False, header=True)

def main_menu(source):
    print(f'current staging directory: {source}')
    print('\nWhat would you like to do?')
    print('1. Copy files to another location')
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
            source = new_dest
        else:
            source = args.source
        if not os.path.isdir(source):
            print(f"no directory {source} exists, exiting program.")
            break
        main_menu(source)
        choice = input('\nEnter your option: ').strip().upper()
        if choice == '1':
            copy_to_stage(source)
        elif choice == '2':
            rename_files(source)
        elif choice == '3':
            new_dest = rename_stage(source)
            if new_dest is not None:
                stage_dir = new_dest
            else:
                stage_dir = ''
        elif choice == '4':
            move_to_top(source)
        elif choice == '5':
            csv_file = get_mediainfo(source)
            arrange_csv(csv_file,
                ['type', 'fileset_label', 'pcdm_use',
                 'preservation_master_file', 'extent',
                 'technical_note', 'master_file_note'])
        elif choice == 'Q':
            print(' - Exiting program. Goodbye!')
            break
        else:
            print(' - Incorrect input. Please enter 1, 2, 3, 4, 5, or Q')

if __name__ == '__main__':
    main(sys.argv[1:])
#!/usr/bin/python3
from asyncio.subprocess import PIPE
from datetime import datetime
import os
import subprocess
from sys import stdout
from datetime import datetime
import time

# Returns strings for functions that have any return from the operating system
def os_command_with_return(command, decode="utf-8"):
    cmd = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    cmd.wait()
    return cmd.stdout.read().decode(decode)


# returns the previous computer boot time information
def get_previous_boot_time():
    current_year = os_command_with_return("date +%Y").strip()
    try:
        logs_file = open("/Cleaner/boot_logs/" + current_year + "/boot_logs.txt")
        previous_boot_time = str(logs_file.readlines()[-2]).strip()
        return previous_boot_time
    except:
        exit()


# Returns the computer's boot time information
def get_current_boot_time():
    current_boot_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return current_boot_time


# It returns the wanted and unwanted files as two different lists.
def get_junk_files(
    includedDirectories="/Cleaner/.junk_cleaner/include.txt",
    excludedDirectories="/Cleaner/.junk_cleaner/exclude.txt",
):
    to_look = []
    to_exclude = []

    with open(includedDirectories, "r") as file:
        for line in file:
            if not line.startswith("#") and not line.startswith("\n"):
                to_look.append(line.strip())
    with open(excludedDirectories, "r") as file:
        for line in file:
            if not line.startswith("#") and not line.startswith("\n"):
                to_exclude.append(line.strip())

    return to_look, to_exclude


def clean_directories():
    previous_boot_time = get_previous_boot_time()
    current_boot_time = get_current_boot_time()

    dirs_to_check, dirs_to_ignore = get_junk_files()

    junk_files = []

    for dir in dirs_to_check:
        command = (
            "find "
            + str(dir)
            + ' -newermt "'
            + str(previous_boot_time)
            + '" ! -newermt "'
            + str(current_boot_time)
            + '"'
        )

        for ignore in dirs_to_ignore:
            if str(ignore).find(str(dir)) != -1:
                command += ' -not -path "' + ignore + '/*"'

        files_to_remove = os_command_with_return(command).split("\n")

        try:
            files_to_remove.remove("")
        except ValueError:
            pass
        junk_files.extend(files_to_remove)

    for dir in dirs_to_check:
        try:
            junk_files.remove(dir)
        except ValueError:
            pass

    for dir in dirs_to_ignore:
        try:
            junk_files.remove(dir)
        except ValueError:
            pass

    backup_files(previous_boot_time, junk_files)

    if len(junk_files) != 0:
        for file in junk_files:
            os.system('echo rm -r "' + file + '" >> /Cleaner/deleted_files.txt')
            os.system('rm -r "' + file + '"')


def backup_files(backup_boot_time, junk_files):
    if not os.path.exists("/Cleaner/.backups"):
        os.mkdir("/Cleaner/.backups")
    backup_count = os.listdir("/Cleaner/.backups")

    if len(junk_files) == 0:
        return
    else:
        try:
            os.mkdir("/Cleaner/.backups/" + str(backup_boot_time))
        except FileExistsError:
            return

        flag = False
        will_be_removed = []
        if len(backup_count) == 6:
            flag = True
            with open("/Cleaner/.backups/last_backup_time.txt", "r") as log:
                last_backup_time = log.readline().strip()
                os.system('rm -r "/Cleaner/.backups/' + last_backup_time + '"')

            f = open("/Cleaner/.backups/last_backup_time.txt", "r")
            will_be_removed = f.readlines()[1:]
            f.close()
            os.system('rm -r "/Cleaner/.backups/last_backup_time.txt"')

        for junk in junk_files:
            # Since the file directory and name information is kept in a single variable,
            # the rsplit command is used for the "/" character,
            # it will split into /home/test/junk.txt >> /home/test and junk.txt.
            # The operation cannot be done from the left because it is unknown
            # how many folders are passed until the directory of the file
            # (the number of the "/" sign varies)
            path = junk.rsplit("/", 1)[0]
            file = junk.rsplit("/", 1)[1]
            cmd = (
                "find "
                + '"'
                + path
                + '"'
                + ' -name "'
                + file
                + '" -type f -exec cp -r --parents \\{\\} "/Cleaner/.backups/'
                + str(backup_boot_time)
                + '" \\;'
            )
            os.system(cmd)

        backup_log = open("/Cleaner/.backups/last_backup_time.txt", "a+")
        if flag:
            backup_log.writelines(will_be_removed)
        backup_log.write(backup_boot_time + "\n")
        backup_log.close()


# Since the deletion is performed by root, the ownership of the
# directories passes to the root account. In order for the student account
# to be able to delete any file, ehe ownership (write and read permissions)
# of the trash and subdirectories must be transferred to the student account.
def clear_trash():
    os.system("rm -rf /home/ogrenci/.local/share/Trash/*")
    os.system("chmod -R o+rw /home/ogrenci/.local/share/Trash")
    os.system("chmod -R o+rw /home/ogrenci/.local/share/Trash/files")
    os.system("chmod -R o+rw /home/ogrenci/.local/share/Trash/expunged")
    os.system("chmod -R o+rw /home/ogrenci/.local/share/Trash/info")


def main():
    clean_directories()
    clear_trash()


if __name__ == "__main__":
    main()

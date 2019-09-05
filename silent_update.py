#!/usr/bin/python
"""
This script will silently patch any app by bundle ID, but only if the app itself is not running
you must supply the bundle ID of the app to check and the policy event manual trigger for jamf as
positional parameters 3 and 4

author:  tlark

Mac Admin Slack @tlark

"""

# import modules
from Cocoa import NSRunningApplication
import sys
import subprocess
import argparse


# parse arguments

parser = argparse.ArgumentParser(description='Silently patch any not currently running app.')
parser.add_argument('mount_point', help='(NOT USED) Mount point of the target drive')
parser.add_argument('computer_name', help='(NOT USED) Computer name')
parser.add_argument('username', help='(NOT USED) User name')
parser.add_argument('app_list', help='Comma seperated list of bundle IDs of the applications to patch')
parser.add_argument('update_policy', help='Update policy to run.')
args = parser.parse_args()

APPS = args.app_list.split(',')
POLICY = args.update_policy


# start functions

def check_if_running(bid):
    """Test to see if an app is running by bundle ID"""
    # macOS API to check if an app bundle is running or not
    app = NSRunningApplication.runningApplicationsWithBundleIdentifier_(bid)
    # return True if running, False if not
    if app:
        return True
    if not app:
        return False


def run_update_policy(event):
    """run the updater policy for the app"""
    # unix command list
    cmd = ['/usr/local/bin/jamf', 'policy', '-event', event]
    # execute the policy to the binary
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # grab stdout and stderr pipes and communicate them to the shell
    out, err = proc.communicate()
    # if we get a non zero response, print the error
    if proc.returncode != 0:
        print('Error: %s' % err)


def main():
    """main policy to run the jewels"""
    # iterate through bundle IDs for the edge case a developer changes a bundle ID
    for app in APPS:
        # if the app is running, we will silently exit
        if check_if_running(app):
            sys.exit(0)
    else:
        run_update_policy(POLICY)


# run the main
if __name__=='__main__':
    main()

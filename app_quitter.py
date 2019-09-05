#!/usr/bin/python

"""
This script will prompt end users to quit apps, or force quit apps depending on the options passed
in the positional parameters

Since this will be ran by jamf remember the first 3 parameters are reserved by jamf, so we will start with parameter 4

APP_LIST will be a comma separated list of bundle IDs of apps you want this code to quit, example:

com.apple.Safari,org.mozilla.firefox,com.google.Chrome

PROMPT will be the parameter you use to decide to prompt the user or not, use strings "true" or "false"

APP_NAME will be the name of the application and how you want to present it in a dialog box, i.e. Safari or Safari.app

UPDATE_POLICY is the jamf event to trigger the policy to update the app

FORCE_QUIT is set to true or false in jamf as a psoitional parameter, if you set this to true it does as advertised
and will force quit the apps by bundle ID and force an update

SYMBOL is the unicode string for the heart emoji, because we can

MESSAGE is the actual message you wish to display to the end user

COMPLETE is the message that will pop when the patch is complete

FORCEMSG = the template message to pop when doing a forced update for security reasons
"""


# import modules
from Cocoa import NSRunningApplication
import sys
import subprocess
import os
import time
import argparse


# process arguments

def str_to_bool(string):
    value = string.lower()
    if value == 'true':
        return True
    if value == 'false':
        return False
    raise argparse.ArgumentTypeError('The value must be "true" or "false".')


parser = argparse.ArgumentParser(description='Prompt (or force) a user to quit one or more applications.')
parser.add_argument('mount_point', help='(NOT USED) Mount point of the target drive')
parser.add_argument('computer_name', help='(NOT USED) Computer name')
parser.add_argument('username', help='(NOT USED) User name')
parser.add_argument('app_list', help='Comma seperated list of bundle IDs of the applications to quit')
parser.add_argument('prompt', type=str_to_bool,
                    help='Prompt the user ("true" or "false")')
parser.add_argument('app_name', help='Display name of the app to use in dialog boxes (i.e. "Safari")')
parser.add_argument('update_policy', help='The event trigger of the Jamf policy that will update the app')
parser.add_argument('force_quit', type=str_to_bool,
                    help='Force quit the app, just in case you need that big red button ("true" or "false")')
args = parser.parse_args()

APP_LIST = args.app_list.split(',')
PROMPT = args.prompt
APP_NAME = args.app_name
UPDATE_POLICY = args.update_policy
FORCE_QUIT = args.force_quit


# global variables

# heart emoji, because we love Snowflake!
SYMBOL = u'\u2764\ufe0f'

# message to prompt the user to quit and update an app
MESSAGE = """Greetings Employee:

I.T. would like to patch {0}.  Please click on the "OK" button to continue, this will prompt you to quit your application and save your work.

You may click "Cancel" to delay this update.

{1} I.T.
""".format(APP_NAME, SYMBOL.encode("utf-8"))

FORCEMSG = """Greetings Snowflake:

I.T. would like to patch {0}.  This is an emergency patch and the application will be quit to deploy security patches.

{1} I.T.
""".format(APP_NAME, SYMBOL.encode("utf-8"))

# message to notify the user upon completion
COMPLETE = """Thank You!

{0} has been patched on your system.  You may relaunch it now if you wish
""".format(APP_NAME)


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


def user_prompt(prompt):
    """simple jamf helper dialog box"""
    # set the path to your custom branding, it will default to the warning sign if your branding is not found
    icon = ''
    # test to see what icons are available on the file system
    if not os.path.exists(icon):
        # default fail over icon in case our custom one does not exist
        icon = '/System/Library/CoreServices/Problem Reporter.app/Contents/Resources/ProblemReporter.icns'
    # build the jamf helper unix command in a list
    cmd = ['/Library/Application Support/JAMF/bin/jamfHelper.app/Contents/MacOS/jamfHelper',
           '-windowType', 'utility',
           '-title', 'Quit Applications',
           '-description', prompt,
           '-icon', icon,
           '-button1', 'OK', '-button2', 'Cancel', '-defaultbutton', '1']
    # call the command via subprocess
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # get stdout and stderr
    out, err = proc.communicate()
    # check for exit status for button clicked, 0 = OK 2 = Cancel
    if proc.returncode == 0:
        # user clicked OK
        return True
    if proc.returncode == 2:
        # user clicked cancel
        return False
    # if there is any other return print it
    else:
        print('Error: %s' % err)


def force_quit_prompt(prompt):
    """jamf helper dialog to inform of the force quit"""
    # Custom branding icon path goes here for Force Quit work flows 
    icon = ''
    # test to see what icons are available on the file system
    if not os.path.exists(icon):
        # default fail over icon in case our custom one does not exist
        icon = '/System/Library/CoreServices/Problem Reporter.app/Contents/Resources/ProblemReporter.icns'
    # build the jamf helper unix command in a list
    cmd = ['/Library/Application Support/JAMF/bin/jamfHelper.app/Contents/MacOS/jamfHelper',
           '-windowType', 'utility',
           '-title', 'Quit Applications',
           '-description', prompt,
           '-icon', icon,
           '-button1', 'OK', '-defaultbutton', '1']
    # call the command via subprocess
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # get stdout and stderr
    out, err = proc.communicate()
    # check for exit status for button clicked, 0 = OK 2 = Cancel
    if proc.returncode == 0:
        # user clicked OK
        return True
    if proc.returncode == 2:
        # user clicked cancel
        return False
    # if there is any other return print it
    else:
        print('Error: %s' % err)


def quit_application(bid):
    """quits apps using NSRunningApplication"""
    # use API to assign a variable for the running API so we can terminate it
    apps = NSRunningApplication.runningApplicationsWithBundleIdentifier_(bid)
    # API returns an array always, must iterate through it
    for app in apps:
        # terminate the app
        app.terminate()
        # if the app does not terminate in 3 seconds gracefully force it
        time.sleep(3)
        if not app.isTerminated():
            app.forceTerminate()


def force_quit_applicaiton(bid):
    """force an application to quit for emergency workflows"""
    # use API to assign a variable for the running API so we can FORCE terminate it
    apps = NSRunningApplication.runningApplicationsWithBundleIdentifier_(bid)
    # API returns an array always, must iterate through it
    for app in apps:
        # terminate the app
        app.forceTerminate()


def run_update_policy(event):
    """run the updater policy for the app"""
    # if you don't need to run an update policy, set to "false" to skip this
    if event == "false":
        pass
    # unix command list
    cmd = ['/usr/local/bin/jamf', 'policy', '-event', event]
    # execute the policy to the binary
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # grab stdout and stderr pipes and communicate them to the shell
    out, err = proc.communicate()
    # if we get a non zero response, print the error
    if proc.returncode != 0:
        print('Error: %s' % err)


def notify_on_completion():
    """notification that the patch is complete"""
    # probably do not need this, can most likely reuse prior dialog box function
    # this is just a place holder for now 
    pass


def run():
    """runs the workflow of the script"""
    # check to see if the app is not running, if it is not we are in luck we can update now!
    for app in APP_LIST:
        if not check_if_running(app):
            run_update_policy(UPDATE_POLICY)
            sys.exit(0)
    # check to see if we are forcing the app to quit first, and take action
    if FORCE_QUIT == 'true':
        force_quit_prompt(FORCEMSG)
        # loop through the bundle ID list
        for bid in APP_LIST:
            # force quit the app and force the update via jamf policy
            force_quit_applicaiton(bid)
            run_update_policy(UPDATE_POLICY)
            user_prompt(COMPLETE)
        # if we are using the force we can exit here
        sys.exit(0)
    # use the bundle ID or IDs from parameter 4 and iterate through them
    for bid in APP_LIST:
        # check if the app is running by bundle ID and we are choosing to prompt from parameter 5
        if check_if_running(bid) and PROMPT == 'true':
            # prompt the user
            answer = user_prompt(MESSAGE)
            # if they click OK, will return True value
            if answer:
                # quit the app, run the update, prompt to notify when complete
                quit_application(bid)
                run_update_policy(UPDATE_POLICY)
                user_prompt(COMPLETE)
            if not answer:
                # if they click "Cancel" we will exit
                sys.exit(0)
        # if we pass the option to not prompt, just quit the app
        if check_if_running(bid) and PROMPT == 'false':
            quit_application(bid)


# gotta have a main
if __name__=='__main__':
    run()

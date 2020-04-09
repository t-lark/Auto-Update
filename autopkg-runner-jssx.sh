#!/bin/sh
#mass patching by zackn9ne
#set your ENV HERE, set your RECIPIES, set your .plist or .json
ENV="corpname"

LOGFILE="/Users/$(whoami)/Desktop/Autopkgr-Overrides/logs/run-$ENV.log"
if [ -e "$LOGFILE" ]
      then
	echo "$LOGFILE Exists"
   else
	echo "Creating $LOGFILE"
	touch $LOGFILE
fi

exec 3>&1 4>&2
trap 'exec 2>&4 1>&3' 0 1 2 3
exec 1>$LOGFILE 2>&1

echo "started run: $(date)" 

/Library/AutoPkg/autopkg run -vv --post 'io.github.hjuutilainen.VirusTotalAnalyzer/VirusTotalAnalyzer' \
AU-Slack.jss \
AU-Zoom.jss \
"AU-Google Chrome.jss" \
AU-Firefox.jss \
AU-DriveFS.jss \
AU-Dropbox.jss \
local.jss.MicrosoftExcel365 \
local.jss.MicrosoftOutlook365 \
local.jss.MicrosoftPowerPoint365 \
local.jss.MicrosoftWord365 \
--prefs /Users/$(whoami)/Desktop/Autopkgr-Prefs/$ENV.json \
#--key STOP_IF_NO_JSS_UPLOAD=False

echo "finished run: $(date)"

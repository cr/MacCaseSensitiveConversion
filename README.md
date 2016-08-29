# The (new) case of Mac Case-Sensitivity

You probably know the story: Unix folks prefer their file systems case-sensitive, and the Mac OS
Installer lets you readily choose to do so. Life is good. Until you want to run software like Steam
(simple workaround) or Creative Cloud (painful partial workaround). So if you're tired of running
into the same old traps over and over, you might consider going back to a case-insensitive HFS+ startup
volume on your Mac.

Over the years there have been various hacks reported on the Internet, but every one I could find either
does not work on a recent Mac OS X "El Capitan" 10.11 installation or involves commercial software
like Carbon Copy Cloner or SuperDuper. However, if you're comfortable using the command line, there
is a way using just onboard, standard tools.

Since it took a very long weekend to figure out all the little obstacles, there might be value in
sharing the recipie that worked for me. In a nutshell:

 1. Resolve case-sensitivity naming conflicts
 2. Make a fresh TimeMachine backup
 3. Flip the backups's case-sensitivity flag
 4. Restore from the manipulated backup

This how-to is kept deliberately vague in areas that are sencond nature to Linux geeks. If you
have a hard time filling in the detail, you might want to get help from a good friend for this
endeavor anyway.

Before you start you might want to temporarily disable disk encryption. It will speed up the process
considerably and simplify a few of the steps.

## 1. Resolve case-sensitivity naming conflicts

A case-sensitive file system treats *Foo* and *foo* as distinct files, but you won't be able to have
both in the same directory on a case-insensitive file system. The moment TimeMachine restores a
conflicting file or directory that is already in place, it will bluntly abort the whole process with
a generic error message.

Hence you must clean your **complete** startup disk of any case conflicts. Unfortunately, this is a
laborious and manual process and I don't know of any tool that can do the work for you all the way.
However, this repository contains two python scripts that can (hopefully) spot the conflict candidates
for you, but dealing with them in a clever way is completely up to you.

What I did on my system was the following:

```bash
$ cd /
$ sudo <path_to_script>/casecheck.py
```

and it produced a nightmarishly long list of conflicts that had to be resolved one by one. In my case,
there were two areas that required special handling. Depending on what programs you use (I expected
lots of conflict potential for my photo database, but it looks like Aperture had it figured out), you
might need use their tooling to fix their databases and directories. In fact, where possible, you
should use those instead of manipulating files and directories on the command line directly.

This repo also contains the script ```casecheck_extra.py```, based on my mostly untested quick&dirty
implementation of Apple's *FastUnicodeCompare* algorithm that is being used in HFS+. The algorithm
skips certain "ignorable characters" that a regular Unicode string comparison would treat as different.
It didn't spot any leftovers on my disk, so it's there mostly for completeness. Feel free to use it
instead of ```casecheck.py``` and let me know how it goes.

### iTunes

Most conflicts occurred in my iTunes collection with capitalization of artists, albums and track names
being all over the place. I found it best to normalize capitalization through iTunes directly, and it
would move files appropriately (IIRC there's a pref for that, be sure to enable it), neatly taking care
of potential collisions. **Just make sure that you normalize both *Artist* and *Album Artist* for each
affected track**, or else the files might remain in conflicting artist directories.

### System files

Mac OS won't let you change anything the */System* folder (even root) from within the running system,
but on my disk there were several conflicts in that tree. To resolve these, you need to:

 1. Boot into the recovery system by pressing *Command-R* on the boot chime
 1. Open the Terminal app from the menu
 1. Resolve the conflicts on the startup volume mounted in /Volume/<your_disk_name>/System/...

Where possible I opted for deleting the older file and in case of my duplicate *Plugin* directory, I
moved the content from one over into the other and deleted the empty directory. So far I encountered
no issues with those decisions.

## 2. Make a fresh TimeMachine backup

It is very hard to overstate this:

**Make a fresh backup for this conversion.**

**Also, have a another backup ready that you won't touch until you're confident that the conversion
succeeded.**

You will need a reliable fallback in case you don't manage to clear every last one of the
case-sensitivity conflicts which you will only really find out when the restore fails – or not.

I trust you know how to create a fresh TimeMachine backup. The new backup disk needs to be
case-sensitive for TimeMachine to do its thing, and that's okay. Make sure no important folders
are on the exception list.

I suggest you let TimeMachine take just a single snapshot. If you end up with multiple snapshots
when the backup ran over night, for example, you may want to delete the older snapshots. The folder
`/Volumes/<BACKUPVOLUME>/Backups.backupdb/<COMPUTERNAME>/` contains all the snapshots encoded by
date plus one symbolic link pointing to the lastest one.

```bash
$ ls -l /Volumes/TimeMachiiine/Backups.backupdb/tin/
total 9
drwxr-xr-x@ 3 root  wheel  204 29 Aug 10:04 2016-08-29-100422/
drwxr-xr-x@ 3 root  wheel  204 29 Aug 11:05 2016-08-29-110526/
lrwxr-xr-x  1 root  wheel   17 29 Aug 11:08 Latest -> 2016-08-29-110526
```

Mind that my backup volume is called ``TimeMachiiine`` and my computer's name is ``tin``. Change
those accordingly to match your situation. Delete all snapshots but the latest one with something
like:

```bash
$ tmutil delete /Volumes/TimeMachiiine/Backups.backupdb/tin/2016-08-29-100422
```

That snapshot will be gone with all metadata intact.

**Never use ``rm -rf`` or anything like that to manipulate the backup. Things will likely break.**

## 3. Flip a TimeMachine backup's case-sensitivity flag

If you restore from this backup – even onto a case-insensitive volume –, the volume will end up
case-sensitive again. TimeMachine's restore process will recreate the volume according to the
backup's case-sensitivity marker. The good news: it doesn't care about the backup volume's
case-sensitivity at all. It just looks for an extended attribute inside the Backup folder.

So, even though the backup is on a case-sensitive volume, all you need to do is flip the
case-sensitivity switch like this:

```bash
$ sudo /System/Library/Extensions/TMSafetyNet.kext/Contents/Helpers/bypass \
    xattr -w com.apple.backupd.VolumeIsCaseSensitive 0 \
    /Volumes/TimeMachiiine/Backups.backupdb/tin/Latest/MacHD
```

Use the name of your Mac's startup volume instead of my ``MacHD``. Same goes for backup volume
and computer name.

In case you're curious: Since the backup folder is heavily ACL'd, you need to bypass them using
the ``bypass`` command like above which is shipped with the TimeMachine kernel extension.
It's present in older Mac OS versions, too, but the path may be slightly different. I'm sure
you can find it.

## 4. Restoring the backup

 1. Reboot you Mac
 1. Hold *Command-R* when the chime plays
 1. Select *Restore from TimeMachine Backup*
 1. Select the prepared backup volume
 1. Let it restore

The restore will only succeed if you managed to clear all case-sensitivity conflicts before
taking the backup. If you didn't, you will need to restore the other backup that you didn't
touch, and start over. Technically you can flip back the case-sensitivity flag of the
manipulated backup using the recovery's terminal, but you'll be very happy to have made
a backup that you didn't touch. Believe me.

But if the restore goes all the way to 100% without an error, and the system finally reboots,
go and have some fun with that crappy software that put you through all of this. ;)

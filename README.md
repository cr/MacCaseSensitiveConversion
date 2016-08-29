# The (new) case of Mac Case-Sensitivity

You probably know the story: Unix folks prefer their file systems case-sensitive, and the Mac OS
installer lets you readily choose to do so. Life is good. Until you want to run software like Steam
(simple workaround) or Creative Cloud (painful partial workaround). So if you're tired of running
into the same traps like me, you might consider going back to a case-insensitive HFS+ start volume
on you Mac.

Over the years there have been various hacks reported on the Internet, but every one I could find either
does not work on a recent Mac OS X "El Capitan" 10.11 installation or it involves commercial software
like Carbon Copy Cloner or SuperDuper. However, if you're comfortable using the Terminal.app, there
is a way using just onboard standard tools.

Since it took me a very long weekend to figure out all the little obstacles, there might be value in
sharing the recipie that worked for me. In a nutshell:

 1. Resolve case-sensitivity naming conflicts
 2. Make a fresh TimeMachine backup
 3. Flip the backups's case-sensitivity flag
 4. Restore from the backup

## 1. Resolve case-sensitivity naming conflicts

TBD

## 2. Make a fresh TimeMachine backup

It is very hard to overstate this:

**Make a fresh backup for this conversion.**

**Also, have a another backup ready that you won't touch until you're confident that the conversion
succeeded.**

You will need this fallback in case you don't manage to clear every last one of the case-sensitivity
conflicts which you will only really find out when the restore fails.

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
drwxr-xr-x@ 3 root  wheel  204 29 Aug 11:05 2016-08-29-100422/
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

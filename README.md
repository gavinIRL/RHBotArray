# RHBotArray

## Summary
A family of socket-controlled video game bots derived from https://github.com/gavinIRL/RHBot. See the parent repo for details on the game in question, etc. Each version is more autonomous with more features than the last. Goal is for fully autonomous bots.

## Current Status
### 7th June
Almost all end-of-level and event handling has now been completed and tested piecemeal. The current focus is now briefly swapping to incorporating the follower bot from the original RHBot family with all of the updates developed as part of RHBA. The intention is for the follower mode to be turned on and off similar to autolooting. In addition, the autonomous looting option developed for the map10 test will also be incorporated into the servers. The intent is to allow an autonomous client control 3 servers at some point allowing for single point of control autonomous party play. Also, all status updates beyond the most recent 3 updates will now be put into a separate file as the readme was getting to be too long.

### Rough plan as of 4th June 2021
1) Clean up and integrate autonomous looting into utils
2) Add tests for detection and handling of events
3) Add tests for endlevel handling
4) Implement endlevel handling, event handling, and autonomous looting into map10 bot
5) Test improved autonomous combat capabilities
6) Add handling for a party of bots
7) Add all other maps to catalogue
8) Add autonomous bounty mission acceptance and completion

## Versions
### Version Features
* Version 1 - Establishing basic chat server connection and functionality
* Version 2 - Changing client communication to be keystrokes sent by listener
* Version 3 - Executing sent keystrokes at server end
* Version 4 - Adding multiple server connections
* Version 5 - Adding time-delayed communications
* Version 6 - Adding support for mouse clicks
* Version 7 - Adding encryption
* Version 8 - Adding hotkey support, integrating RHBot functionality into client and server
* Version 9 - Update for wired switch connection, Tesseract experiments, regroup, autoloot, quest handling
* Version 10 - Loot identification, automatic sell and repair, delayed batch playback
* Version 11 - Fully autonomous bot with combat, looting, navigation, event handling
* Version 12 - Version 10 client-server upgraded with follower and auto-farloot capabilities
* Version 13 - Autonomous bounty mission accept and fulfillment

### Version Status
* Version 1 - Complete
* Version 2 - Complete
* Version 3 - Complete
* Version 4 - Complete
* Version 5 - Complete
* Version 6 - Complete
* Version 7 - Complete
* Version 8 - Complete
* Version 9 - Complete
* Version 10 - Complete
* Version 11 - In progress
* Version 12 - In progress
* Version 13 - Not Started

## Previous Status Updates
### 4th June
The past couple of weeks have mostly been focused initially at applying the required polish to v10 as planned, and more recently at assembling the required pieces for a fully autonomous bot. The 5 key functions of an autonomous bot are combat, looting, navigation, event handling, and end-of-level handling. Of these, the most difficult one (combat) has been initially tackled although most tests have been carried out to enable more complex revisions in the future. Looting has been thoroughly covered and can be considered to be fully completed bar some minor tidying up. Navigation has also been thoroughly carried out although requires some polish. Event handling is the final completely untouched topic and represents the least tested aspect. And finally end-of-level handling is lacking in progress but it is well understood what work is required to complete it. Based on current progress a basic but fully autonomous single-level bot should be ready for 13th June at the latest. The plan is to start gathering footage of the bots in the near future as proof of work and documenting progression.

### 23rd May 2021
The last week has been spent improving and fixing a lot of the features in Version 10 such as regroup. There have been ~15 tests of different features and ideas most of which have been implemented including a much faster keyboard input method. However a number of issues have been discovered and are being tackled mostly today. The plan is to have a fully polished Version 10 free of any bugs or annoyances which should be completed by the 25th at the very latest. Looking beyond that, I have put together a number of tests as part of the Version 10 progression which will become very useful for fully-autonomous botting. However the primary difficult in creating a fully autonomous bot is in the combat aspect of things much more so than the navigation and GUI handling, and therefore this will be the primary focus of Version 11.

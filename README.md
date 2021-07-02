# RHBotArray

## Summary
A family of socket-controlled video game bots derived from https://github.com/gavinIRL/RHBot. See the parent repo for details on the game in question, etc. Each version is more autonomous with more features than the last. Goal is for fully autonomous bots.

## Current Status
### 2nd July
The fully autonomous single-level bot has been completed and the initial upgrade package to improve profitability and robustness is currently underway. It has however been noticed that there are issues when running the bot on other PCs due to a memory leak related to screenshot grabbing. When a small screenshot is taken in the time that a big screenshot in a separate thread is underway but not complete then errors will cascade. Thread locking has merely shifted the problem and so has resource deallocation due to the main logic flow. Therefore a full rewrite of the flow is likely required. But either way a rewrite of the primary logic to allow for a universal map handler is required and therefore both tasks are to be undertaken at the same time. The primary goal for the next week is to finish the universal map handler and then start to add the required map navigation points to the database to enable running more maps. Beyond that the goal is to add bounty contract handling.

## Rough plan as of 2nd July 2021
1) Add ultra-robust autonomous map bot configurable for any map
2) Add all other maps to catalogue
3) Add autonomous bounty mission acceptance and completion
4) Add handling for a party of bots

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
* Version 12 - Version 10 client-server upgraded with follower and robustness upgrades
* Version 13 - Multi-level autonomous bot
* Version 14 - Autonomous bounty mission accept and fulfilment

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
Full list at https://github.com/gavinIRL/RHBotArray/blob/main/STATUS_UPDATES.txt
### 21st June
The autonomous effort ran into a snag in the past week due to getting stuck attempting to loot and also general moving around. Therefore two new more accurate methods have been developed to reduce the chances of getting stuck. Additionally, looting now occurs by moving in a diagonal manner which greatly reduces the time taken and also reduces probability of getting stuck. There is also a much more robust catch for inaccessible loot, with the attempt timeout dictated by the main loop rather than the looting loop as before. The current aim is fully finishing testing the end-level sequence and then incorporating it into the existing map10 bot, therefore the fully autonomous single-level bot ETA is now 27th June. However there will immediately be an upgrade campaign aimed at updating combat capabilities (especially target selection), catching/handling stuck bots, and also special event handling. Once that has been completed it will be on to enabling running of all other maps and multi-bot integration.

### 14th June
The past week has been spent upgrading the client and server to v12 with all of the speed and experimental upgrades from the v10/v11 tests. The planned date of June 13th for a single-level autonomous bot has passed due to a change in priorities. Now the plan is to proceed with the autonomnous efforts again and to now aim for 20th June for a fully autonomous single-level bot. Some other issues currently persist which need to be rectified in the near term such as the regroup function not opening the map correctly.

### 7th June
Almost all end-of-level and event handling has now been completed and tested piecemeal. The current focus is now briefly swapping to incorporating the follower bot from the original RHBot family with all of the updates developed as part of RHBA. The intention is for the follower mode to be turned on and off similar to autolooting. In addition, the autonomous looting option developed for the map10 test will also be incorporated into the servers. The intent is to allow an autonomous client control 3 servers at some point allowing for single point of control autonomous party play. Also, all status updates beyond the most recent 3 updates will now be put into a separate file as the readme was getting to be too long.

### 4th June
The past couple of weeks have mostly been focused initially at applying the required polish to v10 as planned, and more recently at assembling the required pieces for a fully autonomous bot. The 5 key functions of an autonomous bot are combat, looting, navigation, event handling, and end-of-level handling. Of these, the most difficult one (combat) has been initially tackled although most tests have been carried out to enable more complex revisions in the future. Looting has been thoroughly covered and can be considered to be fully completed bar some minor tidying up. Navigation has also been thoroughly carried out although requires some polish. Event handling is the final completely untouched topic and represents the least tested aspect. And finally end-of-level handling is lacking in progress but it is well understood what work is required to complete it. Based on current progress a basic but fully autonomous single-level bot should be ready for 13th June at the latest. The plan is to start gathering footage of the bots in the near future as proof of work and documenting progression.

### 23rd May 2021
The last week has been spent improving and fixing a lot of the features in Version 10 such as regroup. There have been ~15 tests of different features and ideas most of which have been implemented including a much faster keyboard input method. However a number of issues have been discovered and are being tackled mostly today. The plan is to have a fully polished Version 10 free of any bugs or annoyances which should be completed by the 25th at the very latest. Looking beyond that, I have put together a number of tests as part of the Version 10 progression which will become very useful for fully-autonomous botting. However the primary difficult in creating a fully autonomous bot is in the combat aspect of things much more so than the navigation and GUI handling, and therefore this will be the primary focus of Version 11.

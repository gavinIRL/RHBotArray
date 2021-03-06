# RHBotArray

## Summary
A family of socket-controlled video game bots derived from https://github.com/gavinIRL/RHBot. See the parent repo for details on the game in question, etc. Each version is more autonomous with more features than the last. Goal is for fully autonomous bots.

## Current Status
### 12th July
The map navigation points for 5 other levels have been added although require some fine tuning. In general the autonomous bot is now fully operational and only requires a map config file to work essentially. Other priorities have come to the fore and therefore the near term plan for this repo and project is to finish up the documentation of the project using video demonstrations of features and abilities of the bot, and then cleaning up the code to allow for a final release. There is no planned return to improve/extend the capabilities of the autonomous bot right now to the planned version 14 and beyond.

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
* Version 11 - Complete
* Version 12 - Complete
* Version 13 - In Progress
* Version 14 - Not Started

## Previous Status Updates 
Full list at https://github.com/gavinIRL/RHBotArray/blob/main/STATUS_UPDATES.txt
### 2nd July
The fully autonomous single-level bot has been completed and the initial upgrade package to improve profitability and robustness is currently underway. It has however been noticed that there are issues when running the bot on other PCs due to a memory leak related to screenshot grabbing. When a small screenshot is taken in the time that a big screenshot in a separate thread is underway but not complete then errors will cascade. Thread locking has merely shifted the problem and so has resource deallocation due to the main logic flow. Therefore a full rewrite of the flow is likely required. But either way a rewrite of the primary logic to allow for a universal map handler is required and therefore both tasks are to be undertaken at the same time. The primary goal for the next week is to finish the universal map handler and then start to add the required map navigation points to the database to enable running more maps. Beyond that the goal is to add bounty contract handling.

### 21st June
The autonomous effort ran into a snag in the past week due to getting stuck attempting to loot and also general moving around. Therefore two new more accurate methods have been developed to reduce the chances of getting stuck. Additionally, looting now occurs by moving in a diagonal manner which greatly reduces the time taken and also reduces probability of getting stuck. There is also a much more robust catch for inaccessible loot, with the attempt timeout dictated by the main loop rather than the looting loop as before. The current aim is fully finishing testing the end-level sequence and then incorporating it into the existing map10 bot, therefore the fully autonomous single-level bot ETA is now 27th June. However there will immediately be an upgrade campaign aimed at updating combat capabilities (especially target selection), catching/handling stuck bots, and also special event handling. Once that has been completed it will be on to enabling running of all other maps and multi-bot integration.

### 14th June
The past week has been spent upgrading the client and server to v12 with all of the speed and experimental upgrades from the v10/v11 tests. The planned date of June 13th for a single-level autonomous bot has passed due to a change in priorities. Now the plan is to proceed with the autonomnous efforts again and to now aim for 20th June for a fully autonomous single-level bot. Some other issues currently persist which need to be rectified in the near term such as the regroup function not opening the map correctly.

### 7th June
Almost all end-of-level and event handling has now been completed and tested piecemeal. The current focus is now briefly swapping to incorporating the follower bot from the original RHBot family with all of the updates developed as part of RHBA. The intention is for the follower mode to be turned on and off similar to autolooting. In addition, the autonomous looting option developed for the map10 test will also be incorporated into the servers. The intent is to allow an autonomous client control 3 servers at some point allowing for single point of control autonomous party play. Also, all status updates beyond the most recent 3 updates will now be put into a separate file as the readme was getting to be too long.

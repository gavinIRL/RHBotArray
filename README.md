# RHBotArray

## Summary
A family of socket-controlled video game bots derived from https://github.com/gavinIRL/RHBot. See the parent repo for details on the game in question, etc. Each version is more autonomous with more features than the last. Goal is for fully autonomous bots.

## Current Status
### 4th June
The past couple of weeks have mostly been focused initially at applying the required polish to v10 as planned, and more recently at assembling the required pieces for a fully autonomous bot. The 5 key functions of an autonomous bot are combat, looting, navigation, event handling, and end-of-level handling. Of these, the most difficult one (combat) has been initially tackled although most tests have been carried out to enable more complex revisions in the future. Looting has been thoroughly covered and can be considered to be fully completed bar some minor tidying up. Navigation has also been thoroughly carried out although requires some polish. Event handling is the final completely untouched topic and represents the least tested aspect. And finally end-of-level handling is lacking in progress but it is well understood what work is required to complete it. Based on current progress a basic but fully autonomous single-level bot should be ready for 13th June at the latest. The plan is to start gathering footage of the bots in the near future as proof of work and documenting progression. 


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
* Version 11 - Single-level autonomous bot with combat, looting, navigation, event handling
* Version 12 - Multiple-level autonomous bot
* Version 13 - Autonomous quest identification and progression

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
* Version 12 - Not Started
* Version 13 - Not Started

## Previous Status Updates
### 23rd May 2021
The last week has been spent improving and fixing a lot of the features in Version 10 such as regroup. There have been ~15 tests of different features and ideas most of which have been implemented including a much faster keyboard input method. However a number of issues have been discovered and are being tackled mostly today. The plan is to have a fully polished Version 10 free of any bugs or annoyances which should be completed by the 25th at the very latest. Looking beyond that, I have put together a number of tests as part of the Version 10 progression which will become very useful for fully-autonomous botting. However the primary difficult in creating a fully autonomous bot is in the combat aspect of things much more so than the navigation and GUI handling, and therefore this will be the primary focus of Version 11.

### 16th May 2021
Version 10 is now almost completed, the successful test code for the auto-sell-and-repair feature needs to be implemented into both server and client and then I can move on to Version 11. To recap on Version 10: a lot of lessons have been learned in particular approaches to identifying semi-standardised images i.e. images whereby you expect a portion of it to be the same periodically which you require. The time taken to complete Version 10 has been almost double the expected duration however this was due to exploring and eventually finding a much more efficient (over 100x faster) approach in comparison to the initial base plan. Looking forward to the next planned version I feel I have a much better way of developing some features in image identification. The near-term focus the next week will be to polish the features of Version 10 and include all of the required features for convenient fully-managed mtuli-bot gameplay. Note that all annoyances have been resolved.

### 10th May 2021
Version 9 has been completed and now moving on to Version 10 which has the intent of including the delayed batch recordings feature, and also the loot identification tests and auto-sell-and-repair. The regroup command has been successfully implemented and there has been a major step forward in bot accuracy thanks to Tesseract. The quest handler has been implemented also. For the most part there aren't really any pressing issues with the bot, most of the work in the near future is dedicated to adding additional bot capabilities rather than fixing issues and annoyances. The short-to-medium term (i.e. next 3-7 days) focus is on semi-automation of in-town and end-of-dungeon events, beyond that it will be more aimed at fully autonomous actions e.g. solo clear a full level, autonomously hand-in quests upon completion and find and accept new quests, etc.

### 8th May 2021
Version 9 has resolved a number of the problems (along with a network switch for <1ms command latency) however there are still quite a few left. The experiments with Tesseract have shown a much better way of detecting certain features and events moving forward especially once I move more into scripted events. The main priorities in the near term are implementing the "regroup" command, and identifying (and eventually automatically selling) disposable loot at the end of a level.

### 6th May 2021
With the completion of Version 8 it has become clear that this method of botting is definitely viable despite having a few minor quirks and issues. Levelling with 2 sidekick bots has been much much faster than solo thereby increasing the power compared to solo rather than being a distraction. However there are some minor annoyances that need to be addressed.

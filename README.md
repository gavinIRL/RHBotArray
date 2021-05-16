# RHBotArray

## Summary
A family of socket-controlled video game bots derived from https://github.com/gavinIRL/RHBot. See the parent repo for details on the game in question, etc. Each version is more autonomous with more features than the last. Goal is for fully autonomous bots.

## Current Status and Thoughts
### 16th May 2021
Version 10 is now almost completed, the successful test code for the auto-sell-and-repair feature needs to be implemented into both server and client and then I can move on to Version 11. To recap on Version 10: a lot of lessons have been learned in particular approaches to identifying semi-standardised images i.e. images whereby you expect a portion of it to be the same periodically which you require. The time taken to complete Version 10 has been almost double the expected duration however this was due to exploring and eventually finding a much more efficient (over 100x faster) approach in comparison to the initial base plan. Looking forward to the next planned version I feel I have a much better way of developing some features in image identification. The near-term focus the next week will be to polish the features of Version 10 and include all of the required features for convenient fully-managed mtuli-bot gameplay. Note that all annoyances have been resolved.

### 10th May 2021
Version 9 has been completed and now moving on to Version 10 which has the intent of including the delayed batch recordings feature, and also the loot identification tests and auto-sell-and-repair. The regroup command has been successfully implemented and there has been a major step forward in bot accuracy thanks to Tesseract. The quest handler has been implemented also. For the most part there aren't really any pressing issues with the bot, most of the work in the near future is dedicated to adding additional bot capabilities rather than fixing issues and annoyances. The short-to-medium term (i.e. next 3-7 days) focus is on semi-automation of in-town and end-of-dungeon events, beyond that it will be more aimed at fully autonomous actions e.g. solo clear a full level, autonomously hand-in quests upon completion and find and accept new quests, etc.

### 8th May 2021
Version 9 has resolved a number of the problems (along with a network switch for <1ms command latency) however there are still quite a few left. The experiments with Tesseract have shown a much better way of detecting certain features and events moving forward especially once I move more into scripted events. The main priorities in the near term are implementing the "regroup" command, and identifying (and eventually automatically selling) disposable loot at the end of a level.

### 6th May 2021
With the completion of Version 8 it has become clear that this method of botting is definitely viable despite having a few minor quirks and issues. Levelling with 2 sidekick bots has been much much faster than solo thereby increasing the power compared to solo rather than being a distraction. However there are some minor annoyances that need to be addressed.

### List of current problems and annoyances
* None for now

### Proposed solutions to problems and annoyances
* None for now

## Current Status
* Version 1 - Complete
* Version 2 - Complete
* Version 3 - Complete
* Version 4 - Complete
* Version 5 - Complete
* Version 6 - Complete
* Version 7 - Complete
* Version 8 - Complete
* Version 9 - Complete
* Version 10 - In Progress
* Version 11 - Not Started
* Version 12 - Not Started
* Version 13 - Not Started

## Versions
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
* Version 11 - Far loot finding and navigation, enemy nametag detection
* Version 12 - Quest identification and seeking, Contract mission identification and logging
* Version 13 - Automatic combat, automatic level navigation

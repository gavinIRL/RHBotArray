# RHBotArray

## Summary
This is currently the testing ground for the socketed control of bots from https://github.com/gavinIRL/RHBot.

## Current Status and Thoughts
### 10th May 2021
Version 9 has been completed and now moving on to Version 10 which has the intent of including the delayed batch recordings feature, and also the loot identification tests and auto-sell-and-repair. The regroup command has been successfully implemented and there has been a major step forward in bot accuracy thanks to Tesseract. The quest handler has been implemented also. For the most part there aren't really any pressing issues with the bot, most of the work in the near future is dedicated to adding additional bot capabilities rather than fixing issues and annoyances. The short-to-medium term (i.e. next 3-7 days) focus is on semi-automation of in-town and end-of-dungeon events, beyond that it will be more aimed at fully autonomous actions e.g. solo clear a full level, autonomously hand-in quests upon completion and find and accept new quests, etc.

### 8th May 2021
Version 9 has resolved a number of the problems (along with a network switch for <1ms command latency) however there are still quite a few left. The experiments with Tesseract have shown a much better way of detecting certain features and events moving forward especially once I move more into scripted events. The main priorities in the near term are implementing the "regroup" command, and identifying (and eventually automatically selling) disposable loot at the end of a level.

### 6th May 2021
With the completion of Version 8 it has become clear that this method of botting is definitely viable despite having a few minor quirks and issues. Levelling with 2 sidekick bots has been much much faster than solo thereby increasing the power compared to solo rather than being a distraction. However there are some minor annoyances that need to be addressed.

### List of current problems and annoyances
* When in town and completing or starting questlines there is an inconsistency between the player actions and the bot actions which snowballs if an issue arises, in particular if delay is enabled. To maintain a natural-looking group, delayed movement is required. UPDATE: it has been observed that part of the reason for this is that events (text readout, loading) happen a lot quicker on the main PC compared to the other, even though the "slower" PCs actually have faster storage and better processors. The difference is actually ~5 times for certain events and therefore not negligible.

* There is a not-insignificant amount of time spending selling the useless loot that each bot has collected at the end of each level which has resulted in a tendency to wait multiple levels and then sell all at once.

### Proposed solutions to problems and annoyances
* In-town actions (i.e. "delay" mode) could be transmitted as a block of actions with recorded spacing rather than either time-delayed or instant. This should hopefully reduce the issues arising from communication lag. The addition of a "quest handler" button has also helped immensely so far.

* Developing an automated loot-selling hotkey to speed up end-of-level actions would save even more time.

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
* Version 11 - Far loot finding and navigation, enemy nametag detection and targeting
* Version 12 - Quest identification and seeking, Contract mission identification and logging

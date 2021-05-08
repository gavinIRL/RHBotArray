# RHBotArray

## Summary
This is currently the testing ground for the socketed control of bots from https://github.com/gavinIRL/RHBot.

## Current Status and Thoughts
### 8th May 2021
Version 9 has resolved a number of the problems (along with a network switch for <1ms command latency) however there are still quite a few left. The experiments with Tesseract have shown a much better way of detecting certain features and events moving forward especially once I move more into scripted events. The main priorities in the near term are implementing the "regroup" command, and identifying (and eventually automatically selling) disposable loot at the end of a level.

### 6th May 2021
With the completion of Version 8 it has become clear that this method of botting is definitely viable despite having a few minor quirks and issues. Levelling with 2 sidekick bots has been much much faster than solo thereby increasing the power compared to solo rather than being a distraction. However there are some minor annoyances that need to be addressed.

### List of current problems and annoyances
* The different characters will inevitably become separated resulting in spending a small amount of time at the end of every zone walking into corners to regroup.
* When in town and completing or starting questlines there is an inconsistency between the player actions and the bot actions which snowballs if an issue arises, in particular if delay is enabled. UPDATE: it has been observed that part of the reason for this is that events (text readout, loading) happen a lot quicker on the main PC compared to the other, even though the "slower" PCs actually have faster storage and better processors. The difference is actually ~5 times for certain events and therefore not negligible.
* There is a not-insignificant amount of time spending selling the useless loot that each bot has collected at the end of each level which has resulted in a tendency to wait multiple levels and then sell all at once.

### Proposed solutions to problems and annoyances
* Adding a "regroup" button to the client which will either sent an instruction to regroup at the main player location, or else send the required instructions from the client itself.
* In-town actions (i.e. "delay" mode) could be transmitted as a block of actions with recorded spacing rather than either time-delayed or instant. This should hopefully reduce the issues arising from communication lag.
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
* Version 9 - In Progress

## Versions
* Version 1 - Establishing basic chat server connection and functionality
* Version 2 - Changing client communication to be keystrokes sent by listener
* Version 3 - Executing sent keystrokes at server end
* Version 4 - Adding multiple server connections
* Version 5 - Adding time-delayed communications
* Version 6 - Adding support for mouse clicks
* Version 7 - Adding encryption
* Version 8 - Adding hotkey support, integrating RHBot functionality into client and server
* Version 9 - Update for wired switch connection, Tesseract experiments, regroup, autoloot
* Version 10 - Loot identification, automatic sell and repair
* Version 11 - Quest identification, Contract mission identification and logging

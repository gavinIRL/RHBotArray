# RHBotArray

## Summary
This is currently the testing ground for the socketed control of bots from https://github.com/gavinIRL/RHBot.

## Current Status and Thoughts
With the completion of Version 8 it has become clear that this method of botting is definitely viable despite having a few minor quirks and issues. Levelling with 2 sidekick bots has been much much faster than solo thereby increasing the power compared to solo rather than being a distraction. However there are some minor annoyances that need to be addressed.

### List of current problems and annoyances
* The different characters will inevitably become separated resulting in spending a small amount of time at the end of every zone walking into corners to regroup.
* When in town and completing or starting questlines there is an inconsistency between the player actions and the bot actions which snowballs if an issue arises, in particular if delay is enabled.
* Due to small amounts of lag or delay, commands can sometimes be sent on top of each other therefore not being carried out correctly. Potentially the primary cause of the previous point. 
* There is a not-insignificant amount of time spending selling the useless loot that each bot has collected at the end of each level which has resulted in a tendency to wait multiple levels and then sell all at once.

### Proposed solutions to problems and annoyances
* Adding a "regroup" button to the client which will either sent an instruction to regroup at the main player location, or else send the required instructions from the client itself.
* In-town actions (i.e. "delay" mode) could be transmitted as a block of actions with recorded spacing rather than either time-delayed or instant. This should hopefully reduce the issues arising from communication lag.
* Swapping from communicating using a wifi network into using a local wired network specifically for sending bot commands would eliminate lag and potentially solve most of the problems with inconsistency.
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

## Versions
* Version 1 - Establishing basic chat server connection and functionality
* Version 2 - Changing client communication to be keystrokes sent by listener
* Version 3 - Executing sent keystrokes at server end
* Version 4 - Adding multiple server connections
* Version 5 - Adding time-delayed communications
* Version 6 - Adding support for mouse clicks
* Version 7 - Adding encryption
* Version 8 - Adding hotkey support, integrating RHBot functionality into client and server

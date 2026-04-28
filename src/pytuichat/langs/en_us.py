
language: dict[str, str] = {

    "mrkSending": "📨",
    "mrkSent": "✉️",
    "mrkTimeout": "❌",
    "mrkUnread": "📬",
    "mrkRead": "✅",

    "lblTitle": "PyTUI Chat",
    "lblSubTitle": "Terminal messaging!",
    "lblCreateNewChat": """Enter the ID of the chat (usernames, case sensitive).
For multiple users, separate with a comma. For example: \"UserA\", or
\"UserA, UserB\"""",

    "btnBack": "Back",
    "btnExit": "Exit",

    "pptInteractive": "PyTUI Chat (Interactive)",
    "pptSingular": "PyTUI Chat (Singular)",
    "pptConsole": "Enter [a command, \"help\" or \"exit\"]\n> ",
    "pptExiting": "Good Bye!",
    "pptEndReq": "End Request",
    "pptUnknown": "UNKNOWN: ",

    "errNotStarted": "ERR: The Inbox program does not seem to be started",

    "txtHelpCli": """
Welcome to PyTUIChat! Here is a list of commands and their usage. Arguments in brackets are required, while arguments in parentheses may be omitted.
\n\nexit: ends the program
\n\nstart: starts the inbox if it is not already running.
\n\nstop: stops the inbox running without exiting the program.
\n\nlist or ls: lists all active chats.
\n\nread [title] (number): displays number messages from the chat specified by title. Defaults to 10 messages if the number is unspecified, or all messages if the chat has less than number messages.
\n\nsend [title] [text]: sends a message with the provided text to all participants in the chat specified by title.
\n\ncreate [userlist]: creates a chat with all the users in userlist. userlist should contain the usernames of all desired chat participants, separated by commas with no spaces.
\n\noptions (option) (new value): if used with no arguments, prints your current options. Otherwise, changes the value of the given option to the new value. Use “options help” for a list of options and their possible values.
        """,

    "settingHelpCli": """
Use "options" to view your current options.
\n\nUse "options 24hour [value]" to switch between 12-hour and 24-hour time. Value may be "on" or "off".
\n\nUse "options nicks [value]" to switch between showing usernames and chosen nicknames. Value may be "on" or "off".
        """,

    "txtHelpTui": """
Welcome to PyTUIChat! You can navigate using tab to cycle through buttons and enter to activate them, or you can interact with buttons using your mouse. Most keybinds are displayed at the bottom of the Terminal User Interface, so check those for a reminder. As for what they do…
\n\nQuit: exits the TUI without closing the inbox, allowing you to continue receiving messages in the background.
\n\nKill: exits the TUI and closes the inbox, meaning you will not receive messages until you reactivate the inbox.
\n\nBack: returns you to the screen you most recently left. For example, using this while viewing a chat would return you to the screen where you view a summary of all your chats.
\n\nNew chat: opens a screen that prompts you for the usernames of people you wish to create a chat with, separated by commas with no spaces. Press enter to confirm chat creation.
\n\nOptions: opens a screen that allows you to change how the TUI looks.
\n\nHelp: you are here!
\n\nPalette: opens a screen with several commands to use.
        """,
    
    "settingTwentyFourOff": "24-Hour: off",
    "settingTwentyFourOn": "24-Hour: on",
    "settingNicknamesOff": "Nicknames: off",
    "settingNicknamesOn": "Nicknames: on",
}
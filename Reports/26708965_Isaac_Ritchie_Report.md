CIS 1702 - CW2 Group Project - Task 2 / API

-- Individual Report --
name: Isaac D Ritchie 
student no: 26708965


Sub-Team Members:
Isaac Ritchie
Caileb Cook
William Ellison

Sub-Team Timeline:
Weeks 1-3 (UI Team)
Weeks 4-6 (API Team)



Project Development Documentation:

9/12/2025
Update Note:I am the host of the Git Repository. I have split the main branch into 2 separate 
branches for UI and API development and began to astablish a set repository format.
-
Planning Pseudocode: (UI-system)

START 
api_info = API information
    FUNCTION (ui_menu)
    display_width = max length of menu items +3 empty spaces for border separation
    PRINT "+" + "-" x display_width + "+"
    FOR information api_info
        PRINT "|" + (3 empty spaces for boarder) then information + Description via f string
        PRINT new line before any extra info to keep menu formatted
        PRINT new line then "+" + "-" x display_width + "+"
    RETURN
END

19/12/2025
Update Node: Implimented and pushed functinal code for menu output in a seperate UI Staging branch.
Further Development Note: Convert current API functions to return data, not just print within the function.


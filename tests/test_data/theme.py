################################################################
#
#   Humerus - UI Themes
#
################################################################

from gui.albow.theme import root, Theme

MenuButton = Theme("MenuButton")
MenuButton.font = (24, "VeraBd.ttf")
MenuButton.fg_color = (255, 255, 255)
MenuButton.highlight_color = (0, 128, 0)
MenuButton.bg_color = None
MenuButton.enabled_bg_color = None
MenuButton.disabled_bg_color = None
MenuButton.highlight_bg_color = None
MenuButton.margin = 0
MenuButton.border_width = 0

MenuTitle = Theme("MenuTitle")
MenuTitle.font = (48, "VeraBd.ttf")
MenuTitle.fg_color = (255, 255, 255)

ChangeDot = Theme("ChangeDot")
ChangeDot.fg_color = (255, 0, 0)
ChangeDot.fill_color = (0, 0, 0)
ChangeDot.margin = 2
ChangeDot.frame_width = 1

root.MenuButton = MenuButton
root.MenuTitle = MenuTitle
root.ChangeDot = ChangeDot

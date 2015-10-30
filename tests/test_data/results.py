import cocos
from cocos.director import director
import mainmenu
from gamelib import Inventory
from vfx import *

class Results(cocos.layer.Layer):
    def __init__(self, dic = ['test', 1, 'Score: ', 3]):
        super(Results, self).__init__()
        (w,h) = director.get_window_size()
        high_score = Inventory.data['userdata']['HighScore']
        i = 0
        for key in xrange(len(dic)/2):
            keymsg = cocos.text.Label(dic[i],
                        font_name='Nokia Cellphone',
                         font_size=18,
                         anchor_x='right', anchor_y='center')
            keymsg.position = w/2, h - (i+5)*10

            #check if this is highscore
            if dic[i] == "Score: " and dic[i+1] > high_score:
                Inventory.data['userdata']['HighScore'] = dic[i+1]
                Inventory.save()
                msg_layer = MessageLayer()
                msg_layer.show_message("New High Score!!")
                self.add(msg_layer)

            valuemsg =  cocos.text.Label(str(dic[i+1]),
                        font_name='Nokia Cellphone',
                         font_size=18,
                         anchor_x='left', anchor_y='center')
            valuemsg.position = w/2, h - (i+5)*10

            i += 2
            self.add(keymsg)
            self.add(valuemsg)

        menu = cocos.menu.Menu()
        #configure the menu font.
        menu.font_item['font_name'] = 'Nokia Cellphone'
        menu.font_item['font_size'] = 22
        menu.font_item_selected['font_name'] = 'Nokia Cellphone'
        menu.font_item_selected['font_size'] = 30

        l = []
        l.append(cocos.menu.MenuItem("NEXT", self.nextClicked))
        menu.create_menu(l, None, cocos.menu.zoom_in(), cocos.menu.shake())
        menu.position = 0, -h/4
        self.add(menu)

    def goHome(self):
        # We create a new layer, an instance of HelloWorld
        hello_layer = mainmenu.MainMenu() #gameplay.GamePlay()

        # A scene that contains the layer hello_layer
        main_scene = cocos.scene.Scene (hello_layer)

        # And now, start the application, starting with main_scene
        cocos.director.director.run (main_scene)

    def nextClicked(self):
        if not self.are_actions_running():
            self.do(cocos.actions.Delay(1) + cocos.actions.CallFunc(self.goHome))
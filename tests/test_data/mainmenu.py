import cocos
from powerups import PowerUpIndicator
from vfx import *
from cocos.director import director
import cocos.scenes.transitions
from gamelib import Inventory
import gameplay

class MainMenu(cocos.layer.Layer):
    def __init__(self):
        super(MainMenu, self).__init__()

        #play the bg
        music = pyglet.resource.media('Variable-Joshua_H-10424_hifi.mp3', streaming=True)
        player = pyglet.media.Player()
        player.eos_action = pyglet.media.Player.EOS_LOOP
        player.queue(music)
        player.play()

        self.infoShown = -1
        (w, h) = director.get_window_size()

        title = createLabel('BITRIS', 32, (255, 255, 255, 255))
        title.position = w/2, h-32
        self.add(title)

        heading = createLabel('POWERUPS', 15, (0, 0, 255, 255))
        heading.position = w/2, h-150
        self.add(heading)

        self.cycles = createLabel('<>' + str(Inventory.data['userdata']['CpuCycles']), 15, (0, 0, 255, 255))
        self.cycles.element.anchor_x = 'left'
        self.cycles.element.anchor_y = 'top'
        self.cycles.position = 5, h-7
        self.add(self.cycles)

        cl = cocos.layer.ColorLayer(255, 255, 255, 255, 70, 20)
        cl.position = 0, h-20
        self.add(cl)
        self.add(self.cycles)

        #create the menu for powerups.
        menu = cocos.menu.Menu()
        positions = []
        itemSize = w/3
        self.arr = [ 'AutoByte', 'BitAndOrder', 'ByteBlast' ]
        self.counters = []
        for i in xrange(3):
            positions.append((w/2-itemSize/2 + i*itemSize/2, h/2-itemSize))
        i = 0
        for position in positions:
            pup = Inventory.data['gameconfig'][self.arr[i]]
            costLabel = createLabel("<>" + str(pup['cost']), 15, (0, 0, 255, 255))
            costLabel.position = position[0]-itemSize/2 + i*itemSize/2, h/2 - itemSize/4
            self.add(costLabel)

            #add the counter display label.
            pupCount = Inventory.data['userdata'][self.arr[i]]
            self.counters.append(createLabel(str(pupCount), 15))
            self.counters[i].position = position[0]-itemSize/4 + i*itemSize/2, h/2+itemSize/2
            self.add(self.counters[i], 2)
            i += 1

        #add position for the play button.
        positions.append((w/2, itemSize/2))

        #show highscore
        high_score = Inventory.data['userdata']['HighScore']
        label = createLabel("HighScore: " + str(high_score), 10, (255, 255, 255, 255))
        label.position = w/2, h-70
        self.add(label)

        #pup = Inventory.data['gameconfig'][self.arr[self.infoShown]]
        self.infoLabel = createLabel('', 15, (0, 0, 255, 255))
        self.infoLabel.position = w/2, h/2 - itemSize/2
        self.add(self.infoLabel)

        layout_func = cocos.menu.fixedPositionMenuLayout(positions)
        l = []
        l.append(cocos.menu.ImageMenuItem('AutoByte.png', self.abClicked))
        l.append(cocos.menu.ImageMenuItem('BitAndOrder.png', self.baoClicked))
        l.append(cocos.menu.ImageMenuItem('ByteBlast.png', self.bbClicked))
        l.append(cocos.menu.MenuItem('PLAY', self.playClicked))

        #configure the menu font.
        menu.font_item['font_name'] = 'Nokia Cellphone'
        menu.font_item['font_size'] = 22
        menu.font_item_selected['font_name'] = 'Nokia Cellphone'
        menu.font_item_selected['font_size'] = 30

        menu.create_menu(l, None, cocos.menu.zoom_out(), cocos.menu.shake(), layout_func)
        menu.scale = 2
        menu.position = 0, h/2
        self.add(menu)

    def updateInfoLabel(self):
        pup = Inventory.data['gameconfig'][self.arr[self.infoShown]]
        self.infoLabel.element.text = pup['info']
        pupCount = Inventory.data['userdata'][self.arr[self.infoShown]]
        self.counters[self.infoShown].element.text = str(pupCount)
        self.cycles.element.text = '<>' + str(Inventory.data['userdata']['CpuCycles'])

    def buyPowerUp(self, pname):
        #if the user has enough cycles in inventory
        money = Inventory.data['userdata']['CpuCycles']
        cost = Inventory.data['gameconfig'][pname]['cost']
        if money >= cost:
            Inventory.data['userdata'][pname] += 1
            Inventory.data['userdata']['CpuCycles'] -= cost


    def playClicked(self):
        #save the inventory to ensure the buy's are not lost
        Inventory.save()

        game = gameplay.GamePlay()
        # A scene that contains the layer hello_layer
        main_scene = cocos.scene.Scene (game)
        # And now, start the application, starting with main_scene
        director.replace(main_scene)

    def showTip(self):
        (w, h) = director.get_window_size()
        label = createLabel('Click again to buy.', 10, (255, 255, 255, 0))
        label.position = w/2, h-170
        label.do(cocos.actions.FadeIn(0.5) + cocos.actions.Delay(1) +
                 cocos.actions.FadeOut(0.5) + cocos.actions.CallFunc(label.kill))
        self.add(label)

    def abClicked(self):
        #the user already knows that he is buying this. now buy.
        if self.infoShown == 0:
            self.buyPowerUp(self.arr[self.infoShown])
        else:
            self.showTip()
        self.infoShown = 0
        self.updateInfoLabel()

    def baoClicked(self):
        if self.infoShown == 1:
            self.buyPowerUp(self.arr[self.infoShown])
        else:
            self.showTip()
        self.infoShown = 1
        self.updateInfoLabel()

    def bbClicked(self):
        if self.infoShown == 2:
            self.buyPowerUp(self.arr[self.infoShown])
        else:
            self.showTip()
        self.infoShown = 2
        self.updateInfoLabel()
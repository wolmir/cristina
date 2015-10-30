import cocos
from cocos.scenes.transitions import *
import cocos.particle_systems
import cocos.actions
import cocos.sprite
from cocos.director import director
import powerups
import pattern
import results
from vfx import *
from powerups import PowerUpIndicator
import gamelib
import data

class GamePlay(cocos.layer.Layer):
    is_event_handler = True  #: enable director.window events
    BitPatternSize = 8
    def __init__(self):
        super(GamePlay, self).__init__()

        self.sound_effects = {}
        self.sound_effects['click'] = pyglet.media.load(data.filepath('click.wav'), streaming=False)
        self.sound_effects['error'] = pyglet.media.load(data.filepath('error.wav'), streaming=False)
        self.sound_effects['explode'] = pyglet.media.load(data.filepath('explode.wav'), streaming=False)
        self.sound_effects['powerup'] = pyglet.media.load(data.filepath('powerup.wav'), streaming=False)
        self.sound_effects['ok'] = pyglet.media.load(data.filepath('success.wav'), streaming=False)

        # a cocos.text.Label is a wrapper of pyglet.text.Label
        # with the benefit of being a cocosnode
        self.label = createLabel('Hello, World!', 20, (255, 255, 255, 255))
        (w,h) = director.get_window_size()
        self.w = w
        self.h = h
        self.label.position = w/2, h-20
        self.add(self.label)
        self.bitSize = w/GamePlay.BitPatternSize

        #score display
        self.scoreText = createLabel('Score: 8888', 10, (255, 255, 255, 255))
        self.scoreText.element.anchor_x = 'left'
        self.scoreText.position = 5, h-10
        self.add(self.scoreText)

        self.multiplierText = createLabel('x1', 10, (255, 255, 255, 255))
        self.multiplierText.element.anchor_x = 'left'
        self.multiplierText.position = 5, h-25
        self.add(self.multiplierText)

        self.resetGame()

        #we start with 0 as starting point.
        self.currentTarget = 0
        self.label.element.text = "Return: " + str(self.currentTarget)

        cl = cocos.layer.ColorLayer(255, 255, 255, 255, self.w, 72)
        self.add(cl)

        self.powerMenu = []
        self.powerMenu.append(PowerUpIndicator('AutoByte.png', self.activate_powerup))
        self.powerMenu.append(PowerUpIndicator('BitAndOrder.png', self.activate_powerup))
        self.powerMenu.append(PowerUpIndicator('ByteBlast.png', self.activate_powerup))
        itemSize = self.w/3

        for i in xrange(3):
            self.powerMenu[i].scale = 0.8
            self.powerMenu[i].position = itemSize/2 + i*itemSize, 72/2
            self.powerMenu[i].count = gamelib.Inventory.data['userdata'][self.powerMenu[i].file_name.replace(".png", "")]
            self.add(self.powerMenu[i])
        self.schedule(self.update)

    def updateScoreText(self):
        self.scoreText.element.text = "Score: " + str(self.score)
        self.multiplierText.element.text = "x" + str(self.multiplier)

    def resetGame(self):
        self.currentTarget = 0
        self.stackHeight = 72
        self.multiplier = 1
        self.successCounter = 0
        self.isAnimating = False
        self.score = 0
        self.startMutation = False
        self.isGameOver = False
        self.genLimit = 10
        self.delayTime = 1
        self.maxMultiplier = 1
        self.updateScoreText()
        self.generateNextPattern()

    def generateNextPattern(self):
        if self.isGameOver:
            return

        newValue = random.randrange(0, self.genLimit)
        #ensure we dont' see the same number one after the other.
        if newValue == self.currentTarget:
            newValue += 1
        self.currentTarget = newValue

        self.label.element.text = "Return: " + str(self.currentTarget)
        self.bitpattern = pattern.BitPattern(GamePlay.BitPatternSize)

        if self.startMutation and random.choice([0, 1]):
            self.bitpattern.shuffleBits()

            #show a message that indicates that a powerup has been launched.
            mutationmsg = createLabel("Bit Mutation Detected", 18, (255, 0, 0, 255))
            mutationmsg.position = self.w/2, self.h/2 + 72
            mutationmsg.do(cocos.actions.Blink(2, 2) +
                          cocos.actions.FadeOut(1) + cocos.actions.CallFunc(mutationmsg.kill))
            self.add(mutationmsg, 1)

        #keep showing zero till the user gets' one thing right.
        if self.successCounter == 0:
            self.currentTarget = 0
            self.label.element.text = "Return: " + str(self.currentTarget)
            hint = createLabel('Click to Toggle', 10, (255, 255, 255, 255));
            hint.position = self.w/2, self.bitSize + 5
            self.bitpattern.add(hint)

        self.add(self.bitpattern, 0)
        move = cocos.actions.MoveBy((0, -self.bitSize), 0.5)
        delay = cocos.actions.Delay(self.delayTime)
        seq = cocos.actions.sequence(move, delay)
        self.bitpattern.do(cocos.actions.Repeat(seq))

    def isPatternFailed(self):
        return self.currentTarget & self.bitpattern.getValue() != self.currentTarget

    def isPatternFinished(self):
        return self.currentTarget ^ self.bitpattern.getValue() == 0

    def addWhiteLine(self):
        #add the white block at the bottom of screen.
        (w,h) = director.get_window_size()
        cl = cocos.layer.ColorLayer(255,255,255,255, w, self.bitSize)
        cl.position = 0, self.stackHeight
        #cl.do(cocos.actions.FadeIn(0.2))
        self.add(cl, 1)
        self.stackHeight += self.bitSize

    def handleError(self, node):
        node.do(cocos.actions.FadeOut(0.5) + cocos.actions.CallFuncS(self.remove))
        self.addWhiteLine()
        self.isAnimating = False
        self.generateNextPattern()
        self.multiplier = 1
        self.updateScoreText()

    def handleSuccess(self, node = None):
        self.isAnimating = False
        self.generateNextPattern()

        if node:
            node.do(cocos.actions.FadeOut(0.5) + cocos.actions.CallFuncS(self.remove))
        # successcounter
        self.multiplier += 1

        #track the max multiplier that the user had achieved during gameplay.
        if self.maxMultiplier < self.multiplier:
            self.maxMultiplier = self.multiplier

        #increment the genLimit by 10 every time the successCounter goes up.
        if(self.successCounter % 5 == 0):
            self.genLimit += 10

        #decrement the time for every 10 correct answers.
        if(self.successCounter % 10 == 0):
            #decrease the hold time by 0.1 after every 10 successful attempts.
            self.delayTime -= 0.05
            if self.delayTime < 0.5:
                self.delayTime = 0.5
            #start the mutation gameplay as well.
            self.startMutation = True
        self.updateScoreText()

    def showMessage(self, msg, color=(0, 0, 0, 255), isError = True):
        """
        This function is useful for showing the message on screen. If the isError value is
        True, we call the handleError once the FadeIn happens, Else we call handleSuccess.
        """
        #We want to prevent any updates going on while we are showing the message.
        self.isAnimating = True
        #create a white layer that fades in
        (w,h) = director.get_window_size()
        cl = cocos.layer.ColorLayer(255,255,255,0, w, self.bitSize)
        cl.position = 0, self.bitpattern.y
        if isError == True:
            cl.do(cocos.actions.FadeIn(0.2) + cocos.actions.Delay(1.5) + cocos.actions.CallFuncS(self.handleError))
        else:
            cl.do(cocos.actions.FadeIn(0.2) + cocos.actions.Delay(1.5) + cocos.actions.CallFuncS(self.handleSuccess))

        #text label on top of white text.
        errormsg = createLabel(msg, 32, color)
        errormsg.position = w/2, self.bitSize/2-5
        errormsg.do(cocos.actions.Delay(0.2) + cocos.actions.Blink(2, 1) + cocos.actions.FadeOut(0.5))
        cl.add(errormsg)
        self.add(cl)

    def showResults(self):
        print self.multiplier
        print self.score
        print self.successCounter
        r = results.Results(['Multiplier: ', self.maxMultiplier,
                             'Score: ', self.score,
                             'Success: ', self.successCounter,
                             '---------', '--------',
                             'CpuCycles: <>', self.successCounter * self.maxMultiplier])
        s = cocos.scene.Scene(r)
        director.replace(TurnOffTilesTransition(s))

    def updateInventory(self):
        for pup in self.powerMenu:
            gamelib.Inventory.data['userdata'][pup.file_name.replace(".png","")] = pup.count
        gamelib.Inventory.data['userdata']['CpuCycles'] += self.successCounter * self.maxMultiplier
        gamelib.Inventory.save()

    def handleGameOver(self):
        print "GameOver"
        self.isGameOver = True
        self.bitpattern.stop()
        self.unschedule(self.update)

        #set the user data values for the inventory.
        self.updateInventory()

        errormsg = createLabel("Fatal: too many errors")
        errormsg.position = self.w/2, self.h/2
        self.add(errormsg, 2)
        errormsg = createLabel("Program Terminated")
        errormsg.position = self.w/2, self.h/2-25
        self.add(errormsg, 2)
        errormsg.do(cocos.actions.Delay(0.2) + cocos.actions.Blink(2, 1))
        self.do(cocos.actions.Delay(1.5) + cocos.actions.CallFunc(self.showResults))

    def update(self, dt):
        #if we are animating something we do not want the update checks.
        if self.isAnimating:
            return

        #if the required number cannot be achieved
        if self.isPatternFailed():
            #remove the current pattern
            self.bitpattern.stop()
            self.bitpattern.do(cocos.actions.Delay(0.3) + cocos.actions.CallFuncS(self.remove))
            self.showMessage("ERROR", (255, 0, 0, 255))
            self.sound_effects['error'].play()
            return

        # when the pattern has reached bottom of screen.
        if self.bitpattern.y <= self.stackHeight:
            self.bitpattern.stop()
            self.bitpattern.do(cocos.actions.Delay(0.3) + cocos.actions.CallFuncS(self.remove))
            self.showMessage("TIMEOUT!!", (255, 0, 0, 255))
            self.sound_effects['error'].play()


        #the white lines have reached top of screen. It's game over :(
        if(self.stackHeight > self.h - self.bitSize):
            self.handleGameOver()

        elif self.isPatternFinished():
            #increment the score
            self.score += self.multiplier * (self.BitPatternSize - self.bitpattern.getNumBitsOn())
            self.successCounter += 1

            #remove the old bit pattern.
            self.bitpattern.stop()
            self.bitpattern.do(cocos.actions.Delay(0.3) + cocos.actions.CallFuncS(self.remove))
            self.showMessage("SUCCESS!", (0, 255, 0, 255), False)
            self.sound_effects['ok'].play()
            #add a couple of explosions for effect.
            explosion = SuccessExplosion()
            explosion.position = (self.bitSize, self.bitpattern.y + self.bitSize/2)
            self.add(explosion)
            explosion = SuccessExplosion()
            explosion.position = (self.w - self.bitSize, self.bitpattern.y + self.bitSize/2)
            self.add(explosion)

    def update_text(self, x, y):
        self.label.element.text = "" + str(x)  + "," + str(y)

    def activate_powerup(self, fname):
        msg = "AutoByte Launched"
        self.isAnimating = True
        if fname == "AutoByte.png":
            msg = "AutoByte Launched"
            powerups.AutoByte(self.bitpattern, self.currentTarget)

        elif fname == "BitAndOrder.png":
            msg = "BitAndOrder Launched"
            self.bitpattern.do(cocos.actions.Delay(2) +
                               cocos.actions.CallFuncS(powerups.BitAndOrder))

        elif fname == "ByteBlast.png":
            msg = "ByteBlater Launched"
            self.multiplier = 1
            self.bitpattern.do(cocos.actions.Delay(2) +
                               cocos.actions.CallFuncS(powerups.ByteBlaster))

        #show a message that indicates that a powerup has been launched.
        powerupmsg = createLabel(msg, 18, (0, 0, 255, 255))
        powerupmsg.position = self.w/2, self.h/2 + 72
        powerupmsg.do(cocos.actions.Blink(2, 1) +
                      cocos.actions.FadeOut(0.5) + cocos.actions.CallFunc(powerupmsg.kill))
        self.add(powerupmsg, 3)


    def on_mouse_motion(self, sx, sy, dx, dy):
        #handle the mouse over effect.
        for item in self.powerMenu:
            if item.contains(sx, sy):
                item.scale = 0.9
            else:
                item.scale = 0.8

    def on_mouse_press(self, x, y, buttons, modifiers):
        #debug stuff
        #self.score = 10
        #self.showResults()
        #end debug stuff

        if self.isGameOver or self.isAnimating:
            pass
        else:
            #handle the mouse click to activate the powerup.
            for item in self.powerMenu:
                if item.contains(x, y):
                    self.sound_effects['powerup'].play()
                    item.activate()

            self.posx, self.posy = director.get_virtual_coordinates(x, y)
            #make the bits toggle when the mouse is clicked.
            if self.bitpattern.handleClick(x, y):
                self.sound_effects['click'].play()
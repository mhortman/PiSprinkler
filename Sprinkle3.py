import time

import main
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import OptionProperty, NumericProperty, ListProperty, \
        BooleanProperty
from kivy.lang import Builder
from kivy.clock import Clock
import requests

playbackList = []


class MainWindow(Screen):

    vert_slider_val = NumericProperty(1.0)
    base_slider_val = NumericProperty(1.0)
    water = BooleanProperty(False)
    record = BooleanProperty(False)
    cur_base_angle = 0
    cur_vert_angle = 0
    now_record = False
    water_power = False
    startRecordTime = time.time()

    def record(self, record_on):
        print("Record: ", record_on)
        if record_on:
            record = 'on'
            playbackList.clear()
            start_record_time = time.time()
        else:
            record = 'off'
            self.playbackClear()

    def playbackClear(self):
        global playbackList
        clean_playbackList = []
        sumBase = 0
        sumVert = 0
        whichSecond  = 0
        numberInSecond = 0
        print('i am playbacklist: ')
        print(playbackList)
        print('en of playback')
        for idx in range(len(playbackList)):
            playbackValue = playbackList[idx]
            if round(playbackValue[2]) > whichSecond:
                if (sumVert> 0  or sumVert<0):
                    clean_playbackList.append(('V', int(sumVert/numberInSecond),whichSecond))
                if (sumBase > 0 or sumBase < 0):
                    clean_playbackList.append(('B', int(sumBase/numberInSecond), whichSecond))
                numberInSecond = 0
                sumBase = 0
                sumVert = 0
                whichSecond = round(playbackValue[2])

            numberInSecond += 1
            if playbackValue[0] == 'V':
                print("Vert")
                sumVert = sumVert+ playbackValue[1]
            elif playbackValue[0] == 'B':
                print("Base")
                sumBase = sumBase + playbackValue[1]
            else:
                print("XXXX INVALID")
        # global playbackList
        playbackList.clear()
        playbackList = clean_playbackList.copy()


    def showRecord(self, record_on):
        print("Playback ", playbackList)

    def add_to_playback(self,code, val):
        playbackList.append((code, val, round(time.time() - self.startRecordTime, 2)))

    def water(self, power_on):
        print("Power on: ", power_on)
        if power_on:
            water = 'on'
        else:
            self.add_to_playback('W', 0.0)
            water = 'off'

        try:
            response = requests.post("http://192.168.1.47:80/valve/", water, "/", timeout=2)
            print("Valve Response ", response)
        except requests.exceptions.Timeout:
            print("Timeout")
        except requests.exceptions.RequestException as e:
            # catastrophic error. bail.
            raise SystemExit(e)

    def base_turn(self, value):
        angle_diff = value - self.cur_base_angle
        if (angle_diff >0 or angle_diff< 0):
            self.add_to_playback('B', int(value))
        self.cur_base_angle = value

    def vert_turn(self, value):
        angle_diff = value - self.cur_vert_angle
        if (angle_diff >0 or angle_diff< 0):
            self.add_to_playback('V', int(value))
        self.cur_vert_angle = value


class SecondWindow(Screen):

    def play(self):
        print("Playback ", playbackList)

    def load_playback(self):
        self.play_text.text = playbackList
        print("Load Play Text ", playbackList)

class WindowManager(ScreenManager):
    pass

kv = Builder.load_string('''
WindowManager:
    MainWindow:
    SecondWindow:

<MainWindow>:
    name: "main"

    GridLayout:
        cols: 2
        size_hint: 1, None
        height: 44 * 5

        GridLayout:
            cols: 2

            Label:
                text: 'Vertical Control'
            Slider:
                id: vert_val
                min: 0 
                max: 90
                value: 0.0
                step: 1.0
                orientation: 'vertical'
                on_touch_move: if self.collide_point(*args[1].pos): root.vert_turn(self.value)
            Label:
                text: 'Base'
            Slider:
                id: base_val
                min: 0 
                max: 180
                value: 0.0
                step: 1.0
                on_touch_move: if self.collide_point(*args[1].pos): root.base_turn(self.value)


        AnchorLayout:
            GridLayout:
                cols: 1
                size_hint: None, None
                size: self.minimum_size
                ToggleButton:
                    size_hint: None, None
                    size: 100, 44
                    text: 'Water'
                    on_state: root.water(self.state == 'down')
                ToggleButton:
                    size_hint: None, None
                    size: 100, 44
                    text: 'Record'
                    on_state: root.record(self.state == 'down')
                Button:
                    size_hint: None, None
                    size: 100, 44
                    text: 'Show Record'
                    on_state: root.showRecord(self.state == 'down')
                Button:
                    size_hint: None, None
                    size: 100, 44
                    text: "Playback"
                    on_release:
                        app.root.current = "second"
                        root.manager.transition.direction = "left"


<SecondWindow>:
    name: "second"

    GridLayout:
        cols: 2
        size_hint: 1, None
        height: 44 * 5

        GridLayout:
            cols: 2

            TextInput:
                id: play_text
                multiline: True
            Button:
                size_hint: None, None
                size: 100, 44
                text: 'Load'
                on_release: root.load_playback()
            Button:
                size_hint: None, None
                size: 100, 44
                text: 'Play'
                on_release: root.play()
            Button:
                text: "Go Back"
                on_release:
                    app.root.current = "main"
                    root.manager.transition.direction = "right"

''')






class MyMainApp(App):

    def build(self):
        return kv


if __name__ == "__main__":
    MyMainApp().run()


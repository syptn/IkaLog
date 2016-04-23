#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import os
import os.path
import traceback
import threading
import shlex
import subprocess
import tempfile

from ikalog.utils import *

class GstRec(object):

    def start_rec(self):
        self.lock.acquire()
        IkaUtils.dprint('%s: start gstreamer recording.' % self.__class__.__name__)
        self.gst_tempfile = tempfile.mkstemp(dir=self.output_dir)[1]
        self.gst_proc = subprocess.Popen(
            args=shlex.split(self.gst_command),stdout=open(self.gst_tempfile,'w'))
        self.game_context = None
        self.filename = os.path.join(self.output_dir, '%s_unknown.avi')
        self.lock.release()

    def stop_rec(self):
        self.lock.acquire()
        IkaUtils.dprint('%s: stop gstreamer recording.' % self.__class__.__name__)
        if self.gst_proc:
            self.gst_proc.terminate()
            time_str = time.strftime("%Y%m%d_%H%M", time.localtime())
            os.rename(self.gst_tempfile,self.filename % time_str)
        self.gst_proc = None
        self.game_context = None
        self.lock.release()

    def create_output_filename_temp(self, context):
        map = IkaUtils.map2text(context['game']['map'], unknown='マップ不明')
        rule = IkaUtils.rule2text(context['game']['rule'], unknown='ルール不明')
        won = IkaUtils.getWinLoseText(
            context['game']['won'], win_text='win', lose_text='lose')
        newname = os.path.join(self.output_dir, '%s_' + '%s_%s_%s.avi' % (map, rule, won))
        return newname

    def on_lobby_matched(self, context):
        self.start_rec()

    def on_game_individual_result(self, context):
        self.filename = self.create_output_filename_temp(context)

    def on_game_reset(self, context):
        self.stop_rec()

    def __init__(self, gst_command=None, output_dir=None, debug=False):
        self.lock = threading.Lock()
        self.gst_command = gst_command
        self.output_dir = output_dir
        self.debug = debug
        self.game_context = None

if __name__ == "__main__":
    from datetime import datetime
    import time
    class Dummy(object): pass
    context = {
        'game': {
            'map': Dummy(),
            'rule': Dummy(),
            'won': True,
            'timestamp': datetime.now(),
        }
    }
    context['game']['map'].id_ = 'arowana'
    context['game']['rule'].id_ = 'nawabari'

    gst = GstRec(gst_command='gst-launch-1.0 -q videotestsrc ! videoconvert ! fdsink', output_dir='/tmp')

    gst.on_lobby_matched(context)
    time.sleep(1)
    gst.on_game_individual_result(context)
    gst.on_game_reset(context)


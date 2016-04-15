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
    def terminate_gst(self, gst_proc):
        def sub():
            try:
                gst_proc.wait(timeout=600)
            except:
                gst_proc.terminate()
        return sub

    def start_rec(self):
        self.gst_tempfile = tempfile.mkstemp(dir=self.output_dir)[1]
        self.gst_proc = subprocess.Popen(args=shlex.split(self.gst_command),stdout=open(self.gst_tempfile,'w'))
        thread = threading.Thread(target=self.terminate_gst(self.gst_proc))
        thread.start()

    def stop_rec(self, filename):
        if self.gst_proc:
            self.gst_proc.terminate()
            os.rename(self.gst_tempfile,filename)
        self.gst_proc = None

    def create_output_filename(self, context):
        map = IkaUtils.map2text(context['game']['map'], unknown='マップ不明')
        rule = IkaUtils.rule2text(context['game']['rule'], unknown='ルール不明')
        won = IkaUtils.getWinLoseText(
            context['game']['won'], win_text='win', lose_text='lose')

        time_str = time.strftime("%Y%m%d_%H%M", time.localtime())
        newname = os.path.join(self.output_dir, '%s_%s_%s_%s.avi' % (time_str, map, rule, won))

        return newname

    def on_lobby_matched(self, context):
        IkaUtils.dprint('start gstreamer recording.')
        self.start_rec()

    def on_game_individual_result(self, context):
        IkaUtils.dprint('stop gstreamer recording.')
        self.stop_rec(self.create_output_filename(context))

    def on_game_reset(self, context):
        IkaUtils.dprint('abort gstreamer recording.')
        self.stop_rec(self.create_output_filename(context))

    def __init__(self, gst_command=None, output_dir=None):
        self.gst_command = gst_command
        self.output_dir = output_dir


# -*- coding:gb18030 -*-

import time
import BigWorld
from bwdebug import EXCEHOOK_MSG

class FishingEngine:

	_SPT = 1.0/60					# second per tick，1/60相当于1秒最多刷新60次

	def __init__( self, target ):
		self._target = target
		self._lastTick = 0
		self._tickCBID = 0

	def start( self ):
		self._lastTick = time.time()
		self._startTicking()

	def stop( self ):
		self._stopTicking()

	def _tick( self ):
		now = time.time()
		dt = now - self._lastTick
		if dt < self._SPT:
			self._tickCBID = BigWorld.callback(self._SPT - dt, self._tick)
		else:
			self._lastTick = now
			try:
				self._target.onTick(dt)
			except:
				EXCEHOOK_MSG("From FishingEngine:")
			self._tickCBID = BigWorld.callback(0, self._tick)

	def _startTicking( self ):
		self._stopTicking()
		self._tickCBID = BigWorld.callback(0, self._tick)

	def _stopTicking( self ):
		if self._tickCBID:
			BigWorld.cancelCallback( self._tickCBID )
			self._tickCBID = 0

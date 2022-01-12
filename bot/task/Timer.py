# -*- coding: utf-8 -*-

import time
import threading

from .utils import bwdebug

gbTIndex = 0
gbTimerMap = {}

ADD_LOCK = threading.Lock()
DEL_LOCK = threading.Lock()


class Timer(threading.Thread):

	def __init__( self, start, interval, callback, stoppedCallback = None ):
		threading.Thread.__init__(self)
		self._start = start
		self._interval = interval
		self._callback = callback
		self._interrupt = False
		self._stoppedCB = stoppedCallback
		self.setDaemon(True)
		#debug
		self._actualDuration = 0
		#debug end

	def run( self ):
		#debug
		start = time.time()
		#debug end

		bwdebug.DEBUG_MSG("Timer start at thread %s" % threading.currentThread().getName())

		if self._start > 0:
			time.sleep(self._start)
			if not self._interrupt:
				self.callback()
		else:
			self.callback()

		if not self._interrupt and self._interval > 0:
			time.sleep(self._interval)
			while not self._interrupt:
				self.callback()
				time.sleep(self._interval)

		#debug
		self._actualDuration = time.time() - start
		#debug end

		if self._stoppedCB:
			self._stoppedCB(self)

	def callback(self):
		if self._callback:
			self._callback()

	def cancel( self ):
		self._interrupt = True

	@property
	def actualDuration( self ):
		return self._actualDuration


def addTimer( start, interval, callback ):
	global ADD_LOCK
	ADD_LOCK.acquire()

	this_index = None
	try:
		global gbTIndex
		global gbTimerMap

		timer = Timer(start, interval, callback, onTimerStopped)
		timer.start()

		gbTIndex += 1
		gbTimerMap[gbTIndex] = timer
		this_index = gbTIndex

	finally:
		ADD_LOCK.release()

	return this_index


def cancelTimer( timerID ):
	global DEL_LOCK
	DEL_LOCK.acquire()

	try:
		global gbTimerMap
		if timerID in gbTimerMap:
			gbTimerMap[timerID].cancel()
			del gbTimerMap[timerID]
		else:
			bwdebug.DEBUG_MSG("<TimerDebug> Unknown timer %i" % timerID)

	finally:
		DEL_LOCK.release()


def onTimerStopped( timer ):
	global DEL_LOCK
	DEL_LOCK.acquire()

	try:
		global gbTimerMap
		tid = None

		for idx, tm in gbTimerMap.iteritems():
			if tm is timer:
				tid = idx
				break

		if tid is not None:
			del gbTimerMap[tid]

	finally:
		DEL_LOCK.release()


def cancelAllTimers():
	global DEL_LOCK
	DEL_LOCK.acquire()

	try:
		global gbTimerMap
		for timer in gbTimerMap.itervalues():
			timer.cancel()
		gbTimerMap.clear()

	finally:
		DEL_LOCK.release()


def timers():
	global gbTimerMap
	return gbTimerMap.copy()

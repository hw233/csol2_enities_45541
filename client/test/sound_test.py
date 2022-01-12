# -*- coding: gb18030 -*-


from Sound import soundMgr
import csol
import os
import BigWorld

def playTestSound( name ):
	"""
	"""
	if name == "":
		return
	name = name.replace("/","\\")
	mp3file = os.getcwd()+"\\mp3\\"+name+".mp3"
	wavfile = os.getcwd()+"\\mp3\\"+name+".wav"
	
	musicfile = ""
	
	if os.path.exists( mp3file ):
		musicfile = mp3file
	elif os.path.exists( wavfile ):
		musicfile = wavfile
	else:
		print "not find any file!!!"
		print "no file:",mp3file
		print "no file:",wavfile
		if BigWorld.player():
			BigWorld.player().soundPriority = 0
		return
	musicfile = musicfile.replace("\\","/")

	print "musicfile path:",musicfile

	csol.CreateProcess("pmp3.exe %s"%musicfile)
	if BigWorld.player():
		BigWorld.player().soundPriority = 0



def playVocality( name, pyModel ):
	"""
	"""
	playTestSound( name )


def playTestUI( name ):
	"""
	"""
	playTestSound( name )

def play2DSound( name, isGossipVoice = False ):
	"""
	"""
	playTestSound( name )
	
def playVoice( name ):
	"""
	"""
	playTestSound( name )
	
def switchVoice( name ):
	"""
	"""
	playTestSound( name )
	
def playMusic( name ):
	"""
	"""
	playTestSound( name )


def switchMusic( name ):
	"""
	"""
	playTestSound( name )

soundMgr.play2DSound 	= play2DSound
soundMgr.playVoice	 	= playVoice
soundMgr.switchVoice 	= switchVoice
soundMgr.playMusic	 	= playMusic
soundMgr.switchMusic 	= switchMusic
soundMgr.playVocality 	= playVocality
soundMgr.playUI 		= playTestUI
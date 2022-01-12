# -*- coding: gb18030 -*-
import os
import shutil

sourceDir = "E:/love3/datas"
targetDir = "F:\\pp"  #windows平台下用\\


def getDatasPath():
	#返回path.xml中配置的datas文件夹路径
	import ResMgr
	sect = ResMgr.openSection("../paths.xml")
	for k, v in sect.items():
		for k1, v1 in v.items():
			if v1.asString.endswith("datas"):
				return v1.asString
		

def copyDirs(sourceDir, targetDir):
    for f in os.listdir(sourceDir):
        sourceF = os.path.join(sourceDir, f)
        targetF = os.path.join(targetDir, f)
        if os.path.isdir(getDatasPath() + "/" + sourceF):
            if not os.path.exists(targetDir):
                os.makedirs(targetDir)
            if not os.path.exists(targetF):
                os.makedirs(targetF)
            copyDirs(sourceF, targetF)

def copyFiles(sourceDir, targetDir):
    for f in os.listdir(sourceDir):
        sourceF = os.path.join(sourceDir, f)
        targetF = os.path.join(targetDir, f)
        if os.path.isfile(getDatasPath() + "/" + sourceF):
            if not os.path.exists(targetDir):
                os.makedirs(targetDir)
            if not os.path.exists(targetF) or (os.path.exists(targetF) and (os.path.getsize(targetF) != os.path.getsize(getDatasPath() + "/" + sourceF))):
                open(targetF, "wb").write(open(getDatasPath() + "/" + sourceF, "rb").read())
        if os.path.isdir(getDatasPath() + "/" + sourceF):
            copyFiles(sourceF, targetF)
"""
def xcopyFiles(sc, ds):
	os.chdir(sc)
	for root, dirs, files in os.walk("."):
		newpath = os.path.join(ds, root)
		if not os.path.isdir(newpath):
			os.makedirs(newpath)
		if root[0:2] == ".\\" or root[0:2] == "./":
			root = root[2:]
		elif root == ".":
			root = ""
		for name in files:
			inf = os.path.join(sc, root, name)
			ouf = os.path.join(ds, root, name)
			shutil.copyfile(inf, ouf)
"""		



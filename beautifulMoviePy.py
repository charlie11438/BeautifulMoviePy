import sys
from PyQt5.QtWidgets import QDialog, QApplication,QFileDialog,QMessageBox
from GUI import Ui_BeautifulMoviePy
from discretefft import takeLoud
from moviepy.editor import *
from moviepy.audio.fx.all import volumex
import threading
import re

class AppWindow(QDialog):
	def __init__(self):
		super().__init__()
		self.ui = Ui_BeautifulMoviePy()
		self.ui.setupUi(self)
		self.show()
		self.ui.Source.clicked.connect(self.sourcePath)
		self.ui.target.clicked.connect(self.targetPath)
		self.ui.toMP4.clicked.connect(self.to_mp4)
		self.ui.toGIF.clicked.connect(self.to_gif)
	def sourcePath(self):
		path,fileType = QFileDialog.getOpenFileName(self,"choose source file","C:/")
		self.ui.SourcePath.setText(path)
	def targetPath(self):
		path,fileType = QFileDialog.getSaveFileName(self,"choose target file","C:/")
		self.ui.OutputPath.setText(path)
	def subClipListGenerate(self,sourceClip,partsRowSplit):
		VideoClip = []
		for i in range(len(partsRowSplit)):
			start,end = partsRowSplit[i].split('~')
			print(start,end)
			VideoClip.append(sourceClip.subclip(start,end))
		print("generateSuccess")
		return VideoClip		
	def concateSubClip(self,sourceClip,partsRowSplit):
		VideoClip = self.subClipListGenerate(sourceClip,partsRowSplit)
		concatAll = concatenate_videoclips(VideoClip)
		return concatAll
	def seperateSubClip(self,sourceClip,partsRowSplit):
		VideoClip = self.subClipListGenerate(sourceClip,partsRowSplit)
		return VideoClip		

	def to_mp4_child(self):
		try:
			p = True
			print(self.ui.SourcePath.toPlainText())
			sourceClip = VideoFileClip(self.ui.SourcePath.toPlainText())
			start = self.ui.startTimes.toPlainText()
			stop = self.ui.endTimes.toPlainText()
			if self.ui.startOption.isChecked() and self.ui.endOption.isChecked():
				sourceClip = sourceClip.subclip(start,stop)
			if self.ui.startOption.isChecked():
				sourceClip = sourceClip.subclip(start,sourceClip.duration)
			if self.ui.endOption.isChecked():
				sourceClip = sourceClip.subclip("00:00:00",stop)
			if self.ui.fftOption.isChecked():
				sourceClip = takeLoud(sourceClip)
			if self.ui.IncreaseV.isChecked():
				increase = int(self.ui.increaseInput.toPlainText())
				audio_clip = sourceClip.audio
				new_audio_clip = volumex(audio_clip,increase)
				sourceClip.set_audio(new_audio_clip)
			elif self.ui.DecreaseV.isChecked():
				decrease = int(self.ui.decreaseInput.toPlainText())
				audio_clip = sourceClip.audio
				new_audio_clip = volumex(audio_clip,1/decrease)
				sourceClip.set_audio(new_audio_clip)
			if self.ui.subclip_concat.isChecked() and not self.ui.subclip_seperate.isChecked():
				parts = self.ui.subclipText.toPlainText()
				partsRowSplit = parts.split('\n')
				sourceClip = self.concateSubClip(sourceClip,partsRowSplit)
			elif self.ui.subclip_seperate.isChecked() and not self.ui.generateSerial.isChecked():
				p = False
				parts = self.ui.subclipText.toPlainText()
				partsRowSplit = parts.split('\n')
				fileName = self.ui.seperateText.toPlainText()
				fileNameSplit = fileName.split('\n')
				fileNameList = []
				currentDirAll = self.ui.OutputPath.toPlainText()
				currentDir = re.sub('[a-zA-z0-9]+[.][a-zA-z0-9]+','',currentDirAll)
				print(currentDir)
				for i in fileNameSplit:
					fileNameList.append(currentDir+i)
				VideoSeperateClip = self.seperateSubClip(sourceClip,partsRowSplit)
			elif self.ui.subclip_seperate.isChecked() and self.ui.generateSerial.isChecked():
				p = False
				parts = self.ui.subclipText.toPlainText()
				partsRowSplit = parts.split('\n')
				fileNameList = []
				currentDirAll = self.ui.OutputPath.toPlainText()
				currentDir = re.sub('[a-zA-z0-9]+[.][a-zA-z0-9]+','',currentDirAll)
				print(currentDir)
				for i in range(1,len(partsRowSplit)+1):
					fileNameList.append(currentDir+str(i)+".mp4")
				VideoSeperateClip = self.seperateSubClip(sourceClip,partsRowSplit)			
			if p:
				sourceClip.write_videofile(self.ui.OutputPath.toPlainText())
				self.ui.status.setText("success")
			else:
				print(fileNameList)
				print(VideoSeperateClip)
				for i,j in zip(fileNameList,VideoSeperateClip):
					j.write_videofile(i)
				self.ui.status.setText("success")
		except Exception as e:
			print(e)
			self.ui.status.setText("Error:"+str(e))


	def to_gif_child(self):
		try:
			sourceClip = VideoFileClip(self.ui.SourcePath.toPlainText())
			start = int(self.ui.startTimes.toPlainText()) if self.ui.startTimes.toPlainText() else ""
			stop = int(self.ui.endTimes.toPlainText()) if self.ui.endTimes.toPlainText() else ""
			if self.ui.startOption.isChecked() and self.ui.endOption.isChecked():
				sourceClip = sourceClip.subclip(start,stop)
			if self.ui.startOption.isChecked():
				sourceClip = sourceClip.subclip(start,sourceClip.duration)
			if self.ui.endOption.isChecked():
				sourceClip = sourceClip.subclip(0,stop)
			sourceClip.write_gif(self.ui.OutputPath.toPlainText())
			self.ui.status.setText("success")
		except Exception as e:
			print(e)
			self.ui.status.setText("Error:"+str(e))

	def to_mp4(self):
		self.ui.status.setText("transforming...............")
		self.mp4_thread = threading.Thread(target=self.to_mp4_child)
		self.mp4_thread.setDaemon(True)
		self.mp4_thread.start()
	def to_gif(self):
		self.ui.status.setText("transforming...............")
		self.gif_thread = threading.Thread(target=self.to_gif_child)
		self.gif_thread.setDaemon(True)
		self.gif_thread.start()

if __name__ == "__main__":
	app = QApplication(sys.argv)
	w = AppWindow()
	w.show()
	sys.exit(app.exec_())
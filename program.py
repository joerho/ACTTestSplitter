from pdf2image import convert_from_path
import pytesseract
from PIL import Image

from PyPDF4 import PdfFileReader,PdfFileWriter,PdfFileMerger
from reportlab.pdfgen import canvas
import sys
import os
import re

#python3 program.py test.pdf cover.pdf [page ranges]
CONST_OUTDIR = '/Users/joerho/Desktop/pyPDF/ACT/Subject Separated'
CONST_NUM_SECTIONS = 4
CONST_SECTION_MAP = {1:'E', 2:'M', 3:'R' , 4:'S'}
CONST_ENGLISH = '/Users/joerho/Desktop/pyPDF/Test Covers/english.png'
CONST_MATH = '/Users/joerho/Desktop/pyPDF/Test Covers/math.png'
CONST_READING = '/Users/joerho/Desktop/pyPDF/Test Covers/reading.png'
CONST_SCIENCE = '/Users/joerho/Desktop/pyPDF/Test Covers/science.png'


def main(argv):
	print("Parsing command line arguments...")
	parsedArgv = checkArgv(argv)
	print(parsedArgv)
	print("\n\n")

	testPath = parsedArgv[0]
	pageRanges = parsedArgv[1]
	testNameNum = getTestName(parsedArgv[0])
	outputDirs = prepareOutputDirectory(testNameNum[0])

	splitPages(testNameNum, testPath, pageRanges, outputDirs)


def splitPages(testNameNum, testPath, pageRanges, outputDirs):
	temp = 1
	key = 1
	for bookmark in pageRanges:
		f = open(testPath, 'rb')
		pdf = PdfFileReader(f)
		pdfWriter = PdfFileWriter()
		
		#add watermark to original cover
		origCover = pdf.getPage(0)
		newCover = addWaterMark(origCover, key)

		#put new cover on the front
		pdfWriter.addPage(newCover)

		for page in range(temp, bookmark):
			pdfWriter.addPage(pdf.getPage(page))

		outputFileName = os.path.join(outputDirs[1], '{} {} {}.pdf'
			.format(testNameNum[1], testNameNum[0], CONST_SECTION_MAP[key]))
		with open(outputFileName, 'wb') as out:
			pdfWriter.write(out)
		temp = bookmark
		key += 1

	f.close()

def checkArgv(argv):
	testPath = argv[0]
	pageRanges = argv[1]

	try:
		t = open(testPath, 'rb')
	except Exception as e:
		print("The test pdf does not exist.")

	t.close()

	pageArr = checkPageRanges(pageRanges)

	return [testPath, pageArr]


def checkPageRanges(pageRanges):
	pageArr = pageRanges.split(',')
	try:
		pageArr = [int(x) for x in pageArr]
	except:
		print("Each value of page range must be an int.")

	if isPositive(pageArr) == False:
		print("Why would you put in a negative number..?")
		sys.exit()

	if isSorted(pageArr) == False:
		print("Page range has to be sorted.")
		sys.exit()

	if len(pageArr) != CONST_NUM_SECTIONS:
		print("Page range must be a length of {}".format(CONST_NUM_SECTIONS))
		sys.exit()

	return pageArr

def isPositive(pageArr):
	for x in pageArr:
		if x <= 0:
			return False

	return True

def isSorted(pageArr):
	temp = pageArr[0]
	for x in pageArr[1:]:
		if x < temp:
			return False
		else:
			temp = x

	return True

def getTestName(testPath):
	path, testName = os.path.split(testPath)
	arr = testName.split(" ")
	testNum = re.search('\(([^)]+)', arr[-1]).group(1)
	arr = [''.join(arr[:-1]), testNum]

	return arr

def prepareOutputDirectory(testName):
	if not os.path.exists(CONST_OUTDIR):
		os.makedirs(CONST_OUTDIR)

	testDirPath = os.path.join(CONST_OUTDIR, testName)
	if not os.path.exists(testDirPath):
		os.makedirs(testDirPath)

	individualPath = os.path.join(testDirPath, "Individual Sections")
	if not os.path.exists(individualPath):
		os.makedirs(individualPath)

	return [testDirPath, individualPath]

def addWaterMark(origCover, key):
	c = canvas.Canvas('watermark.pdf')
	if key == 1:
		c.drawImage(CONST_ENGLISH, 190, 220)
	elif key == 2:
		c.drawImage(CONST_MATH, 220, 220)
	elif key == 3:
		c.drawImage(CONST_READING, 190, 220)
	elif key == 4:
		c.drawImage(CONST_SCIENCE, 190, 220)

	c.save()
	watermark = PdfFileReader(open("watermark.pdf", "rb"))
	origCover.mergePage(watermark.getPage(0))
	os.remove("watermark.pdf")
	return origCover






if __name__ == '__main__':
	main(sys.argv[1:])

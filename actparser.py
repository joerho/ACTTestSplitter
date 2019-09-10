from pdf2image import convert_from_path
import pytesseract
from PIL import Image

from PyPDF4 import PdfFileReader,PdfFileWriter,PdfFileMerger
from reportlab.pdfgen import canvas
import sys
import os
import re
import itertools

#python3 program.py test.pdf cover.pdf [page ranges]
CONST_TESTPATH = '/Users/joerho/ModusDropBox/Dropbox/Modus Teachers (Shared)/1 ACT/ REAL ACT TESTS/Single File'
CONST_OUTDIR = '/Users/joerho/ModusDropBox/Dropbox/Modus Teachers (Shared)/9 Joe/ACT/SubjectSeparated'
CONST_NUM_SECTIONS = 4
CONST_SECTION_MAP = {0:'E', 1:'M', 2:'R' , 3:'S'}
CONST_ENGLISH = '/Users/joerho/Desktop/pyPDF/Test Covers/english.png'
CONST_MATH = '/Users/joerho/Desktop/pyPDF/Test Covers/math.png'
CONST_READING = '/Users/joerho/Desktop/pyPDF/Test Covers/reading.png'
CONST_SCIENCE = '/Users/joerho/Desktop/pyPDF/Test Covers/science.png'


def actparse(argv):
	print("\n\nParsing arguments...")
	parsedArgv = checkArgv(argv)
	print(parsedArgv)

	testPath = os.path.join(CONST_TESTPATH, parsedArgv[0])
	pageRanges = parsedArgv[1]
	testNameNum = getTestName(testPath)
	outputDirs = prepareOutputDirectory(testNameNum[0])

	splitPages(testNameNum, testPath, pageRanges, outputDirs)
	mixAndMatch(testNameNum, testPath, outputDirs)

def splitPages(testNameNum, testPath, pageRanges, outputDirs):
	temp = 1
	key = 0
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

		outputFileName = genSectionFilePath(outputDirs, testNameNum[1], testNameNum[0], key)
		with open(outputFileName, 'wb') as out:
			pdfWriter.write(out)
		temp = bookmark
		key += 1

	f.close()


def mixAndMatch(testNameNum, testPath, outputDirs):
	subsets = generateKeyCombo()
	for subset in subsets:
		eachSection = list()
		size = len(subset)

		if size == 2:
			outputFileName = os.path.join(outputDirs, '{} {} {}{}.pdf'
			 .format(testNameNum[1], testNameNum[0], CONST_SECTION_MAP[subset[0]], 
			 CONST_SECTION_MAP[subset[1]]))
			eachSection.append(genSectionFilePath(outputDirs, testNameNum[1], testNameNum[0], subset[0]))
			eachSection.append(genSectionFilePath(outputDirs, testNameNum[1], testNameNum[0], subset[1]))

		if size == 3:
			outputFileName = os.path.join(outputDirs, '{} {} {}{}{}.pdf'
			 .format(testNameNum[1], testNameNum[0], CONST_SECTION_MAP[subset[0]], 
			 CONST_SECTION_MAP[subset[1]], CONST_SECTION_MAP[subset[2]]))
			eachSection.append(genSectionFilePath(outputDirs, testNameNum[1], testNameNum[0], subset[0]))
			eachSection.append(genSectionFilePath(outputDirs, testNameNum[1], testNameNum[0], subset[1]))
			eachSection.append(genSectionFilePath(outputDirs, testNameNum[1], testNameNum[0], subset[2]))
		
		pdfConcat(eachSection, outputFileName, testPath)

def generateKeyCombo():
	keys = list()
	subsets = list()

	for i in range(0, CONST_NUM_SECTIONS):
		keys.append(i)

	for length in range(2, len(keys)):
		for subset in itertools.combinations(keys, length):
			subsets.append(subset)

	return subsets

def pdfConcat(inputFiles, outputFileName, testPath):
	pdfWriter = PdfFileWriter()
	temp = open(testPath, 'rb')
	pdf = PdfFileReader(temp)
	pdfWriter.addPage(pdf.getPage(0))

	for filePath in inputFiles:
		f = open(filePath , 'rb')
		pdfReader = PdfFileReader(f)
		
		for page in pdfReader.pages[1:]:
			pdfWriter.addPage(page)

	with open(outputFileName, 'wb') as out:
		pdfWriter.write(out)

	temp.close()

def addPages(pdfWriter, pdf):
	for page in pdf:
		pdfWriter.addPage(page)

def genSectionFilePath(outputDir, testNum, testName, sectionKey):
	return os.path.join(outputDir, '{} {} {}.pdf'
	 .format(testNum, testName, CONST_SECTION_MAP[sectionKey]))
				

def getOrigCover(testPath):
	with open(testPath, 'rb') as f:
		pdf = PdfFileReader(f)
		return pdf.getPage(0)


def checkArgv(argv):
	testName = argv[0]
	pageRanges = argv[1]
	testPath = os.path.join(CONST_TESTPATH, testName)

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

	return testDirPath

	# individualPath = os.path.join(testDirPath, "Individual Sections")
	# if not os.path.exists(individualPath):
	# 	os.makedirs(individualPath)

	# return [testDirPath, individualPath]

def addWaterMark(origCover, key):
	c = canvas.Canvas('watermark.pdf')
	if key == 0:
		c.drawImage(CONST_ENGLISH, 190, 220)
	elif key == 1:
		c.drawImage(CONST_MATH, 220, 220)
	elif key == 2:
		c.drawImage(CONST_READING, 190, 220)
	elif key == 3:
		c.drawImage(CONST_SCIENCE, 190, 220)

	c.save()
	watermark = PdfFileReader(open("watermark.pdf", "rb"))
	origCover.mergePage(watermark.getPage(0))
	os.remove("watermark.pdf")

	return origCover

# if __name__ == '__main__':
# 	main(sys.argv[1:])

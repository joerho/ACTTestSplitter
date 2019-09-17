from pdf2image import convert_from_path
import pytesseract
from PIL import Image

from PyPDF4 import PdfFileReader,PdfFileWriter,PdfFileMerger
from reportlab.pdfgen import canvas
import sys
import os
import re
import itertools
import dropbox

#python3 program.py test.pdf cover.pdf [page ranges]
CONST_ACCESS_TOKEN = 'do2GicKOS1AAAAAAAAAC0ARZMyPNvzfbbvA3073XwjYFtErsHsS4ZmCGWkx53YRN'
CONST_TESTPATH = '/Users/joerho/ModusDropBox/Dropbox/Modus Teachers (Shared)/1 ACT/ REAL ACT TESTS/Single File'
CONST_OUTDIR = '/testparser/ACT/SubjectSeparated'
CONST_NUM_SECTIONS = 4
CONST_SECTION_MAP = {0:'E', 1:'M', 2:'R' , 3:'S'}
CONST_ENGLISH = '/Users/joerho/Desktop/pyPDF/Test Covers/english.png'
CONST_MATH = '/Users/joerho/Desktop/pyPDF/Test Covers/math.png'
CONST_READING = '/Users/joerho/Desktop/pyPDF/Test Covers/reading.png'
CONST_SCIENCE = '/Users/joerho/Desktop/pyPDF/Test Covers/science.png'
CONST_LOCAL = 'temporaryPDF'

class TransferData:
    def __init__(self, access_token):
        self.access_token = access_token

    def upload_file(self, file_from, file_to):
        dbx = dropbox.Dropbox(self.access_token)

        with open(file_from, 'rb') as f:
            dbx.files_upload(f.read(), file_to)

def actparse(argv):
	print("\n\nParsing arguments...")
	parsed_argv = check_argv(argv)
	print(parsed_argv)

	test_path = os.path.join(CONST_TESTPATH, parsed_argv[0])
	page_ranges = parsed_argv[1]
	testnamenum = get_testnamenum(test_path)
	output_dir = prepare_output_dir(testnamenum[0])

	split_pages(testnamenum, test_path, page_ranges)
	mix_match(testnamenum, test_path)
	move_to_dropbox(output_dir)
	remove_local_files()

def move_to_dropbox(output_dir):
	filelist = os.listdir(CONST_LOCAL)
	for f in filelist:
		local_filename = os.path.join(CONST_LOCAL, f)
		output_filename = os.path.join(output_dir, f)
		upload_dropbox(local_filename, output_filename)

def remove_local_files():
	filelist = os.listdir(CONST_LOCAL)
	for f in filelist:
		os.remove(os.path.join(CONST_LOCAL, f))

def upload_dropbox(local_filename, output_filename):
	transferData = TransferData(CONST_ACCESS_TOKEN)
	transferData.upload_file(local_filename, output_filename)

def split_pages(testnamenum, test_path, page_ranges):
	temp = 1
	key = 0
	for bookmark in page_ranges:
		f = open(test_path, 'rb')
		pdf = PdfFileReader(f)
		pdf_writer = PdfFileWriter()
		
		#add watermark to original cover
		orig_cover = pdf.getPage(0)
		new_cover = add_watermark(orig_cover, key)

		#put new cover on the front
		pdf_writer.addPage(new_cover)

		for page in range(temp, bookmark):
			pdf_writer.addPage(pdf.getPage(page))

		local_filename = generate_section_filepath(CONST_LOCAL, testnamenum, key)
		# output_filename = generate_section_filepath(output_dirs, testnamenum, key)

		with open(local_filename, 'wb') as out:
			pdf_writer.write(out)

		# upload_dropbox(local_filename, output_filename)

		temp = bookmark
		key += 1

	f.close()


def mix_match(testnamenum, test_path):
	subsets = generate_keycombo()
	for subset in subsets:
		each_section = list()
		size = len(subset)

		if size == 2:
			new_filename = '{} {} {}{}.pdf'.format(
				testnamenum[1], 
				testnamenum[0], 
				CONST_SECTION_MAP[subset[0]], 
			 	CONST_SECTION_MAP[subset[1]])
			each_section.append(generate_section_filepath(CONST_LOCAL, testnamenum, subset[0]))
			each_section.append(generate_section_filepath(CONST_LOCAL, testnamenum, subset[1]))

		if size == 3:
			new_filename = '{} {} {}{}{}.pdf'.format(
				testnamenum[1], 
				testnamenum[0], 
				CONST_SECTION_MAP[subset[0]], 
				CONST_SECTION_MAP[subset[1]], 
				CONST_SECTION_MAP[subset[2]])
			each_section.append(generate_section_filepath(CONST_LOCAL, testnamenum, subset[0]))
			each_section.append(generate_section_filepath(CONST_LOCAL, testnamenum, subset[1]))
			each_section.append(generate_section_filepath(CONST_LOCAL, testnamenum, subset[2]))
		
		pdfConcat(each_section, new_filename, test_path)

def generate_keycombo():
	keys = list()
	subsets = list()

	for i in range(0, CONST_NUM_SECTIONS):
		keys.append(i)

	for length in range(2, len(keys)):
		for subset in itertools.combinations(keys, length):
			subsets.append(subset)

	return subsets

def pdfConcat(each_section, new_filename, test_path):
	pdf_writer = PdfFileWriter()
	temp = open(test_path, 'rb')
	pdf = PdfFileReader(temp)
	pdf_writer.addPage(pdf.getPage(0))

	for file_path in each_section:
		f = open(file_path , 'rb')
		pdf_reader = PdfFileReader(f)
		
		for page in pdf_reader.pages[1:]:
			pdf_writer.addPage(page)

	local_filename = os.path.join(CONST_LOCAL, new_filename)

	with open(local_filename, 'wb') as out:
		pdf_writer.write(out)
		
	# upload_dropbox(local_filename, output_filename)

	temp.close()

def generate_section_filepath(output_dir, testnamenum, sectionKey):
	return os.path.join(output_dir, '{} {} {}.pdf'
	 .format(testnamenum[1], testnamenum[0], CONST_SECTION_MAP[sectionKey]))
				

def getOrigCover(test_path):
	with open(test_path, 'rb') as f:
		pdf = PdfFileReader(f)
		return pdf.getPage(0)


def check_argv(argv):
	test_name = argv[0]
	page_ranges = argv[1]
	test_path = os.path.join(CONST_TESTPATH, test_name)

	try:
		t = open(test_path, 'rb')
	except Exception as e:
		print("The test pdf does not exist.")
	
	t.close()

	page_arr = checkPageRanges(page_ranges)

	return [test_path, page_arr]


def checkPageRanges(page_ranges):
	page_arr = page_ranges.split(',')
	try:
		page_arr = [int(x) for x in page_arr]
	except:
		print("Each value of page range must be an int.")

	if isPositive(page_arr) == False:
		print("Why would you put in a negative number..?")
		sys.exit()

	if isSorted(page_arr) == False:
		print("Page range has to be sorted.")
		sys.exit()

	if len(page_arr) != CONST_NUM_SECTIONS:
		print("Page range must be a length of {}".format(CONST_NUM_SECTIONS))
		sys.exit()

	return page_arr

def isPositive(page_arr):
	for x in page_arr:
		if x <= 0:
			return False

	return True

def isSorted(page_arr):
	temp = page_arr[0]
	for x in page_arr[1:]:
		if x < temp:
			return False
		else:
			temp = x

	return True

def get_testnamenum(test_path):
	path, test_name = os.path.split(test_path)
	arr = test_name.split(" ")
	test_num = re.search('\(([^)]+)', arr[-1]).group(1)
	arr = [''.join(arr[:-1]), test_num]

	return arr

def prepare_output_dir(test_name):
	test_directory = os.path.join(CONST_OUTDIR, test_name)

	return test_directory

def add_watermark(orig_cover, key):
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
	orig_cover.mergePage(watermark.getPage(0))
	os.remove("watermark.pdf")

	return orig_cover

# if __name__ == '__main__':
# 	main(sys.argv[1:])

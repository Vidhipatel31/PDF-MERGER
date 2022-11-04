import os
import shutil
import PyPDF2
from PIL import Image
from multiprocessing.pool import ThreadPool
# Current Folder
Folder = input("Folder [Hit Enter to select current working directory]:")
if Folder == "":
    Folder = os.getcwd()
# Replacing backslashes with forewardslashes, cuz OS issues.
Folder = Folder.replace("\\", "/")
if not Folder.endswith("/"):
    Folder += "/"

LongestNum = 0
for File in os.listdir(Folder):
    FileName = ".".join(File.split('.')[:-1])
    if FileName.isnumeric() and len(FileName) > LongestNum:
        LongestNum = len(FileName)
for File in os.listdir(Folder):
    FileName = ".".join(File.split('.')[:-1])
    if FileName.isnumeric():
        newFileName = FileName.zfill(LongestNum) + "." + File.split('.')[-1]
        os.rename(Folder+File, Folder+newFileName)


ContentFolder = Folder+"Content"
NewFiles = [ContentFolder + "/" +
            File for File in sorted(os.listdir(Folder), key=str)]
# Data folder
TempFolder = Folder+"Temp"
DataFolder = Folder + "Data"
if not os.path.isdir(DataFolder):
    os.mkdir(DataFolder)


def IMG2PDF(File):
    try:
        File = Folder + File
        I = Image.open(File)
        I.save(f"{'.'.join(File.split('.')[:-1])}.pdf")
        os.rename(File, Folder + "Data/" + File.split('/')[-1])
    except Exception as e:
        pass


for i in ThreadPool(25).imap_unordered(IMG2PDF, sorted(os.listdir(Folder))):
    pass


Files = [Folder+File for File in sorted(os.listdir(Folder)) if not os.path.isdir(
    Folder+"/"+File) and not File.startswith('.')]

Merger = PyPDF2.PdfFileMerger()


for File in Files:

    # Incase file is a pdf
    if File.endswith('.pdf'):
        with open(File, "rb") as f:
            Merger.append(PyPDF2.PdfFileReader(f))

    # And incase file is not pdf
    elif not File.endswith('.pdf'):

        # If TempFolder doesn't exist this will create it.
        if not os.path.isdir(TempFolder):
            os.mkdir(TempFolder)

        # File name with extension and without extension
        FileNameExt = File.split('/')[-1]
        FileName = ".".join(FileNameExt.split('.')[0:-1])

        # Converting File to pdf
        with open(f"{TempFolder}/{FileName}.pdf", "wb") as f:
            try:
                # f.write(img2pdf.convert(File))
                f.write(None)
            # For any kind of error it will skip it, and store the file in Error folder.
            except Exception as e:
                print(f"{File}: {type(e).__name__}")

                ErrorFolder = Folder+"Error"
                if not os.path.isdir(ErrorFolder):
                    os.mkdir(ErrorFolder)
                SourceFilePath = f"{Folder}{FileNameExt}"
                DestinationFilePath = f"{Folder}Error/{FileNameExt}"
                os.replace(SourceFilePath, DestinationFilePath)

                continue

        # Name of the current file
        File = f"{TempFolder}/{FileName}.pdf"

        # Adding it to the Merger instance
        with open(File, "rb") as f:
            Merger.append(PyPDF2.PdfFileReader(f))

# Getting OutputFile name and writing the Merger instance to the OutputFile.
OutputFile = Folder + Folder.split("/")[-2] + ".pdf"
Merger.write(OutputFile)

# Deleting the Temp Folder
if os.path.isdir(TempFolder):
    shutil.rmtree(TempFolder)

# Moving the Original Contents of the folder to "Content" folder. - 2
if not os.path.isdir(ContentFolder):
    os.mkdir(ContentFolder)
for src, dst in zip(Files, NewFiles):
    try:
        os.replace(src, dst)
    except Exception as e:
        pass

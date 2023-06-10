# Youtube and Reddit MP3/MP4 Downloader
This Python program allows you to download MP3 or MP4 files from YouTube and Reddit. It provides a graphical user interface (GUI) built using PySimpleGUI.

# Dependencies
This program depends on the following Python packages:

* subprocess
* requests
* os
* re
* sys
* pyperclip
* pytube
* redvid
* threading
* bs4 (BeautifulSoup)
* time (sleep)
* PySimpleGUI

To install most python dependencies easily, run the following command (Some may need to be installed manually):
pip install -r requirements.txt

# Usage
1. Run the program using Python.
2. The main window will appear with options for YouTube and Reddit downloads, as well as video compression.
3. In the YouTube section, enter the URL of the video you want to download in the "Video Link" field. You can also click the "Paste" button to paste a copied link. The program will display information about the video, such as title, views, and length.
4. Choose the desired format from the drop-down menu in the "Pick your desired Format" field. You can select MP3 or various resolutions of MP4 videos. If you select a specific resolution, the program will download the video with that resolution. If you choose "MAX (.mp4)," it will download the video with the highest available resolution. Click the "Confirm" button to start the download.
5. The program will display the progress of the download in the progress bar. Larger files may take longer to download.
6. After the download is complete, the program will indicate that the file has been downloaded successfully. The downloaded file will be saved in the default Downloads folder.
7. You can specify a different output folder by entering the desired path in the "Output" field.
8. To download MP3 or MP4 files from Reddit, follow the same steps as for YouTube but use a Reddit post URL instead.
9. In the video compression section, you can compress existing video files using Ffmpeg. Click the "Install" button to install the required packages for video compression. Then, choose a file to compress by clicking the "Choose a file" button. Enter the Constant Rate Factor (CRF) value in the range of 23-51, where a lower value indicates higher quality. Finally, enter the desired name for the compressed file in the "Compressed File Name" field and click the "Compress Video" button. The program will display the progress of the compression process.

Note: The program will show the output and error messages in the respective output fields.

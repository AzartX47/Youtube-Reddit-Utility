import subprocess
import requests
import os, re, sys
import pyperclip as pc
from pytube import YouTube
from redvid import Downloader
import threading
from bs4 import BeautifulSoup
from time import sleep

try: import PySimpleGUI as sg
except ImportError as e: print(f"Missing package: {e} (Use pip to install)"), sleep(5), sys.exit()

downloads_path = str(f"{os.path.expanduser('~')}\Downloads")
#downloads_path = str(f"{os.path.expanduser('~')}\Downloads\Music")
headers, glob = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36"}, 0
sg.theme("Dark Grey 5")

def window_framework(): 

    main_window = [
    [sg.Text("                 Youtube and Reddit MP3/MP4 Downloader\n")],
	[sg.Text("Video Link:"), sg.Input(size=(36,2), enable_events=True, key="-LINK-"), sg.Button("Paste")],
    [sg.Text("                                  "), sg.Button("        Confirm        ")],
	[sg.Text("File Information:")],
    [sg.Output(size=(53,4), key="-INFO-")],
    [sg.Text("Rename (Blank for Default):  "), sg.Input(size=(18,2), enable_events=True, key="-NAME-"), sg.Text(".mp3/mp4")],
    [sg.Text("Pick you desired Format:      "), sg.OptionMenu(values=[' Select Value'], default_value='Select Value', key='-FORMAT-'), sg.Button('  Confirm ')],
    [sg.Text('The file will download after the "Confirm" button is pressed')],
    [sg.Text("                Larger files take longer to download:"), sg.ProgressBar(1000, orientation='h', size=(9.5, 20), key='progressbar')],
    [sg.Text("Output: "), sg.Input(size=(30,1), enable_events=True, key="-OUT-"), sg.Button("      Clear All      ")]] #, sg.Button("Quit ")

    compressor_window = [
    [sg.Text("                                    Compress Video Files with Ffmpeg\n")],
    [sg.Text("Install all required packages from pip.\nClick the button to install all the packages needed for program execution:\n", text_color='red', font='Helvetica 10'), sg.Button("Install")],
    [sg.Text("Choose a file: "), sg.Input(key="-DISPLAY-"), sg.FileBrowse()],
    [sg.Text("Please enter crf value in range 23-51 (A lower value is a higher quality): "), sg.Input(size=(7,1), enable_events=True, key="-CRF-")],
    [sg.Text("")],
    [sg.Text("Compressed File Name: "), sg.Input(size=(18,1), key="-CMPNAME-"), sg.Text(".mp4 (only)"), sg.Button("Compress Video")],
    [sg.Text("Process:")],
    [sg.Output(size=(66,4), key="-CMPINFO-")],
    [sg.Text("Output:"), sg.Input(size=(30,1), key="-CMPOUTPUT-"),sg.Text("       "), sg.Button(" Clear All "), sg.Button("  Quit  ")]
    ]

    layout = [
	[
	sg.Column(main_window),
	sg.VSeperator(),
	sg.Column(compressor_window),
	] ]

    window = sg.Window("Youtube/Reddit Utility (Created by AzartX47)", layout)
    progress_bar = window['progressbar']
    return window, progress_bar

def event_loop(window, progress_bar):
    data = ""
    while True:
        event, values = window.read()
        try:
            if event == sg.WIN_CLOSED or event == "  Quit  ":
                window.close()
                break
            if event == '  Confirm ' and values['-FORMAT-'].lstrip(" ") != 'Select Value':
                window["-OUT-"].update("Working..."), window.find_element("-CMPOUTPUT-").update("")
                progress_bar.UpdateBar(0)
                threading.Thread(target={'mp3': mp3_only, 'mp4': both_tracks}[re.sub('[\W_]+', '', values['-FORMAT-'].split(' ')[1 if ' ' in values['-FORMAT-'] else 0])], args=(window, values, data, values['-FORMAT-'], progress_bar), daemon=True).start()
            if event == "      Clear All      ": clear(window, ["-LINK-", "-INFO-", "-OUT-", "-NAME-"]), progress_bar.UpdateBar(0)
            if event == " Clear All ": clear(window, ["-DISPLAY-", "-CRF-", "-CMPNAME-", "-CMPOUTPUT-", "-CMPINFO-"])
            if event == "Compress Video": threading.Thread(target=compress_video, args=(window, values, progress_bar), daemon=True).start()
            if event == "Install": threading.Thread(target=installer, args=(window, values, progress_bar), daemon=True).start()
            if event == "Paste": window.find_element("-LINK-").update(pc.paste())
            if event == "        Confirm        " and values["-LINK-"] != "": data = check_parameters(window, values)
        except Exception as e: window["-CMPINFO-"].update(e)

def check_parameters(window, values):
    def fetch_res(yt):
        video_resolutions = []

        for stream in yt.streams.filter(progressive=True): video_resolutions.append(int(stream.resolution[:-1]))
        l = [*set(video_resolutions)]
        l.sort()
        for id in range(len(l)): l[id] = f"{str(l[id])}p (.mp4)"
        l = ['.mp3'] + l + ['MAX (.mp4)', 'Select Value']
        return l

    try:
        clear(window, ["-LINK-", "-INFO-", "-OUT-", "-NAME-"])
        try:
            yt = YouTube(values["-LINK-"])
            info = f"Title: {str(yt.title)}\nNumber of views: {f'{int(yt.views):,}'}\nLength of video: {f'{int(yt.length):,}'} seconds"
            window.Element('-FORMAT-').Update(values=fetch_res(yt), value='Select Value')
            window["-INFO-"].update(info)
            return yt
        except:
            soup = BeautifulSoup(requests.get(values["-LINK-"], headers=headers).content, 'html.parser')
            title_ = soup.find('h1', class_='_eYtD2XCVieq6emjKBH3m').text
            upvotes = soup.find('div', class_='_1E9mcoVn4MYnuBQSVDt1gC').find('div', class_='_1rZYMD_4xY3gRcSS3p8ODO').text
            community = soup.find('div', class_='_20Kb6TX_CdnePoT8iEsls6').text
            info = f"Title: {str(title_)}\nCommunity: {str(community)}\nUpvotes: {str(upvotes)}"
            window.Element('-FORMAT-').Update(values=['.mp3', '.mp4', 'Select Value'], value='Select Value')
            window["-INFO-"].update(info)
            return {'Reddit': [values["-LINK-"], title_]}
    except:
        info = 'Must be a valid Youtube or Reddit link!'
        window["-INFO-"].update(info)

def mp3_only(window, values, yt, v_f, progress_bar):
    global glob
    #clear(window, ["-CMPINFO-", "-CMPOUTPUT-"])

    try:
        if yt == "": raise NameError('Value is blank. Make sure to specify source first')
        threading.Thread(target=progressbar, args=(window, progress_bar), daemon=True).start()
        if type(yt) != dict:
            ys = yt.streams.get_lowest_resolution()
            #ys = yt.streams.get_audio_only()
            file = ys.download(downloads_path, filename=uniquify(f"{downloads_path}\{yt.title}.mp4"))
        else:
            reddit = Downloader(url= yt['Reddit'][0])
            reddit.log, reddit.overwrite, reddit.path = False, True, downloads_path
            file = reddit.download()
            
        base, ext = os.path.splitext(file)
        if values["-NAME-"] != "": filename = uniquify(f'{downloads_path}\{str(values["-NAME-"])}{ext}').rstrip(ext)
        else: filename = base.rstrip('.mp4') if type(yt) != dict else uniquify(f"{downloads_path}\{str(yt['Reddit'][1])}{ext}").rstrip(ext)

        compressor_call(window, values, f'ffmpeg -y -i "{base}"{ext} "{filename}".mp3', ["-OUT-", "File downloaded successfully"])
        os.remove(file)

    except: 
        if 'BaseException' in str(sys.exc_info()[0]): window["-OUT-"].update("Working... No video in post!")
        else: window["-OUT-"].update("Working... Failed"), window["-CMPINFO-"].update(sys.exc_info())
    glob = 1

def both_tracks(window, values, yt, v_f, progress_bar):
    global glob
    #clear(window, ["-CMPINFO-", "-CMPOUTPUT-"])

    try:
        if yt == "": raise NameError('Value is blank. Make sure to specify source first')
        threading.Thread(target=progressbar, args=(window, progress_bar), daemon=True).start()
        if type(yt) != dict:
            ys = yt.streams.get_highest_resolution() if 'MAX' in v_f else yt.streams.filter(progressive=True, res=v_f.split(' ')[0]).first()
            file = ys.download(downloads_path, filename=uniquify(f"{downloads_path}\{yt.title}.mp4"))
        else:
            reddit = Downloader(url= yt['Reddit'][0])
            reddit.log, reddit.overwrite, reddit.path = False, True, downloads_path
            file = reddit.download()

        if type(yt) != dict:
            if str(values["-NAME-"]) != "":
                name = str(values["-NAME-"])
                new_file = f'{downloads_path}/{name}.mp4'
                os.rename(file, uniquify(new_file))
            else:
                pass
        else:
            if str(values["-NAME-"]) != "":
                name = str(values["-NAME-"])
            else:
                name = str(yt['Reddit'][1])
            new_file = f'{downloads_path}/{name}.mp4'
            os.rename(file, uniquify(new_file))

        window["-OUT-"].update("File downloaded successfully")

    except: 
        if 'BaseException' in str(sys.exc_info()[0]): window["-OUT-"].update("Working... No video in post!")
        else: window["-OUT-"].update("Working... Failed"), window["-CMPINFO-"].update(sys.exc_info())
    glob = 1

def compress_video(window, values, progress_bar):
    global glob

    window["-CMPOUTPUT-"].update("Working...")
    if os.path.exists(values["-DISPLAY-"]) == True:
        #threading.Thread(target=progressbar, args=(window, progress_bar), daemon=True).start()
        compressor_call(window, values, "ffmpeg -y -i " +str("\"" + values["-DISPLAY-"])+ "\" -vcodec libx264 -crf "+str(values["-CRF-"])+" \""+downloads_path+"/"+str(values["-CMPNAME-"])+"_compressed.mp4\"", ["-CMPOUTPUT-", "File compressed successfully"])
    else: window["-CMPOUTPUT-"].update("Compression Failed")
    #glob = 1

def compressor_call(window, values, command, output_window):
    p = subprocess.Popen(command, shell=True, encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True) #, universal_newlines=True
    #for line in iter(p.stdout.readline,''):
    for line in p.stdout:
        print(line.rstrip())
        window.Refresh() if window else None
    window[output_window[0]].update(output_window[1])

def installer(window, values, progress_bar):
    global glob

    commands = [
    'PySimpleGUI',
    'ffmpeg-python', 
    'pyperclip',
    'pytube',
    'redvid',
    'beautifulsoup4',
    'requests'
    ]
    #threading.Thread(target=progressbar, args=(window, progress_bar), daemon=True).start()
    window["-CMPOUTPUT-"].update(f'Started Installation...')
    for package in commands:
        try: packages(window, values, f"pip install {package}")
        except Exception as e: window["-CMPOUTPUT-"].update(f'{window["-CMPOUTPUT-"]} {e}')
    window["-CMPOUTPUT-"].update("Finished Installation")
    #glob=1


def packages(window, values, command):
    p = subprocess.Popen(command, shell=True, encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True) #, universal_newlines=True
    for line in p.stdout:
        print(line.rstrip())
        window.Refresh() if window else None

def progressbar(window, progress_bar):
    global glob
    i = 0
    while glob != 1:
        i += 0.5
        if i != 1010: progress_bar.UpdateBar(i + 1)
        else: i = 0

    progress_bar.UpdateBar(1000)
    glob = 0

def uniquify(path):
    filename, extension = os.path.splitext(path)
    counter = 1
    while os.path.exists(path):
        path = f"{filename}({str(counter)}){extension}"
        counter += 1
    return path

def clear(window, windows):
    for element in windows: window.find_element(element).update("")

wnd, progress = window_framework()
event_loop(wnd, progress)
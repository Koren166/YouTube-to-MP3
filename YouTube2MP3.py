from pytube import YouTube
import pytube.exceptions
import os
import PySimpleGUI as sg

SYMBOL_UP = '▲'
SYMBOL_DOWN = '▼'


def collapse(content, key):
    """
    Helper function that creates a Column that can be later made hidden, thus appearing "collapsed"

    :param content: The layout for the section
    :param key: Key used to make this section visible / invisible
    :return: A pinned column that can be placed directly into your layout
    :rtype: sg.pin
    """
    return sg.pin(sg.Column(content, key=key, visible=False))


def is_line_num_even(text):
    """Checks if there's an even amount of lines"""
    n = text.count("\n")
    return n % 2 == 0


def download_files(text, folder_path):
    """
    Converts YouTube links to MP3 files and downloads them to a chosen location

    :param text: Contains the titles & links given by the user
    :param folder_path: Where to save the downloaded files
    :return: Returns True if fully successful, False otherwise
    """
    i = int(-1)
    lines = []
    for line in text.splitlines():
        try:
            i += 1
            lines.append(line)

            # is title
            if (i % 2) == 0:
                continue

            # is url
            elif (i % 2) == 1:
                title = lines[i - 1]
                yt = YouTube(line)
                video = yt.streams.filter(only_audio=True).first()
                out_file = video.download(output_path=folder_path, filename=title)
                base, ext = os.path.splitext(out_file)
                new_file = base + '.mp3'
                os.rename(out_file, new_file)

        except (pytube.exceptions.VideoUnavailable, pytube.exceptions.ExtractError, pytube.exceptions.RegexMatchError,
                pytube.exceptions.PytubeError, pytube.exceptions.HTMLParseError) as e:
            return False
    return True


sg.theme('TanBlue')

help_section = [sg.Frame(layout=[[sg.Text('1) In the box below, enter the desired file name\n'
                                          '   for each music file, followed by the link to it,\n'
                                          '   each in separate lines (important!)\n\n'
                                          '   You can add as many as you want!', font='Quicksand 10')],
                                 [sg.Frame(title='Example:', element_justification='center',
                                           layout=[[sg.Text('Rick Astley - Never Gonna Give You Up\n'
                                                            'https://www.youtube.com/watch?v=dQ...\n'
                                                            'Smash Mouth - All Star\n'
                                                            'https://www.youtube.com/watch?v=L_...\n'
                                                            '. . .', font='Quicksand 8')]])],
                                 [sg.Text('2) Choose where you want to save the files\n\n'
                                          '3) Click download! The window might freeze or\n'
                                          '   turn black - no worries!\n'
                                          '   It means it\'s downloading, which takes a few\n '
                                          '   seconds, depends how many files you are\n'
                                          '   downloading at once',
                                          font='Quicksand 10')]], title='?', relief='sunken')],

layout = [
    # Headline
    [sg.Frame(title='', element_justification='center',
              layout=[[sg.Text('Welcome to YouTube to MP3 downloader!')]])],

    # Help Section
    [sg.T(SYMBOL_UP, enable_events=True, k='-OPEN SEC2-'),
     sg.T('How to use?', enable_events=True, k='-OPEN SEC2-TEXT')],
    [collapse(help_section, '-SEC2-')],

    # User input
    [sg.Text('File names & links ↓')],
    [sg.Multiline(key='urls', size=(32, 7), enable_events=True, default_text='')],

    # Folder browser
    [sg.Frame(title='Save files to...',
              layout=[[sg.In(key='folder', size=(24, 1), default_text='Choose folder'),
                       sg.FolderBrowse(target='folder')]])],

    # Success message
    [sg.Text('       Previous download was successful!       ', justification='center', relief='groove',
             visible=False, background_color='Light Green', text_color='Dark Green', key='success')],

    # Download Button
    [sg.Button(button_text='                           Download                           ',
               border_width=5, key='download')],

    # Disclaimer, copyright, etc.
    [sg.Text('Use at own risk! Do not distribute without permission! Koren Gazit, 2020',
             font='Quicksand 7', text_color='Grey')]
]

window = sg.Window('YouTube to MP3', layout, font='Quicksand 12')
opened2 = False
event, values = window.read()

# Event Loop
while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED:
        break

    if event.startswith('-OPEN SEC2-'):
        opened2 = not opened2
        window['-OPEN SEC2-'].update(SYMBOL_DOWN if opened2 else SYMBOL_UP)
        window['-SEC2-'].update(visible=opened2)

    urls = values['urls']
    folder = values['folder']

    if event == 'download':
        if (urls == '\n') or (not (is_line_num_even(urls))):
            sg.popup_ok('The number of titles & links is not even!', title='Error')
        elif (folder == 'Choose folder') or (folder == ''):
            sg.popup_ok('You did not choose where to save!', title='Error')
        else:
            folder += '/'
            dl_success = download_files(urls, folder)
            if not dl_success:
                sg.popup_ok('There was a problem with one of the links.\n'
                            'Check which file was the problem and try again.', title='Fail')
            else:
                window['urls'].update('')
                window['success'].update(visible=True)

window.close()

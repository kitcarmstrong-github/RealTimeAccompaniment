import ast
import time
import rtmidi
import threading
import tkinter as tk
from tkinter import scrolledtext, filedialog, ttk
from rtmidi.midiutil import open_midioutput
from rtmidi.midiconstants import NOTE_OFF, NOTE_ON, CONTROL_CHANGE, ALL_SOUND_OFF,  ALL_NOTES_OFF

def print_to_terminal(message, output_widget):
    output_widget.insert(tk.END, message)
    output_widget.yview(tk.END)

def clear_terminal(output_widget):
    output_widget.delete(1.0, tk.END)

def open_file(output_widget):
    output_widget.delete(1.0, tk.END)
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file_path:
        with open(file_path, 'r') as file:
            try:
                global inputlog
                inputlog = ast.literal_eval(file.read())
                for item in inputlog:
                    print_to_terminal(str(item) + '\n', output_widget)
                print_to_terminal('\n' + 'Sum of notes = ' + str(len(inputlog)) + '\n', output_widget)
            except (ValueError, SyntaxError):
                print_to_terminal("Error: File content is not a valid Python literal.\n", output_widget)

def save_to_file(output_widget):
    content = output_widget.get("1.0", tk.END)
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])

    if file_path:
        with open(file_path, 'w') as file:
            file.write(content)
        print_to_terminal(f"Terminal content saved to file: {file_path}\n", terminal_output2)

def on_port_selected(event):
    global midiout
    selected_port = port_combobox.get()
    try:
        midiout, port_name = open_midioutput(selected_port)
        message = f"Selected MIDI Port: {port_name}\n"
        print_to_terminal(message, terminal_output2)
    except Exception as e:
        error_message = f"Error opening MIDI Port: {e}\n"
        print_to_terminal(error_message, terminal_output2)

stop_flag = threading.Event()
midiout = 0
is_playing = False

def play_in_thread(stop_flag, output_widget):
    global midiout, is_playing
    startTime = time.time()
    print_to_terminal('Start Time Stamp = ' + str(startTime) + '\n', output_widget)
    index = 0
    while not stop_flag.is_set():
        try:
            currentTime = time.time()
            if ((startTime + inputlog[index][4] - inputlog[0][4] + 1) - currentTime <= 0):
                midiout.send_message([inputlog[index][1], inputlog[index][2], inputlog[index][3]])
                print_to_terminal(str(inputlog[index][1]) + ',' + str(inputlog[index][2]) + ',' + str(inputlog[index][3]) + '\n',output_widget)
                index += 1
                if (index >= len(inputlog)):
                    print('Done')
                    is_playing = False
                    break
        except (EOFError, KeyboardInterrupt):
            print('Exit')
            is_playing = False
            break

def play_program_in_thread(output_widget):
    global stop_flag, is_playing
    stop_flag.clear()
    if (is_playing == False):
        is_playing = True
        threading.Thread(target=play_in_thread, args=(stop_flag, output_widget,)).start()

def reset_midi_program():
        if midiout:
            channel = 0
            for note in range(128):
                midiout.send_message([NOTE_OFF | channel , note, 0])
            midiout.close_port()
            
def stop_program():
    global stop_flag, is_playing
    stop_flag.set()
    is_playing = False
    if midiout:
        channel = 0
        for note in range(128):
            midiout.send_message([NOTE_OFF | channel , note, 0])

def exit_program():
    global stop_flag
    stop_flag.set()
    if midiout:
        channel = 0
        for note in range(128):
            midiout.send_message([NOTE_OFF | channel , note, 0])
        midiout.close_port()
    root.destroy()

root = tk.Tk()
root.title("Team Piano MIDI Player")

# Frame 1
frame1 = tk.Frame(root)
frame1.grid(row=0, column=0, padx=10, pady=10)

# Label for Terminal 1
label_terminal1 = tk.Label(frame1, text='Terminal 1')
label_terminal1.grid(row=0, column=0, padx=10, pady=5)

terminal_output1 = scrolledtext.ScrolledText(frame1, wrap=tk.WORD, width=60, height=30)
terminal_output1.config(state=tk.NORMAL)
terminal_output1.grid(row=1, column=0, padx=10, pady=5)

# Frame 3
frame3 = tk.Frame(root)
frame3.grid(row=0, column=2, padx=10, pady=5)

# Label for Terminal 2
label_terminal2 = tk.Label(frame3, text='Terminal 2')
label_terminal2.grid(row=0, column=0, padx=10, pady=5)

terminal_output2 = scrolledtext.ScrolledText(frame3, wrap=tk.WORD, width=60, height=30)
terminal_output2.config(state=tk.NORMAL)
terminal_output2.grid(row=1, column=0, padx=10, pady=10)

# Frame 2
frame2 = tk.Frame(root)
frame2.grid(row=0, column=1, padx=10, pady=10)

port_combobox = ttk.Combobox(frame2, values=rtmidi.MidiOut(rtapi=rtmidi.API_UNIX_JACK).get_ports(), width=25)
port_combobox.set("Select MIDI Output Port")
port_combobox.grid(row=0, column=0, pady=20)
port_combobox.bind("<<ComboboxSelected>>", on_port_selected)

button_open1 = tk.Button(frame2, text="Open File to Terminal 1", command=lambda: open_file(terminal_output1))
button_open1.grid(row=1, column=0, pady=10)

button_save2 = tk.Button(frame2, text="Save Terminal 2 to File", command=lambda: save_to_file(terminal_output2))
button_save2.grid(row=2, column=0, pady=10)

button_clear1 = tk.Button(frame2, text="Clear Terminal 1", command=lambda: clear_terminal(terminal_output1))
button_clear1.grid(row=3, column=0, pady=10)

button_clear2 = tk.Button(frame2, text="Clear Terminal 2", command=lambda: clear_terminal(terminal_output2))
button_clear2.grid(row=4, column=0, pady=10)

button_play = tk.Button(frame2, text="Play", command=lambda: play_program_in_thread(terminal_output2))
button_play.grid(row=5, column=0, pady=10)

button_stop = tk.Button(frame2, text="Stop", command=stop_program)
button_stop.grid(row=6, column=0, pady=10)

button_reset_midi = tk.Button(frame2, text="Reset MIDI", command=reset_midi_program)
button_reset_midi.grid(row=7, column=0, pady=9)

button_exit = tk.Button(frame2, text="Exit", command=exit_program)
button_exit.grid(row=8, column=0, pady=10)

root.mainloop()
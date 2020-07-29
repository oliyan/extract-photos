import os
import shutil
import tkinter as tk

window_height = 400
window_width = 750
window_title = 'Extract shortlisted photos - by Oliyan'


# This function does the actual copying of files.
def process(entry1, entry2, entry3):
    selected_pics = entry1.replace('\\', '/')  # Replace the forward slash to backward slash
    main_source = entry2.replace('\\', '/')    # so that the shutil will work
    job_source = entry3.replace('\\', '/')

    n = 0
    # For every file in the raw image directory
    for file in os.listdir(main_source):
        # Extract only the file name without the extension
        name = file.split(".")[0]

        # For every jpg-file in the client selected Directory
        for jpg in os.listdir(selected_pics):
            # If the jpg name matches with source name
            if jpg.startswith(name):
                # Copy the file to the job Directory
                this_RAW_image = main_source + "/" + file
                shutil.copy(this_RAW_image, job_source)
                if n == 0:
                    print("Copying files, please wait...")
                    # Need to add a counter that counts the no. of files that got copied
                    # This counter has to be printed on a 'read only field' on the app.
                    # such as 'nnn files copied successfully'
                n = n + 1


# This function clears the input field entries
def clear_fields():
    entry1.delete(first=0, last=100)
    entry2.delete(first=0, last=100)
    entry3.delete(first=0, last=100)


root = tk.Tk()
root.title(window_title)

root.resizable(width=False, height=False)   # don't allow users to resize the window

# Place an empty canvas in light blue color
canvas = tk.Canvas(root, height=window_height, width=window_width, bg='#cdecfa')
canvas.pack()

# Place a frame inside the canvas in which all the elements will be placed
frame1 = tk.Frame(root)
frame1.place(relx=0.1, rely=0.1, relwidth=0.8, relheight=0.8)

# Place the background image (the image has to be in png format)
bgm = tk.PhotoImage(file='bgm.png')
bg_label = tk.Label(frame1, image=bgm)
bg_label.place(relwidth=1, relheight=1)

# Display label1 and entry field - selected pics
label1 = tk.Label(frame1, text='Enter the Selected Pics location', bg='#80c1ff', font=30)
label1.place(rely=0.1)
entry1 = tk.Entry(frame1, bg='#d6d2d0', width=100)
entry1.place(rely=0.17)

# Display label2 and entry field - main source
label2 = tk.Label(frame1, text='Enter the Main Source location', bg='#80c1ff', font=30)
label2.place(rely=0.3)
entry2 = tk.Entry(frame1, bg='#d6d2d0', width=100)
entry2.place(rely=0.37)

# Display label3 and entry field - job source
label3 = tk.Label(frame1, text='Enter the Job Source location', bg='#80c1ff', font=30)
label3.place(rely=0.5)
entry3 = tk.Entry(frame1, bg='#d6d2d0', width=100)
entry3.place(rely=0.57)

# Submit button - calls the function process()
button = tk.Button(frame1, text='Create Job Source', font=40,
                   command=lambda: process(entry1.get(), entry2.get(), entry3.get()))
button.place(relx=0.4, rely=0.8)

# Exit button - calls the function exit()
exit_button = tk.Button(frame1, text='Exit', command=lambda: exit())
exit_button.place(relx=0.95, rely=0.9)

# Clear button - calls the function clear_fields()
clear_button = tk.Button(frame1, text='Reset', command=clear_fields)
clear_button.place(relx=0.05, rely=0.9)

root.mainloop()

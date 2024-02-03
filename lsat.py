import re
import pandas as pd
import pdfplumber
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd


class Parse():
    
    def __init__(self):
        super.__init__()

    @classmethod
    def ans(self, path):

        # pdf magic
        with pdfplumber.open(path) as pdf:
            page = pdf.pages[34]
            data = str(page.extract_text())

        # create dataframe and modify rows
        df = pd.DataFrame(data.split())
        df = df.drop(df.index[[0, 1]])
        pat = r"(?=[a-zA-Z]+)(?=I)"
        filter = df[0].str.contains(pat)
        df = df[~filter]


        # create two columns and sections
        df[0] = df[0].str.replace(".", "", regex=False)
        df = df.reset_index(drop=True)
        q =  pd.DataFrame(df[0].str.extractall("(\d+)").unstack()).reset_index(drop=True)
        a =  pd.DataFrame((df[0].str.extractall("([a-zA-Z])").unstack())).reset_index(drop=True)            
        q = q.dropna(axis=1)
        a = a.dropna(axis=1)
        df = df.drop(0, axis=1)

        # create columns
        df["Questions"] = q.astype(int)
        df["Answers"] = a
        df = df.dropna(axis=0)

        # add section column
        sec = 0
        for i, val in enumerate(df["Questions"]):
            if val == 1:
                sec += 1
            df.loc[i, "Section"] = sec
    
        # sort columns
        df = df.sort_values(
            ["Section", "Questions"],
            ascending = [True, True]
            )
        df = df.reset_index(drop=True)
        df["Questions"] = df["Questions"].astype(int)
        df["Index"] = range(1, len(df)+1)
        df["Choice"] = None
        df["Correct"] = False   
        df["Widget"] = None
        df["Tab"] = None     

        print(df)

        return df

    
    @classmethod
    def score(self):
        arr = \
        [
        [180,100,101], [179,99,99],   [178,98,98],   [177,97,97], 
        [176,97,97],   [174,95,95],   [173,94,94],   [172,93,93], 
        [171,92,92],   [170,91,91],   [169,89,90],   [168,88,88],
        [167,87,87],   [166,85,86],   [165,84,84],   [164,82,83],
        [163,81,81],   [162,79,80],   [161,77,78],   [160,75,76],
        [159,74,74],   [158,72,73],   [157,70,71],   [156,68,69], 
        [155,66,67],   [154,65,65],   [153,63,64],   [152,61,62], 
        [151,59,60],   [150,57,58],   [149,55,56],   [148,54,54], 
        [147,52,53],   [146,50,51],   [145,48,49],   [144,47,47], 
        [143,45,46],   [142,43,44],   [141,42,42],   [140,40,41], 
        [139,38,39],   [138,37,37],   [137,35,36],   [136,34,34], 
        [135,33,33],   [134,31,32],   [133,30,30],   [132,29,29], 
        [131,28,28],   [130,27,27],   [129,25,26],   [128,24,24], 
        [127,23,23],   [126,24,24],   [125,22,22],   [124,21,21], 
        [123,20,20],   [122,19,19],   [121,18,18],   [120,0,17,]
        ]
        df = pd.DataFrame(arr)
        df = df.rename(columns={
            0: "Score", 1: "R1", 2: "R2"
        })

        return df

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        # main self window
        self.title("LSAT Grader Pro")
        self.config(background="#FFFFFF")
        self.geometry("450x500")
        self.iconbitmap(r"C:\Users\samue\OneDrive\Coding Projects\Python-Projects\lsat pro\red-apple-icon-8.ico")
        self.resizable(0, 1)
        self.rowconfigure(2, weight=5)

        # padding for widgets using the grid layout
        self.theme = {'style': 'Accent.TButton'}
        self.card = {'style': 'Card.TFrame'}
        self.paddings = {'padx': 5, 'pady': 5}
        self.sticky = {'sticky': 'nsew'}

        # constants
        self.df = pd.DataFrame()
        self.bool = False

        # import theme package --azure
        self.tk.call("source", r"C:\Users\samue\OneDrive\Coding Projects\Python-Projects\lsat pro\Azure-ttk-theme-main\Azure-ttk-theme-main\azure.tcl")
        self.tk.call("set_theme", "light")
        
        self.create_widgets()

    def all_children(self, wid):

        _list = wid.winfo_children()

        for item in _list:
            if item.winfo_children():
                _list.extend(item.winfo_children())

        return _list

    def create_widgets(self):

        def browse():

            # clear entry box
            entry.delete(0, "end")

            # show the open file dialog
            file = fd.askopenfile(
                            mode='r',
                            initialdir=r"C:\Users\samue\OneDrive\LSAT\1-80 PT Original"
                            )

            entry.insert("end", file.name)

        def test():
             
            def test_create_widgets():

                def hide_switch():
                    if self.bool:
                        self.bool = False
                    else:
                        self.bool = True
                    print(f"Hide Answers: {self.bool}")        
                    
                def grade():

                    # grab dataframes
                    df = self.df
                    s = Parse.score()

                    # get score
                    i = df["Correct"].sum()
                    value = s["R2"].sub(i).abs().idxmin()
                    score = s.loc[value, "Score"]
                    final_score.configure(
                        text=f"Final Score {score}", font=("Sans-Serif", 14, "bold"))

                    # section scores
                    for i in [1, 2, 3, 4]:

                        # get tab widgets
                        tab_index = df.loc[df["Section"] == i, "Tab"].first_valid_index()
                        tab = self.nametowidget(df.loc[tab_index, "Tab"])

                        # calculate sectionscore and update tabs
                        total = df.loc[df["Section"] == i].shape[0]
                        right = df.loc[df["Section"] == i, "Correct"].sum()
                        sec_score_button = ttk.Label(
                            tab, text=F"{right}/{total} Correct", style="Toggle.TButton")
                        sec_score_button.grid(
                            row=0, column=0, columnspan=7, **self.paddings, **self.sticky)
                    

                    # change states
                    if self.bool is False:
                        for widget in self.all_children(notebook):
                            match = re.search("radio", f"{widget}")
                            if bool(match):
                                q, a = f"{widget}".split(".radio_")[1].split("_")
                                name = df.loc[int(q)-1, "Widget"]
                                switch = self.nametowidget(name)
                                if df.loc[int(q)-1, "Correct"] == True:
                                    right = re.search(a, df.loc[int(q)-1, "Answers"])
                                    if bool(right):
                                        switch.configure(foreground="green", text=u'\u2714')
                                else:
                                    switch.configure(foreground="red", text=u'\u274C')
                                
                # create instance frames
                frame2 = ttk.Frame(self, **self.card)
                frame3 = ttk.Frame(self, **self.card)
                frame2.grid(row=1, column=0, **self.paddings, **self.sticky)
                frame3.grid(row=2, column=0, **self.paddings, **self.sticky)

                # create test tabs
                notebook = ttk.Notebook(frame3)
                notebook.pack(fill="both", expand=True, **self.paddings)
                for i in [1, 2, 3, 4]:
                    tabs(master=notebook, i=i, df=self.df)

                # create widgets
                grade = ttk.Button(
                    frame2, text="Grade", **self.theme, command=grade)
                hide_answer = ttk.Checkbutton(
                    frame2, text="Hide", style="Switch.TCheckbutton", command=hide_switch)
                final_score = ttk.Label(frame2)

                # orient
                grade.grid(row=0, column=0, **self.paddings, **self.sticky)
                hide_answer.grid(row=0, column=1, **self.paddings, **self.sticky)
                final_score.grid(row=0, column=2, **self.paddings, **self.sticky)

            def tabs(master, i, df):

                def update(var):

                    df = self.df
                    i = str(var.get()).split()
                    df.loc[df["Index"] == int(i[0]), "Choices"] = str(i[1])
                    if  str(i[1]) == df.loc[int(i[0])-1, "Answers"]:
                        df.loc[int(i[0])-1, "Correct"] = True
                    else:
                        df.loc[int(i[0])-1, "Correct"] = False

                # tabs
                tab = ttk.Frame(master, name=f"tab_{i}")
                master.add(tab, text=f"Section {i}")

                # scroll frame
                canvas = tk.Canvas(tab)
                scroll = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
                scroll_frame = ttk.Frame(canvas, name=f"tab_frame_{i}")
                df.loc[df["Section"] == i, "Tab"] = scroll_frame

                # bind
                scroll_frame.bind(
                    "<Configure>",
                    lambda e: canvas.configure(
                        scrollregion=canvas.bbox("all")
                    )
                )
                canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
                canvas.configure(yscrollcommand=scroll.set)

                # orient frames and scrollbar
                canvas.pack(side="left", fill="both", expand=True, **self.paddings)
                scroll.pack(side="right", fill="y", expand=True)   

                # populate array of buttons
                for x, _ in enumerate(df.loc[df["Section"] == i, "Questions"], start=1):
                    index = df[(df["Questions"]  == x) & (df["Section"] == i)].index.tolist()[0] + 1
                    var = tk.StringVar(value=str(index))
                    for num, char in enumerate(["A", "B", "C", "D", "E"], start=1):
                        answer = ttk.Radiobutton(
                            scroll_frame, 
                            text=char, 
                            value=f"{index} {char}",
                            name=f"radio_{index}_{char}",
                            variable=var, 
                            command=lambda e=var: update(e)
                            )
                        answer.grid(row=int(x), column=num, **self.paddings, **self.sticky)


                    # create instance widgets
                    question = tk.Label(
                        scroll_frame, name=str(index), text=int(x), width=2, font=("Sans-Serif", 10))
                    question.grid(row=int(x), column=0, **self.paddings, **self.sticky)
                    grade_label = tk.Label(
                        scroll_frame, font=("Sans-Serif", 10, "bold"), name=f"grade_{index}")
                    grade_label.grid(row=int(x), column=6, **self.paddings, **self.sticky)
                    df.loc[int(index)-1, "Widget"] = grade_label
                    
            #set dataframe and call instance widgets
            file = entry.get()
            self.df = Parse.ans(path=file)
            test_create_widgets()

        # create frames
        frame1 = ttk.Frame(self, **self.card)
        
        # create widgets
        browse = ttk.Button(frame1, text="Browse", **self.theme, command=browse)
        entry = ttk.Entry(frame1)
        save = ttk.Button(frame1, text="Save", **self.theme, command=test)

        # orientation
        frame1.grid(row=0, column=0, **self.paddings, **self.sticky)
        browse.grid(row=0, column=0, **self.paddings, **self.sticky)
        entry.grid(row=0, column=1, **self.paddings, **self.sticky)
        save.grid(row=0, column=2, **self.paddings, **self.sticky)


if __name__ == "__main__":
    app = App()
    app.mainloop()
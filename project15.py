# day15_netflix_eda_gui.py
# GUI EDA Viewer for Netflix Dataset (Day 15 of 30-Day Challenge)

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tkinter import Tk, Label, Button, filedialog, Frame, Scrollbar, Canvas
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from wordcloud import WordCloud, STOPWORDS

sns.set(style="whitegrid")

class NetflixEDAApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Netflix EDA Dashboard")
        self.root.geometry("1200x800")

        Label(root, text="Netflix Exploratory Data Analysis", font=("Arial", 18, "bold")).pack(pady=10)

        Button(root, text="Load Netflix CSV", command=self.load_data, bg="#4CAF50", fg="white", font=("Arial", 12)).pack(pady=5)
        self.frame = Frame(root)
        self.frame.pack(fill="both", expand=True)

        # add scrollbars
        self.canvas = Canvas(self.frame)
        self.scroll_y = Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)
        self.scroll_y.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.configure(yscrollcommand=self.scroll_y.set)

        self.inner_frame = Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")
        self.inner_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

    def load_data(self):
        file_path = filedialog.askopenfilename(title="Select Netflix CSV", filetypes=[("CSV Files", "*.csv")])
        if not file_path:
            return

        self.df = pd.read_csv(file_path)
        self.preprocess()
        self.show_all_plots()

    def preprocess(self):
        data = self.df.copy()
        data.columns = data.columns.str.strip().str.lower().str.replace(' ', '_')
        data['date_added'] = pd.to_datetime(data['date_added'], errors='coerce')
        data['added_year'] = data['date_added'].dt.year
        data['added_month'] = data['date_added'].dt.month
        data['duration_num'] = data['duration'].str.extract(r'(\d+)').astype(float)
        data['duration_unit'] = data['duration'].str.replace(r'^\d+\s*', '', regex=True).str.strip()
        for col in ['director','cast','country','rating','listed_in','description']:
            data[col] = data[col].fillna('Unknown')
        data['is_movie'] = (data['type'].str.lower() == 'movie')
        self.data = data

    def plot_to_frame(self, fig, title):
        Label(self.inner_frame, text=title, font=("Arial", 14, "bold")).pack(pady=5)
        canvas = FigureCanvasTkAgg(fig, master=self.inner_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=5)

    def show_all_plots(self):
        for widget in self.inner_frame.winfo_children():
            widget.destroy()

        d = self.data

        # 1 Type Distribution
        fig1 = plt.Figure(figsize=(6,4))
        sns.countplot(data=d, x='type', palette='viridis', ax=fig1.add_subplot(111))
        fig1.suptitle("Count by Type (Movie/TV Show)")
        self.plot_to_frame(fig1, "Type Distribution")

        # 2 Ratings
        fig2 = plt.Figure(figsize=(8,4))
        ax2 = fig2.add_subplot(111)
        d['rating'].value_counts().nlargest(15).plot(kind='bar', color='skyblue', ax=ax2)
        fig2.suptitle("Top 15 Ratings")
        self.plot_to_frame(fig2, "Ratings")

        # 3 Countries
        fig3 = plt.Figure(figsize=(8,5))
        ax3 = fig3.add_subplot(111)
        top_countries = d['country'].str.split(', ').explode().value_counts().nlargest(15)
        sns.barplot(x=top_countries.values, y=top_countries.index, palette='mako', ax=ax3)
        fig3.suptitle("Top 15 Countries")
        self.plot_to_frame(fig3, "Countries")

        # 4 Genres
        fig4 = plt.Figure(figsize=(8,6))
        ax4 = fig4.add_subplot(111)
        genres = d['listed_in'].str.split(', ').explode().value_counts()
        sns.barplot(x=genres.values[:15], y=genres.index[:15], palette='crest', ax=ax4)
        fig4.suptitle("Top Genres")
        self.plot_to_frame(fig4, "Genres")

        # 5 Titles per Year
        fig5 = plt.Figure(figsize=(8,4))
        ax5 = fig5.add_subplot(111)
        added_per_year = d['added_year'].value_counts().sort_index()
        added_per_year.plot(marker='o', ax=ax5)
        fig5.suptitle("Titles Added per Year")
        self.plot_to_frame(fig5, "Titles per Year")

        # 6 Release Year Distribution
        fig6 = plt.Figure(figsize=(8,4))
        ax6 = fig6.add_subplot(111)
        sns.histplot(d['release_year'].dropna().astype(int), bins=40, color='purple', ax=ax6)
        fig6.suptitle("Release Year Distribution")
        self.plot_to_frame(fig6, "Release Year Distribution")

        # 7 WordCloud
        desc = ' '.join(d['description'].dropna().tolist()).lower()
        stopwords = set(STOPWORDS)
        wc = WordCloud(width=800, height=400, background_color='white', stopwords=stopwords).generate(desc)

        fig7 = plt.Figure(figsize=(10,5))
        ax7 = fig7.add_subplot(111)
        ax7.imshow(wc, interpolation="bilinear")
        ax7.axis("off")
        fig7.suptitle("WordCloud of Descriptions")
        self.plot_to_frame(fig7, "WordCloud")

        Label(self.inner_frame, text="✅ EDA Complete!", font=("Arial", 14, "bold"), fg="green").pack(pady=10)


if __name__ == "__main__":
    root = Tk()
    app = NetflixEDAApp(root)
    root.mainloop()

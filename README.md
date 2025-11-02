# SaveCodeX

## Details
This is a desktop app is made to make coding work for college smoother and less repetitive.
- Save Code: paste and save code instantly.
  - Select an extention, then your folder, It will automatically pick a number based on the files in the given folder
  - AI On: it will save the file as `num_discription.ext`
  - AI Off: it will instantly save the file as `num.ext`
  - The num will automatically increment as you paste more files!
- DOCX Generator: turn saved code into Word report.
  - Select a folder and the language the code's written in
  - This will automatically run through every file in that folder, sort it in numerical ascending order, compile it, run the code in a new terminal and take screenshot of it
  - It will then generate a docx file with a Header and description of choosing and contain all of your code with their outputs in order
- Settings

## Run Locally
```
git clone https://github.com/kartinul/save-code-x.git
cd save-code-x
python -m venv venv
\venv\Scripts\activate
pip install -r requirements.txt
````
Then make a new file `.env` with the contents
```
OPENAI_KEY = YOUR_OPEN_AI_KEY
```
and run with 
```
python main.py
```

## Build

Activate venv and install PyInstaller
Then build with: `python -m PyInstaller .\main.py --onefile --noconsole --add-data "languages.json;."`

## Demo
https://youtu.be/zmnwcFAomLw
https://youtu.be/_SVnLpMCFvE

<a href="https://www.flaticon.com/free-icons/code" title="code icons">Code icons created by Smashicons - Flaticon</a>

# ForestGuard AI — Dynamic Final

## Important change
The Analytics graphs are now fully dynamic. They contain NO preset/static values.

### AI Detection graph
Every time you upload an image and click **Run AI Scan**, the actual model's deforestation probability becomes the next graph point.

### Before/After graph
Every time you upload Before and After images and click **Compare Images**, the actual calculated vegetation-loss percentage becomes the next graph point.

### Persistence
All readings are stored in `reports/history.json`, so the graph keeps its readings after restarting the Flask server.

### Reports
A separate report is automatically generated for every completed AI Detection and Before/After analysis.

### Run
```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe app.py
```
Then open http://127.0.0.1:5000

Developer: Mr. V. Sri Ram

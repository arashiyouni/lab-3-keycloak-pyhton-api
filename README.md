## How to run API

1. 🔌 Activate the Virtual Environment

**On windows**
```python
lab3-env\Scripts\activate 
```
**On Linux/macOS**

```
source lab3-env/bin/activate
```


2. 🍞 Install Dependencies

```python
pip install -r requirements.txt
```

3. 🧑‍🦽 Start the API with Uvicorn:

```python
uvicorn main:app --reload --port 8000    
```
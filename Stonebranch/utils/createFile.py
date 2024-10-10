import json

def createJson(filename, data):
    try:
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4)
        print(f"{filename} created successfully")
    except Exception as e:
        print(f"Error creating {filename}: {e}")
        
def createXml(filename, data):
    try:
        with open(filename, 'w') as file:
            file.write(data)
        print(f"{filename} created successfully")
    except Exception as e:
        print(f"Error creating {filename}: {e}")
        
def createText(filename, data):
    try:
        with open(filename , 'wb') as file:
            file.write(data)
        print(f"{filename} created successfully")
    except Exception as e:
        print(f"Error creating {filename}: {e}")
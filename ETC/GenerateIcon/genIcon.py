from PIL import Image
import os




def generateIcon(icon_path, output_path, size):
    icon = Image.open(icon_path)
    icon = icon.resize((size, size))
    icon.save(output_path)




def main():
    icon_path = input("Enter the path of the icon: ")
    output_path = input("Enter the output path: ")
    output_file_name = input("Enter the output file name: ")
    output_path = os.path.join(output_path, output_file_name)
    icon_size = int(input("Enter the size of the icon: "))
    
    if not os.path.exists(icon_path):
        print("Icon path not found")
        return
    
    generateIcon(icon_path, output_path, icon_size)
    print("Icon generated")
    
    
if __name__ == "__main__":
    main()
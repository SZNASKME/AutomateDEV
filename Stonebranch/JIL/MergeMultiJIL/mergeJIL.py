import sys
import os


sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

output_file = 'outputJIL_ATS_FLPN.txt'


def main():
    
    folder_path = input("Enter the folder path: ")
    
    
    with open(output_file, 'w') as outfile:
        # Loop through all files in the folder
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            
            # Check if it's a file (not a directory)
            if os.path.isfile(file_path):
                # Read the contents of the file and write to the output file
                with open(file_path, 'r') as infile:
                    outfile.write(infile.read())
                    outfile.write("\n")  # Optional: add newline between files' contents
        
            
if __name__ == "__main__":
    main()










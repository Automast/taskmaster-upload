import os
import requests
import sys

# Change SERVER_URL to your railway URL later or keep it as localhost for now
SERVER_URL = "http://localhost:3000"

def upload_files():
    # Looks for a folder called "output"
    output_dir = "output"
    
    if not os.path.exists(output_dir):
        # Fallback 1: Check in the directory above
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_output = os.path.join(os.path.dirname(current_dir), "output")
        
        # Fallback 2: Check inside the speedrun folder 
        speedrun_output = r"c:\Users\pc\Desktop\taskmaster videos\speedrun\output"
        
        if os.path.exists(parent_output):
             output_dir = parent_output
        elif os.path.exists(speedrun_output):
             output_dir = speedrun_output
        else:
             print(f"Error: '{output_dir}' directory not found anywhere. Please run this script from the directory containing the 'output' folder.")
             return

    print(f"Using output directory: {output_dir}")

    # User wants to upload folders *in* output folder
    folders = [f for f in os.listdir(output_dir) if os.path.isdir(os.path.join(output_dir, f))]
    if not folders:
        print(f"No folders found inside '{output_dir}'.")
        return

    for folder_name in folders:
        folder_path = os.path.join(output_dir, folder_name)
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        
        if not files:
            print(f"Folder '{folder_name}' is empty. Skipping.")
            continue
            
        print(f"\nUploading from folder '{folder_name}'...")
        for filename in files:
            file_path = os.path.join(folder_path, filename)
            print(f"  Uploading {filename}...")
            
            try:
                with open(file_path, 'rb') as f:
                    files_payload = {'file': (filename, f)}
                    data_payload = {'folderName': folder_name}
                    response = requests.post(f"{SERVER_URL}/upload", files=files_payload, data=data_payload)
                    
                    if response.status_code == 200:
                        print(f"  Success: {response.json().get('filename')}")
                    else:
                        print(f"  Failed: HTTP {response.status_code} - {response.text}")
            except Exception as e:
                print(f"  Error uploading {filename}: {e}")

def clear_server_files():
    try:
        response = requests.get(f"{SERVER_URL}/folders")
        if response.status_code != 200:
            print("Failed to get folders from server.")
            return
        
        folders = response.json().get('folders', [])
        if not folders:
            print("No folders found on the server.")
            return
            
        print("\nFolders on server:")
        for idx, folder in enumerate(folders):
            print(f" {idx + 1}. {folder}")
            
        choice = input("\nEnter the number of the folder to clear files from (or 0 to cancel): ").strip()
        if not choice.isdigit():
            print("Invalid input.")
            return
            
        choice_idx = int(choice) - 1
        if 0 <= choice_idx < len(folders):
            folder_to_clear = folders[choice_idx]
            confirm = input(f"Are you sure you want to delete all files in '{folder_to_clear}'? (y/n): ").strip().lower()
            if confirm == 'y':
                del_resp = requests.delete(f"{SERVER_URL}/folders/{folder_to_clear}")
                if del_resp.status_code == 200:
                    print(f"Successfully cleared all files in '{folder_to_clear}'.")
                else:
                    print(f"Failed to clear files: {del_resp.text}")
            else:
                print("Cancelled.")
        elif choice_idx == -1:
            print("Cancelled.")
        else:
            print("Invalid number.")
            
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server. Is it running?")
    except Exception as e:
        print(f"Error communicating with server: {e}")

def main():
    print("=== Video Uploader ===")
    choice = input("Do you want to upload? (1 for yes, anything else for no): ").strip()
    
    if choice == '1':
        upload_files()
    else:
        clear_choice = input("Do you want to clear files on the server? (y/n): ").strip().lower()
        if clear_choice == 'y':
            clear_server_files()
            
    print("\nDone.")

if __name__ == "__main__":
    main()

import os
import gdown



def download_weights(google_drive_file_id: str, output_file_name):
    """
    google_drive_file: Id of you google drive file that contains the pytorch
                        weights of your model, stored as a state dictionary
    
    output_file_name: the name of the file to store the weights in once downloaded
    """
    if not os.path.exists(output_file_name):
        print("Downloading model from Google Drive...")
        gdown.download(f"https://drive.google.com/uc?id={google_drive_file_id}", output_file_name, quiet=False)

    
import streamlit as st
from PIL import Image
import pillow_avif # plugin which will allow pillow to open avif images, just in case
from stegano import lsb
import uuid
import os
import base64
import requests

os.makedirs("clean", exist_ok=True)
os.makedirs("text", exist_ok=True)
os.makedirs("stegano", exist_ok=True)

############ for auto upload of files to github that be used as  train data of model ####################3

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]  # store securely as env var
REPO = "prince-musonda/Steganography-image-detector"
BRANCH = "main"

def upload_to_github(local_file_path, repo_path, commit_message):
    with open(local_file_path, "rb") as f:
        content = base64.b64encode(f.read()).decode()

    url = f"https://api.github.com/repos/{REPO}/contents/{repo_path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    data = {
        "message": commit_message,
        "content": content,
        "branch": BRANCH
    }

    response = requests.put(url, json=data, headers=headers)
    if response.status_code in [201, 200]:
        print(f"✅ Uploaded {repo_path}")
    else:
        print(f"❌ Failed to upload {repo_path}: {response.json()}")


###################### UI#################################
st.title("stagnography image creator")
uploaded_file = st.file_uploader("Please provide an image that you want to check if it has hidden information in it",
                                 type=["webp", "jpg","jpeg","png", "svg","gif", "avif", "bmp"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image)

secret_message = st.text_input("Please provide your secret mesage over here, it will be encoding using lsb")

if uploaded_file and secret_message:
    # Convert image to PNG and store it
    image = Image.open(uploaded_file).convert("RGB")
    unique_name = str(uuid.uuid4())
    clean_image_path = os.path.join("clean", f"{unique_name}.png")
    text_path = os.path.join("text", f"{unique_name}.txt")
    stegano_image_path = os.path.join("stegano", f"{unique_name}.png")

    #save image
    image.save(clean_image_path)
    with open(text_path, "w") as file:
        file.write(secret_message)  
    if st.button("Hide message in the image",type="primary"):
        secret_image = lsb.hide(clean_image_path,message=secret_message)
        secret_image.save(stegano_image_path)
        # Upload files to GitHub
        upload_to_github(clean_image_path, f"clean/{unique_name}.png", "Add clean image")
        upload_to_github(text_path, f"text/{unique_name}.txt", "Add secret message")
        upload_to_github(stegano_image_path, f"stegano/{unique_name}.png", "Add stego image")

        # Provide download link
        with open(stegano_image_path, "rb") as file:
            btn = st.download_button(
                label="Download Stego Image",
                data=file,
                file_name=f"stego_{unique_name}.png",
                mime="image/png"
            )


               
           


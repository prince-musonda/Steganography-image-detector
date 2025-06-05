import streamlit as st
import torch
from torch import nn
from torchvision import models
from stegano import lsb
from PIL import Image
import os
import uuid
import pillow_avif # plugin which will allow pillow to open avif images, just in case
from helper_function import download_weights

# set up  model
device = "cuda" if torch.cuda.is_available() else "cpu"
model = models.efficientnet_b5()
img_transforms = models.EfficientNet_B5_Weights.DEFAULT.transforms()
model.classifier = nn.Sequential(
    nn.Dropout(p=0.2, inplace=True),
    nn.Linear(in_features=2048,out_features=2)
)
model.to(device)

# download weights
model_weights_file = "model_weights.pt"
download_weights(google_drive_file_id="1-kXWiHRKbZsj2LcPMnSSHe7efzhKFYrH",output_file_name=model_weights_file)
model.load_state_dict(torch.load(model_weights_file, map_location=device))

# prediction function
def predict(image, transforms = img_transforms, device=device):
    model.eval()
    with torch.inference_mode():
        # transform image
        transformed_image = transforms(image).to(device)
        transformed_image.unsqueeze_(dim=0)
        print(transformed_image.shape)
        prediction = model(transformed_image)
        # turn prediction in propability
        prediction = torch.softmax(prediction, dim=-1).squeeze()
        print(prediction)
    return {"clean" : prediction[0].item()*100, "stegano": prediction[1].item()*100}


# hidden message decrption function
def reveal_message(image):
    # convert image to png
    image_name = f"{uuid.uuid4()}.png"
    image.save(image_name)
    try:
        message= lsb.reveal(image_name)
    except:
        message = "Couldn't find any hidden message"
    # delete photo
    os.remove(image_name)
    return message


########################## create UI
st.title("steganography images detector and decryptor")
st.write("Note: even though the model achieved an accuracy of 74 percent on the the" \
            "testing dataset, we struggled to obtain a proper diverse dataset. As a result," \
            "the model was just trained on simple images from the following source:")
st.link_button("Here","https://www.kaggle.com/datasets/marcozuppelli/stegoimagesdataset",icon=':material/exit_to_app:')
st.subheader("However")
st.write("we are now creating a better model and building our own better dataset.")
st.write("But as for now, the models prediction may false on some complicated images")
uploaded_file = st.file_uploader("Please provide an image that you want to check if it has hidden information in it",
                                 type=["webp", "jpg","jpeg","png", "svg","gif", "avif", "bmp"])
if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    col1, col2 = st.columns([3,1],vertical_alignment="center")
    # show image
    with col1:
        st.image(image=image)

    with col2:
        # clasification
        if st.button("Classify this image",type="primary", icon=":material/terminal:"):
            with st.spinner(text="classifying"):
                prediction = predict(image)
            st.write("Probablity of image being clean or being a steganography image according to AI model:")
            st.badge(f"CLEAN: {prediction["clean"]:.2f}%")
            st.badge(f"STEGANO: {prediction["stegano"]:.2f}%",color="green")
        
        # decryption
        if st.button("try decrypting image"):
            with st.spinner():
                secrete_message = reveal_message(image=image)
            st.caption(secrete_message)

    
            


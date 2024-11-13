import os
import io
import requests
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image

# Load environment variables
load_dotenv(".env")

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if GOOGLE_API_KEY is None:
    st.error("API Key not found. Please set the GOOGLE_API_KEY in the .env file.")
    st.stop()
    
# Access Google API Key from environment variables
genai.configure(api_key=GOOGLE_API_KEY)

# Function to convert image to byte format with MIME type
def convert_image_to_bytes(image: Image.Image, format: str = "PNG") -> bytes:
    """
    Converts a PIL Image object into bytes format with a specified MIME type.

    Args:
        image (Image.Image): The image to be converted.
        format (str): The format to use for the conversion (e.g., "PNG", "JPEG").

    Returns:
        bytes: The image data in bytes format.
    """
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format=format)  # Save image to BytesIO object
    img_byte_arr = img_byte_arr.getvalue()   # Get bytes from the BytesIO object
    return img_byte_arr

# Function to get Gemini model response based on text and images
def get_gemini_response(images: list[Image.Image], text: str = "What is in this image?") -> None:
    """
    Generates a response using the Gemini model. It sends both user-provided text and a list of images.

    Args:
        images (list[Image.Image]): List of images to analyze.
        text (str): The prompt to send along with the images.

    Returns:
        None: The function directly displays the result or an error message.
    """
    try:
        model = genai.GenerativeModel("gemini-1.5-flash-001")
        
        # Generate the content with both text and images
        response = model.generate_content(
            [{"text": text}] + 
            [{"mime_type": "image/png", "data": convert_image_to_bytes(image)} for image in images]
        )

        # Check if the response has valid parts
        if hasattr(response, 'text') and response.text:
            st.write(response.text)
        else:
            st.write("The content could not be processed due to safety concerns or inappropriate content.")
        
    except ValueError as e:
        # Log the detailed error for debugging
        st.error(f"Error processing the request: {str(e)}")

# Function to resize image to a square of specified size
def resize_image_to_square(image: Image.Image, size: tuple[int, int] = (150, 150)) -> Image.Image:
    """
    Resizes an image to a square of specified size.

    Args:
        image (Image.Image): The image to resize.
        size (tuple[int, int]): The dimensions to resize the image to (width, height).

    Returns:
        Image.Image: The resized image.
    """
    return image.resize(size)

# Main function to handle Streamlit UI and interactions
def main() -> None:
    """
    The main function for the Streamlit app that allows users to upload images, provide input text, and receive
    analysis from the Gemini model. Displays uploaded images and outputs analysis results.
    
    Args:
        None
    
    Returns:
        None
    """
    st.title("Gemini Multi-language Document Extraction")

    # File uploader for multiple image files
    uploaded_files = st.file_uploader("Upload your images for analysis ~", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

    # Check if files were uploaded
    if uploaded_files:
        images = []
        columns = st.columns(len(uploaded_files))
        
        # Process each uploaded image
        for idx, uploaded_file in enumerate(uploaded_files):
            try:
                image = Image.open(uploaded_file)
                resized_image = resize_image_to_square(image)  # Resize to square
                images.append(image)

                # Display each image in a separate column
                with columns[idx]:
                    st.image(resized_image, caption=f'Image: {uploaded_file.name}', use_column_width=True)

            except FileNotFoundError as e:
                st.error(f"Error loading image {uploaded_file.name}: {str(e)}")

        # Get user input text
        text = st.text_input("Input: ", key="input")

        submit = st.button("Tell me")

        if submit:
            if text or images:
                # Call the Gemini Pro model to analyze the uploaded images
                st.write("Results:~")
                get_gemini_response(images, text)
            else:
                st.error("Please Upload at least one image.")
    else:
        st.write("Please upload image files to proceed.")
    
if __name__ == '__main__':
    main()
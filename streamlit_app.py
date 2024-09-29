import streamlit as st
import google.generativeai as genai
import os

# Configure Google Generative AI with the API key
os.environ["API_KEY"] = ""  # Gemini API key
genai.configure(api_key=os.environ["API_KEY"])

# Initialize session state variables
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []
if "genai_files" not in st.session_state:
    st.session_state.genai_files = []

# Function to upload a file
def upload_file(file, display_name):
    try:
        uploaded_file = genai.upload_file(path=file, display_name=display_name)
        return uploaded_file
    except Exception as e:
        st.error(f"Failed to upload {display_name}: {e}")
        return None

# Function to delete a file by ID
def delete_file(file_id):
    try:
        genai.delete_file(file_id)
        st.success(f"Deleted file with ID: {file_id}")
    except Exception as e:
        st.error(f"Error deleting file with ID {file_id}: {e}")

# Streamlit app layout
st.title("Document Upload and Analysis")
st.write("Upload three documents, ask questions, and delete the files when needed.")

# File upload section
uploaded_files = []
for i in range(3):
    file = st.file_uploader(f"Upload Document {i + 1}", type=["pdf"], key=f"file_{i}")
    if file:
        file_path = f"temp_file_{i}.pdf"
        with open(file_path, "wb") as f:
            f.write(file.read())
        uploaded_files.append((file_path, file.name))

# Upload files to Google Generative AI
if st.button("Upload Files"):
    if len(uploaded_files) > 0:
        for path, name in uploaded_files:
            genai_file = upload_file(path, name)
            if genai_file:
                st.session_state.genai_files.append(genai_file)
        st.success("Files uploaded successfully.")
    else:
        st.warning("Please upload documents.")

# Display list of uploaded files
if st.session_state.genai_files:
    st.write("Uploaded Files:")
    for file in st.session_state.genai_files:
        st.write(f"{file.display_name}, URI: {file.uri}")

# Text input for a specific prompt
prompt = st.text_area("Enter your prompt")

# Provide an answer button to get the response
if st.button("Give Answer"):
    if prompt and len(st.session_state.genai_files) > 0:
        try:
            # Choose the Gemini model
            model = genai.GenerativeModel(model_name="gemini-1.5-pro")
            
            # Generate response using the uploaded files and the prompt
            response = model.generate_content(
                [*st.session_state.genai_files, prompt]
            )
            st.write("Response:")
            st.write(response.text)
        except Exception as e:
            st.error(f"Error generating response: {e}")
    else:
        st.warning("Please upload files and enter a prompt.")

# List and delete files
file_ids = []
if st.button("List Files"):
    try:
        files = genai.list_files()
        st.write("Files:")
        for file in files:
            file_id = file.uri.split('/')[-1]
            file_ids.append(file_id)
            st.write(f"{file.display_name}, URI: {file.uri}")
    except Exception as e:
        st.error(f"Error listing files: {e}")

# Delete all files when required
file_ids = []
if st.button("Delete All Files"):
    # Listing the files and collecting their IDs
    for file in genai.list_files():
        # Extract the file ID from the URI
        file_id = file.uri.split('/')[-1]
        file_ids.append(file_id)
        print(f"{file.display_name}, ID: {file_id}")

    # Step 2: Delete each file using the collected IDs
    for file_id in file_ids:
        try:
            # Delete the file using the ID
            genai.delete_file(file_id)
            st.write(f'Deleted file with ID: {file_id}')
        except Exception as e:
            st.warning(f'Error deleting file with ID {file_id}: {e}')


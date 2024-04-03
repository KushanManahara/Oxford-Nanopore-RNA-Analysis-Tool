import paramiko
import streamlit as st
import time
import os


def login():
    def on_login():
        try:
            ssh_client = create_ssh_connection(
                host, username, password)

            toast_placeholder = st.empty()
            toast_placeholder.success("Login successful!")
            ssh_client.close()
            time.sleep(2)
            toast_placeholder.empty()

            title_placeholder.empty()
            host_placeholder.empty()
            username_placeholder.empty()
            password_placeholder.empty()
            st.session_state.logged_in = True
            st.session_state.host = host
            st.session_state.username = username
            st.session_state.password = password
            st.session_state.ssh_client = ssh_client

        except Exception as e:
            st.error(f"Login failed: {e}")

    title_placeholder = st.empty()
    host_placeholder = st.empty()
    username_placeholder = st.empty()
    password_placeholder = st.empty()
    login_button_placeholder = st.empty()

    title_placeholder.title("Login Page")

    host = host_placeholder.text_input("Host")
    username = username_placeholder.text_input("Username")
    password = password_placeholder.text_input("Password", type="password")

    if host and username and password:
        print(host)
        print(username)
        print(password)
        if not login_button_placeholder.button(
                "Login", on_click=on_login):
            st.error("Invalid hostname, username or password, . Please try again.")

    # if login_status == False:
    # st.error("Invalid username or password. Please try again.")


def create_ssh_connection(host, username, password):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=host, username=username, password=password)
    return ssh_client


def create_project_dir(ssh_client, folder_name):
    ssh_client.exec_command(f'mkdir -p WebApp/{folder_name}')
    ssh_client.exec_command(f'mkdir -p WebApp/{folder_name}/test-dir')
    ssh_client.exec_command(f'mkdir -p WebApp/{folder_name}/EXPORTS')
    ssh_client.exec_command(
        f'echo "Hello World" > WebApp/{folder_name}/hello-world.txt')


def create_zip_folder(ssh_client, folder_path, zip_file_path):
    # Execute the zip command remotely to create the zip file
    ssh_client.exec_command(f'zip -r {zip_file_path} {folder_path}')


def download_zip_file(ssh_client, remote_zip_file_path, local_zip_file_path):
    # Obtain the path to the user's "Downloads" directory
    local_zip_file_path = os.path.expanduser("~/Downloads/remote_zipfile.zip")

    # Execute the scp command remotely to download the zip file
    ssh_client.exec_command(
        f'scp {remote_zip_file_path} {local_zip_file_path}')


def project_init():
    st.title("Project Init Page")
    st.write("Welcome to the Project Init Page! You can start project init here.")


def blasting(host, username, password):
    if not st.button("Back", on_click=logout):
        st.title("Blasting Page")
        folder_name = st.text_input(
            "Project Name")
        uploaded_file = st.file_uploader(
            "Upload FAST5 file as a zip", type=["zip"])

        creating_folder_status = st.empty()
        upload_file_status = st.empty()

        if st.button("Start Blasting"):
            creating_folder_status.info("Creating folder...")
            try:
                ssh_client = create_ssh_connection(
                    host, username, password)
                create_project_dir(ssh_client, folder_name)
                st.success(f"Folder '{folder_name}' created successfully!")
                ssh_client.close()
            except Exception as e:
                creating_folder_status.error(f"An error occurred: {e}")

            if uploaded_file is not None:
                creating_folder_status.empty()
                upload_file_status.info("Uploading file...")
                try:
                    ssh_client = create_ssh_connection(
                        host, username, password)
                    with ssh_client.open_sftp() as sftp:
                        with sftp.file(f"WebApp/{folder_name}/{uploaded_file.name}", "wb") as f:
                            f.write(uploaded_file.getvalue())
                    upload_file_status.success("File uploaded successfully!")

                    create_zip_folder(
                        ssh_client, f"WebApp/{folder_name}", f"WebApp/{folder_name}/EXPORTS/exports.zip")

                    upload_file_status.success("File Downloading...")
                    # Download the folder from the remote server                # Create the zip file on the remote server
                    download_zip_file(
                        ssh_client, f"WebApp/{folder_name}/exports.zip", ".")
                    upload_file_status.success("File Downloaded successfully!")

                except Exception as e:
                    upload_file_status.error(
                        f"An error occurred while uploading file: {e}")
                    ssh_client.close()


# Main function
def logout():
    st.session_state.logged_in = False


def main():
    global ssh_client, host, username, password

    if "logged_in" not in st.session_state:
        host = "localhost"
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        login()

    else:
        blasting(st.session_state.host, st.session_state.username,
                 st.session_state.password)


# Run the main function
if __name__ == "__main__":
    main()

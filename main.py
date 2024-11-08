import os
import subprocess
import time
import threading
import requests
import json

try:
    import pyfiglet
except ImportError:
    print("pyfiglet not found. Installing..")
    subprocess.run(['pip', 'install', 'pyfiglet'])
    import pyfiglet

def print_mcWizard_title():
    custom_fig = pyfiglet.Figlet(font='slant')
    title = custom_fig.renderText('mcWizard')
    print(title)

def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

def update_install():
    print("Updating and installing necessary packages...")
    subprocess.run(["sudo", "apt", "update"])
    subprocess.run(["sudo", "apt", "install", "openjdk-16-jre-headless", "curl", "tmux"])
    print("Installation complete.")

def kill_java_processes():
    print("Killing all Java processes...")
    subprocess.run(["pkill", "-f", "java"])
    print("Java processes killed.")

def get_latest_stable_build(project, minecraft_version):
    api_url = f"https://api.papermc.io/v2/projects/{project}/versions/{minecraft_version}/builds"
    response = requests.get(api_url)
    builds = response.json().get("builds", [])
    stable_builds = [build["build"] for build in builds if build["channel"] == "default"]
    return max(stable_builds, default=None)

def download_latest_stable_build(project, minecraft_version):
    print("Downloading server...")
    latest_build = get_latest_stable_build(project, minecraft_version)
    if latest_build is not None:
        jar_name = f"paper-{minecraft_version}-{latest_build}.jar"
        api_url = f"https://api.papermc.io/v2/projects/{project}/versions/{minecraft_version}/builds/{latest_build}/downloads/{jar_name}"
        subprocess.run(["curl", "-o", "server.jar", api_url])
        print("Download completed.")
        time.sleep(1)
    else:
        print("Failed to retrieve the latest stable build.")

def check_and_set_eula():
    print("Setting EULA to true...")
    time.sleep(1)
    with open("eula.txt", "r") as file:
        data = file.read()
    if "eula=false" in data:
        data = data.replace("eula=false", "eula=true")
        with open("eula.txt", "w") as file:
            file.write(data)
    time.sleep(1)
    print("EULA set to true.")
    time.sleep(1)

def start_minecraft_server():
    if not os.path.exists("eula.txt"):
        print("EULA file not found. Starting the server...")
        time.sleep(2)
        subprocess.run(["tmux", "new-session", "-d", "-s", "minecraft", "java", "-Xmx1024M", "-Xms512M", "-jar", "server.jar", "nogui"])
        print("Server started.")
        time.sleep(5)
        print("EULA needs to be accepted. Please continue with task 4 & 5.")
        time.sleep(5)
        return

    with open("eula.txt", "r") as eula_file:
        eula_content = eula_file.read()

    if "eula=true" in eula_content:
        print("Server is starting...")
        subprocess.run(["tmux", "new-session", "-d", "-s", "minecraft", "java", "-Xmx1024M", "-Xms512M", "-jar", "server.jar", "nogui"])
        print("Server started.")
        time.sleep(1)
        print("Loading...")
        time.sleep(5)
        print("Loading...")
        time.sleep(5)
        print("Loading...")
        time.sleep(5)
        print("Loading...")
        time.sleep(5)
        print("Loaded...")
    else:
        print("EULA needs to be accepted. Please check the eula.txt file.")
        time.sleep(1)

def create_start_script():
    print("Creating start script...")
    time.sleep(1)
    with open("start_server.sh", "w") as file:
        file.write("#!/bin/bash\njava -Xmx1024M -Xms512M -jar server.jar nogui")
    subprocess.run(["chmod", "+x", "start_server.sh"])
    time.sleep(1)
    print("Start script created.")
    time.sleep(1)

def install_ngrok():
    print("Installing ngrok...")
    run_command("curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null")
    run_command('echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list')
    run_command("sudo apt update && sudo apt install ngrok")
    print("Ngrok installed.")
    time.sleep(1)

def configure_ngrok(auth_token):
    print("Configuring ngrok with auth token...")
    run_command(f"ngrok config add-authtoken {auth_token}")
    print("Ngrok configured with auth token.")
    time.sleep(1)

def start_ngrok():
    print("Starting ngrok in a new tmux session...")

    # Check if ngrok is installed
    ngrok_version = run_command("ngrok version")
    if "command not found" in ngrok_version:
        print("Error: ngrok is not installed. Please install ngrok first.")
        return
    
    # Start ngrok in a new tmux session
    ngrok_command = "tmux new-session -d -s ngrok 'ngrok tcp 25565'"
    result = subprocess.run(ngrok_command, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("Ngrok started in tmux session.")
    else:
        print(f"Failed to start ngrok in tmux session: {result.stderr}")

    time.sleep(1)


# Verify the session creation
def check_ngrok_session():
    result = run_command("tmux list-sessions | grep ngrok")
    if result:
        print("Ngrok session is running.")
    else:
        print("Error: Ngrok session is not running. Please check the logs for more details.")


def close_server_and_ngrok():
    print("Closing the server and ngrok...")
    run_command("sudo pkill ngrok")
    run_command("sudo pkill -9 java")
    print("Server and ngrok closed.")
    time.sleep(1)

def send_in_game_command():
    while True:
        in_game_command = input("Enter in-game command (type 'exit' to return to the menu): ")
        if in_game_command.lower() == 'exit':
            break
        subprocess.run(["tmux", "send-keys", "-t", "minecraft", f"{in_game_command}\n"])

def open_console():
    result = run_command("tmux list-sessions | grep minecraft")
    if not result:
        print("Error: The Minecraft server is not running. Cannot access the console.")
        time.sleep(1)
    else:
        print("Opening Console GUI...")
        time.sleep(1)
        print("Press Ctrl + B, then D to exit the console GUI and return to the menu.")
        time.sleep(2)
        subprocess.run(["tmux", "attach-session", "-t", "minecraft"])

def open_ngrok_console():
    check_ngrok_session()
    print("Opening Ngrok Console...")
    time.sleep(1)
    print("Press Ctrl + B, then D to exit the ngrok console and return to the menu.")
    time.sleep(2)
    subprocess.run(["tmux", "attach-session", "-t", "ngrok"])

def check_server_status():
    print("Checking server status...")
    result = run_command("tmux list-sessions | grep minecraft")
    if result:
        print("Minecraft server is running.")
    else:
        print("Minecraft server is not running.")

    result_ngrok = run_command("pgrep -x ngrok")
    if result_ngrok:
        print("Ngrok is running.")
    else:
        print("Ngrok is not running.")
    time.sleep(2)

def update_minecraft_server():
    print("Updating Minecraft server to the latest stable build...")
    download_latest_stable_build("paper", "1.20.4")
    print("Minecraft server updated successfully.")

def download_plugin(link, plugin_folder):
    try:
        response = requests.get(link)
        if response.status_code == 200:
            os.makedirs(plugin_folder, exist_ok=True)
            file_name = os.path.join(plugin_folder, link.split("/")[-1])
            with open(file_name, "wb") as file:
                file.write(response.content)
            print(f"Downloaded plugin to {file_name}")
        else:
            print(f"Failed to download plugin. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error downloading plugin: {e}")

def restart_server():
    print("Restarting the server...")
    close_server_and_ngrok()
    time.sleep(2)
    print("Starting the server..")
    start_minecraft_server()
    start_ngrok()
    time.sleep(1)

def main():
    while True:
        subprocess.run("clear", shell=True)
        print("Script\nMade by Cr0mb\nhttps://github.com/cr0mb")
        print_mcWizard_title()
        print("\nOptions:")
        print("1. update & install")
        print("2. download minecraft server.jar")
        print("3. load eula")
        print("-----------------------------------------------")
        print("4. kill all java processes")
        print("5. check and set eula")
        print("6. create a start script for the server")
        print("7. install and configure ngrok")
        print("-----------------------------------------------")
        print("8. check server status")
        print("9. update Minecraft server to the latest stable build")
        print("10. Download Plugin to Plugin Folder")
        print("11. Restart the server")
        print("12. Send console commands")
        print("-----------------------------------------------")
        print("type 'start' to start the server & ngrok")
        print("type 'stop' to stop the server & ngrok")
        print("type 'exit' to exit script")
        print("type 'msfconsole' to open console gui.")
        print("type 'ngrokconsole' to open ngrok console gui.")

        option = input("Choose an option: ")

        if option == "1":
            thread = threading.Thread(target=update_install)
            thread.start()
            thread.join()
        elif option == "2":
            thread = threading.Thread(target=download_latest_stable_build, args=("paper", "1.20.4"))
            thread.start()
            thread.join()
        elif option == "3":
            thread = threading.Thread(target=start_minecraft_server)
            thread.start()
            thread.join()
        elif option == "4":
            thread = threading.Thread(target=kill_java_processes)
            thread.start()
            thread.join()
        elif option == "5":
            thread = threading.Thread(target=check_and_set_eula)
            thread.start()
            thread.join()
        elif option == "6":
            thread = threading.Thread(target=create_start_script)
            thread.start()
            thread.join()
        elif option == "7":
            auth_token = input("Enter ngrok auth token: ")
            thread1 = threading.Thread(target=install_ngrok)
            thread2 = threading.Thread(target=configure_ngrok, args=(auth_token,))
            thread1.start()
            thread1.join()
            thread2.start()
            thread2.join()
        elif option == "8":
            thread = threading.Thread(target=check_server_status)
            thread.start()
            thread.join()
        elif option == "9":
            thread = threading.Thread(target=update_minecraft_server)
            thread.start()
            thread.join()
        elif option == "10":
            plugin_link = input("Enter the link to the plugin: ")
            script_dir = os.path.dirname(os.path.abspath(__file__))
            plugin_folder = os.path.join(script_dir, "plugins")
            thread = threading.Thread(target=download_plugin, args=(plugin_link, plugin_folder))
            thread.start()
            thread.join()
        elif option == "11":
            thread = threading.Thread(target=restart_server)
            thread.start()
            thread.join()
        elif option == "12":
            send_in_game_command()
        elif option == "msfconsole":
            open_console()
        elif option == "ngrokconsole":
            open_ngrok_console()
        elif option == "start":
            thread1 = threading.Thread(target=start_minecraft_server)
            thread2 = threading.Thread(target=start_ngrok)
            thread1.start()
            thread2.start()
            thread1.join()
            thread2.join()
        elif option == "stop":
            thread = threading.Thread(target=close_server_and_ngrok)
            thread.start()
            thread.join()
        elif option == "exit":
            break
        else:
            print("Invalid option. Please choose a valid option.")

if __name__ == "__main__":
    main()



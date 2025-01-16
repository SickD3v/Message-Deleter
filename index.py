import os
import json
import requests
import time

# Make the console clean regardless of the OS.
os.system('cls' if os.name == 'nt' else 'clear')

# Check if the JSON file is ok and load it
if os.path.exists('config.json'):
    # "with" ensures that when the "config" variable is retrieved, the memory containing the file is cleared.
    with open('config.json', 'r') as config_file:
        config = json.loads(config_file.read())

    # Check if the "token" key is present in the JSON and if its value is a string.
    if "token" not in config or not isinstance(config['token'], str):
        input("\n It seems that the token is either incorrectly entered or missing in the JSON file.")
        exit()

    # Check if the "timeout" key is present in the JSON and if its value is a int.
    if 'timeout' not in config or not isinstance(config['timeout'], int):
        input("\n It seems that the timeout is either incorrectly entered or missing in the JSON file.")
        exit()
else:
    input("\n It seems that the JSON file is missing. Make sure you have downloaded it from GitHub and restart the script.")
    exit()

# Check if the token is valid and get the user ID.
discord_headers = {'authorization': config['token'],
                   'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.1126 Chrome/128.0.6613.186 Electron/32.2.7 Safari/537.36'}

me_request = requests.get('https://discord.com/api/v9/users/@me', headers=discord_headers)

if me_request.status_code == 200:
    global_name = me_request.json()['global_name']
    user_id     = me_request.json()['id']
else:
    input("\n It seems that the entered token is invalid. Make sure you have entered it correctly in \"config.json\".")
    exit()

# Get the amount and verify if it is correct.
messages_count = input(f"\n [{global_name}] Number of messages : ")

if messages_count.isdigit():
    messages_count = int(messages_count)
else:
    input("\n It seems that you have entered an invalid number; this input must not contain any alphabetic characters.")
    exit()

# Check where the messages need to be deleted.
place = input(f" [{global_name}] Place (server/dm) : ")

match place:
    case 'server':
        guild_id   = input(f" [{global_name}] Guild ID : ")
        search_url = f"https://discord.com/api/v9/guilds/{guild_id}/messages/search?author_id={user_id}&sort_by=timestamp&sort_order=asc&offset=0"

    case 'dm':
        channel_id = input(f" [{global_name}] Channel ID : ")
        search_url = f"https://discord.com/api/v9/channels/{channel_id}/messages/search?author_id={user_id}&sort_by=timestamp&sort_order=asc&offset=0"

    case _:
        input("\n You must choose between \"server\" or \"dm\".")
        exit()

# Just a small aesthetic touch for readability.
print()

messages_counter = 0
while True:
    # Retrieve all the messages on the search page, starting with the oldest.
    search_request = requests.get(search_url, headers=discord_headers)
            
    if search_request.status_code == 200:
        messages = search_request.json()['messages']

        if len(messages) == 0:
            input("\n All the messages were deleted before even reaching the initial number given, so the script was stopped.")
            break

        # List all the messages retrieved in the request.
        for message in messages:
            channel_id, message_id, content = message[0]['channel_id'], message[0]['id'], message[0]['content']

            # Delete the current message.
            delete_request = requests.delete(f"https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}", headers=discord_headers)

            if delete_request.status_code == 204:
                print(f" Message deleted : {content}")
                messages_counter += 1

                # Stop the "for" if messages_count = messages_counter and show a message.
                if messages_count == messages_counter:
                    input("\n All the messages has been deleted.")
                    break
            else:
                input(f"\n An error occurred while deleting message (error code: {delete_request.status_code}).")
                break

            # Wait for the timeout given in the JSON file.
            time.sleep(config['timeout'])

        # Stop the "while" if messages_count = messages_counter.
        if messages_count == messages_counter:
            break
    else:
        input(f"\n An error occurred while retrieving the search page (error code: {search_request.status_code}).")
        break

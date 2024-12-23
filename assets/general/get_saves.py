##################################
# This is the original source code
# of the Discord Bot's Baxi.
#
# When using the code (copy, change)
# all policies and licenses must be adhered to.
#
# Developer: Red_Wolf2467
# Original App: Baxi
##################################
import configparser
import json
import os
import random
import string

config = configparser.ConfigParser()
config.read("config/runtime.conf")
auth0 = configparser.ConfigParser()
auth0.read("config/auth0.conf")


async def save_globalchat_image(attachment):
    filename = ''.join(random.choices(string.ascii_letters + string.digits, k=10)) + \
               os.path.splitext(attachment.filename)[1]
    await attachment.save(os.path.join(config["FLASK"]["global_img_folder"], filename))
    return filename


async def save_general_image(attachment):
    filename = ''.join(random.choices(string.ascii_letters + string.digits, k=15)) + \
               os.path.splitext(attachment.filename)[1]
    await attachment.save(os.path.join(config["FLASK"]["global_img_folder"], filename))
    return filename


def load_data(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        return {}


def save_data(file_path, data):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


files_and_functions = [
    ("json/servers.json", load_data, save_data),
    ("json/staff_users.json", load_data, save_data),
    ("json/newschannel.json", load_data, save_data),
    ("json/banned_server.json", load_data, save_data),
    ("json/early_support.json", load_data, save_data),
    ("json/project-supporter.json", load_data, save_data),
    ("json/dev_user.json", load_data, save_data),
    ("json/verified.json", load_data, save_data),
    ("json/active_user.json", load_data, save_data),
    ("json/staff_user.json", load_data, save_data),
    ("json/banned_users.json", load_data, save_data),
    ("json/chatfilter.json", load_data, save_data),
    ("json/guessing.json", load_data, save_data),
    ("json/countgame_data.json", load_data, save_data),
    ("json/suggestion.json", load_data, save_data),
    ("json/chatfilterrequest.json", load_data, save_data),
    ("json/welcome.json", load_data, save_data),
    ("json/verify.json", load_data, save_data),
    ("json/ticketdata.json", load_data, save_data),
    ("json/ticketinfo.json", load_data, save_data),
    ("json/logged_servers.json", load_data, save_data),
    ("json/language.json", load_data, save_data),
    ("language/en.json", load_data, save_data),
    ("language/de.json", load_data, save_data),
    ("language/norsk.json", load_data, save_data),
    ("language/fr.json", load_data, save_data),
    ("json/api_keys.json", load_data, save_data),
    ("json/gc_messages.json", load_data, save_data),
    ("filter/word_list.json", load_data, save_data),
    ("filter/allowed_words.json", load_data, save_data),
    ("json/privacy_image.json", load_data, save_data),
    ("json/log_channels.json", load_data, save_data),
    ("json/anti_raid.json", load_data, save_data),
    ("json/spamdb_bypass.json", load_data, save_data),
    ("json/auto_roles.json", load_data, save_data),
    ("filter/nsfw_words.json", load_data, save_data)
]

for file_path, load_data, save_data in files_and_functions:
    globals()[f"{os.path.basename(file_path).split('.')[0]}_data"] = load_data(file_path)




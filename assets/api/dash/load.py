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


from reds_simple_logger import Logger
import configparser
import discord
from cryptography.fernet import Fernet
from quart import Quart, render_template, request, send_from_directory, jsonify, url_for

from assets.general.get_saves import *

logger = Logger()


async def get_active_systems(request, guild: discord.Guild):
    key = request.headers.get("Authorization")
    if str(key) != auth0["DASH"]["key"]:
        return jsonify({'error': "Invalid API KEY"}), 401

    data = {}
    anti_raid = load_data("json/anti_raid.json")
    guessing = load_data("json/guessing.json")
    counting = load_data("json/countgame_data.json")
    gc = load_data("json/servers")
    gserver_ids = [item["guildid"] for item in gc]
    welcome = load_data("json/welcome.json")
    verify = load_data("json/verify.json")
    suggestion = load_data("json/suggestion.json")
    ticket = load_data("json/ticketdata.json")
    log = load_data("json/log_channels.json")
    chatfilter = load_data("json/chatfilter.json")
    auto_role = load_data("json/auto_roles.json")

    data["anti_raid"] = 1 if str(guild.id) in anti_raid else 0
    data["mgg"] = 1 if str(guild.id) in guessing else 0
    data["mgc"] = 1 if str(guild.id) in counting else 0
    data["gc"] = 1 if int(guild.id) in gserver_ids else 0
    data["welc"] = 1 if str(guild.id) in welcome else 0
    data["verify"] = 1 if str(guild.id) in verify else 0
    data["sugg"] = 1 if str(guild.id) in suggestion else 0
    data["ticket"] = 1 if str(guild.id) in ticket else 0
    data["log"] = 1 if str(guild.id) in log else 0
    data["sec"] = 1 if str(guild.id) in chatfilter else 0
    data["auto_roles"] = 1 if str(guild.id) in auto_role else 0

    return data


async def load_antiraid_settings(request, guild: discord.Guild):
    config = configparser.ConfigParser()
    config.read("config/runtime.conf")
    try:
        key = request.headers.get("Authorization")
        if str(key) != auth0["DASH"]["key"]:
            return jsonify({'error': "Invalid API KEY"}), 401
        if bool(config["WEB"]["api_online"]):
            anti_raid_settings = load_data("json/anti_raid.json")

            server_roles = {str(role.id): str(role.name) for role in guild.roles if
                            role != guild.default_role}
            if str(guild.id) in anti_raid_settings:
                try:
                    role = guild.get_role(int(anti_raid_settings[str(guild.id)]["role_id"]))
                except Exception as e:
                    logger.error(str(e))
                    return jsonify({"notify-error": "An error occurred while loading the role information."})
                return {"active-switch": 1,
                        "role-label": "Quarantine role",
                        "role-activedrop": {str(role.id): str(role.name)},
                        "role-drop": server_roles
                        }
            else:
                return {"active-switch": 0,
                        "role-label": "Quarantine role",
                        "role-activedrop": None,
                        "role-drop": server_roles
                        }

        else:
            return {
                "notify-warn": "Unfortunately, our backend server is currently unavailable. Please try again later!"}
    except Exception as e:
        return {"notify-warn": f"An unknown error has occurred! Check that all settings are correct.\n{str(e)}"}


async def load_globalchat_settings(request, guild: discord.Guild):
    config = configparser.ConfigParser()
    config.read("config/runtime.conf")
    try:
        key = request.headers.get("Authorization")
        if str(key) != auth0["DASH"]["key"]:
            return jsonify({'error': "Invalid API KEY"}), 401
        if bool(config["WEB"]["api_online"]):
            servers = load_data("json/servers.json")
            gserver_ids = [item["guildid"] for item in servers]
            server_channels = {str(channel.id): str(channel.name) for channel in
                               guild.text_channels}
            if guild.id in gserver_ids:
                for server in servers:
                    if guild.id == server["guildid"]:
                        channel = guild.get_channel(int(server["channelid"]))
                        return {"active-switch": 1,
                                "channels-label": "Channel",
                                "channels-activedrop": {str(channel.id): str(channel.name)},
                                "channels-drop": server_channels
                                }
            else:
                return {"active-switch": 0,
                        "channels-label": "Channel",
                        "channels-activedrop": None,
                        "channels-drop": server_channels
                        }
        else:
            return {
                "notify-warn": "Unfortunately, our backend server is currently unavailable. Please try again later!"}
    except Exception as e:
        return {"notify-warn": f"An unknown error has occurred! Check that all settings are correct.\n{str(e)}"}


async def load_minigame_guessing_settings(request, guild: discord.Guild):
    try:
        key = request.headers.get("Authorization")
        if str(key) != auth0["DASH"]["key"]:
            return jsonify({'error': "Invalid API KEY"}), 401
        if bool(config["WEB"]["api_online"]):
            guessinggame_data = load_data("json/guessing.json")
            server_channels = {str(channel.id): str(channel.name) for channel in
                               guild.text_channels}
            if guild.id in guessinggame_data or str(guild.id) in guessinggame_data:
                # noinspection PyBroadException
                try:
                    channel = guild.get_channel(int(guessinggame_data[str(guild.id)]["channel_id"]))
                except:
                    channel = guild.get_channel(int(guessinggame_data[str(guild.id)]["channel_id"]))
                return {"active-switch": 1,
                        "channels-label": "Channel",
                        "channels-activedrop": {str(channel.id): str(channel.name)},
                        "channels-drop": server_channels
                        }
            else:
                return {"active-switch": 0,
                        "channels-label": "Channel",
                        "channels-activedrop": None,
                        "channels-drop": server_channels
                        }
        else:
            return {
                "notify-warn": "Unfortunately, our backend server is currently unavailable. Please try again later!"}
    except Exception as e:
        return {"notify-warn": f"An unknown error has occurred! Check that all settings are correct.\n{str(e)}"}


async def load_minigame_counting_game(request, guild: discord.Guild):
    try:
        key = request.headers.get("Authorization")
        logger.info(str(key))
        if str(key) != auth0["DASH"]["key"]:
            return jsonify({'error': "Invalid API KEY"}), 401
        if bool(config["WEB"]["api_online"]):
            countinggame_data = load_data("json/countgame_data.json")
            server_channels = {str(channel.id): str(channel.name) for channel in
                               guild.text_channels}
            if str(guild.id) in countinggame_data:
                channel = guild.get_channel(int(countinggame_data[str(guild.id)]["channel_id"]))
                print(channel.name)
                return {"active-switch": 1,
                        "channels-label": "Channel",
                        "channels-activedrop": {str(channel.id): str(channel.name)},
                        "channels-drop": server_channels
                        }
            else:
                return {"active-switch": 0,
                        "channels-label": "Channel",
                        "channels-activedrop": None,
                        "channels-drop": server_channels
                        }
        else:
            return {
                "notify-warn": "Unfortunately, our backend server is currently unavailable. Please try again later!"}
    except Exception as e:
        return {"notify-warn": f"An unknown error has occurred! Check that all settings are correct.\n{str(e)}"}


async def load_security_settings(request, guild: discord.Guild):
    try:
        key = request.headers.get("Authorization")
        logger.info(str(key))
        if str(key) != auth0["DASH"]["key"]:
            return jsonify({'error': "Invalid API KEY"}), 401
        if bool(config["WEB"]["api_online"]):
            chatfilter_data = load_data("json/chatfilter.json")
            font_options = {str(1): "Block", str(0): "Allow"}
            try:
                server_index = next(
                    (index for (index, d) in enumerate(chatfilter_data) if str(d["guildid"]) == str(guild.id)), None)
                logger.debug.info(server_index)
            except Exception:
                server_index = None
            if server_index is not None:
                server_channels = {str(channel.id): str(channel.name) for channel in
                                   guild.text_channels if
                                   int(channel.id) not in chatfilter_data[server_index]["bypass_channels"]}
                server_channels["0"] = "Please select"
                channels = {}
                channels_to_rem = {str(channel.id): str(channel.name) for channel in
                                   guild.text_channels if
                                   int(channel.id) in chatfilter_data[server_index]["bypass_channels"]}
                channels_to_rem["0"] = "Please select"
                for channel in guild.text_channels:
                    if int(channel.id) in chatfilter_data[server_index]["bypass_channels"]:
                        channels[str(channel.id)] = str(channel.name)

                for server_data in chatfilter_data:
                    if server_data["guildid"] == guild.id:
                        block_fonts = server_data["block_ascci"]
                        if block_fonts:
                            block_fonts = 1
                            block_fonts_txt = "Block"
                        else:
                            block_fonts = 0
                            block_fonts_txt = "Allow"
                        return {"active-switch": 1,
                                "block_unknown_symbols-label": "Allow unknown symbols?",
                                "block_unknown_symbols-drop": font_options,
                                "block_unknown_symbols-activedrop": {
                                    str(block_fonts): str(block_fonts_txt)},
                                "channels_add-label": "Add chatfilter bypass",
                                "channels_add-drop": server_channels,
                                "channels_add-activedrop": None,
                                "channels_rem-label": "Remove chatfilter bypass",
                                "channels_rem-drop": channels_to_rem,
                                "channels_rem-activedrop": None,
                                "channels-label": "Bypassed channels",
                                "channels-table": channels
                                }
            else:
                server_channels = {str(channel.id): str(channel.name) for channel in
                                   guild.text_channels}
                server_channels["0"] = "Please select"
                channels = {}
                channels_to_rem = {"0": "Please select"}
                return {"active-switch": 0,
                        "block_unknown_symbols-label": "Allow unknown symbols?",
                        "block_unknown_symbols-drop": font_options,
                        "block_unknown_symbols-activedrop": "None",
                        "channels_add-label": "Add chatfilter bypass",
                        "channels_add-drop": server_channels,
                        "channels_add-activedrop": None,
                        "channels_rem-label": "Remove chatfilter bypass",
                        "channels_rem-drop": channels_to_rem,
                        "channels_rem-activedrop": None,
                        "channels-label": "Bypassed channels",
                        "channels-table": channels
                        }
        else:

            return {
                "notify-warn": "Unfortunately, our backend server is currently unavailable. Please try again later!"}
    except Exception as e:
        return {"notify-warn": f"An unknown error has occurred! Check that all settings are correct.\n{str(e)}"}


async def load_welcome_settings(request, guild: discord.Guild):
    try:
        logger.debug.info("load_welc")
        if "Authorization" in request.headers:
            key = request.headers.get("Authorization")
        else:
            return jsonify(
                {"notify-error": "No Auth header was found in the request! Please report this to the DEV team."})
        logger.debug.info(str(key))
        if str(key) != auth0["DASH"]["key"]:
            return jsonify({'error': "Invalid API KEY"}), 401
        logger.debug.info("Key valid")
        if bool(config["WEB"]["api_online"]):
            welcomelist = load_data("json/welcome.json")
            server_channels = {str(channel.id): str(channel.name) for channel in
                               guild.text_channels}
            colors = {
                "Red": "rot",
                "Blue": "blau",
                "Green": "grün",
                "Purple": "lila",
                "Crimson": "crimson",
                "Random": "zufall"
            }
            if str(guild.id) in welcomelist:
                channel = guild.get_channel(int(welcomelist[str(guild.id)]["channel_id"]))
                message = welcomelist[str(guild.id)]["message"]
                link = welcomelist[str(guild.id)]["image"]

                return {"active-switch": 1,
                        "channels-label": "Channel",
                        "channels-activedrop": {str(channel.id): str(channel.name)},
                        "channels-drop": server_channels,
                        "color-label": "Embed color",
                        "color-activedrop": None,
                        "color-drop": colors,
                        "message-label": "Welcome message",
                        "message-input": message,
                        "image-label": "Embed image",
                        "image-input": link
                        }
            else:
                return {"active-switch": 0,
                        "channels-label": "Channel",
                        "channels-activedrop": None,
                        "channels-drop": server_channels,
                        "color-label": "Embed color",
                        "color-activedrop": None,
                        "color-drop": colors,
                        "message-label": "Welcome message",
                        "message-input": None,
                        "image-label": "Embed image",
                        "image-input": f"https://placehold.co/400x200?text={guild.name}"
                        }
        else:
            return {
                "notify-warn": "Unfortunately, our backend server is currently unavailable. Please try again later!"}
    except Exception as e:
        return {"notify-warn": f"An unknown error has occurred! Check that all settings are correct.\n{str(e)}"}


async def load_verify_settings(request, guild: discord.Guild):
    try:
        key = request.headers.get("Authorization")
        logger.info(str(key))
        if str(key) != auth0["DASH"]["key"]:
            return jsonify({'error': "Invalid API KEY"}), 401
        if bool(config["WEB"]["api_online"]):
            verifylist = load_data("json/verify.json")
            server_channels = {str(channel.id): str(channel.name) for channel in
                               guild.text_channels}
            server_roles = {str(role.id): str(role.name) for role in guild.roles if
                            role != guild.default_role}
            task_drop = {
                0: "None",
                1: "CAPTCHA"
            }
            if str(guild.id) in verifylist:
                role = guild.get_role(int(verifylist[str(guild.id)]["role_id"]))
                message = verifylist[str(guild.id)]["message"]
                task = int(verifylist[str(guild.id)]["task"]) - 1
                if task == 0:
                    task_str = "None"
                else:
                    task_str = "CAPTCHA"

                print(task)
                print(task_str)
                news_channels = load_data("json/newschannel.json")
                baxi_new_channel = guild.get_channel(int(news_channels[str(guild.id)]["channelid"]))

                return {"active-switch": 1,
                        "channels-label": "Channel",
                        "channels-drop": server_channels,
                        "channels-activedrop": {
                            str(baxi_new_channel.id): str(baxi_new_channel.name)},
                        "role-label": "Member role",
                        "role-activedrop": {str(role.id): str(role.name)},
                        "role-drop": server_roles,
                        "message-label": "Message",
                        "message-input": message,
                        "task-label": "Task",
                        "task-drop": task_drop,
                        "task-activedrop": {str(task): str(task_str)}
                        }
            else:
                return {"active-switch": 0,
                        "channels-label": "Channel",
                        "channels-drop": server_channels,
                        "channels-activedrop": None,
                        "role-label": "Member role",
                        "role-activedrop": None,
                        "role-drop": server_roles,
                        "message-label": "Message",
                        "message-input": None,
                        "task-label": "Task",
                        "task-drop": task_drop,
                        "task-activedrop": None
                        }
        else:
            return {
                "notify-warn": "Unfortunately, our backend server is currently unavailable. Please try again later!"}
    except Exception as e:
        return {"notify-warn": f"An unknown error has occurred! Check that all settings are correct.\n{str(e)}"}


async def load_sugg_settings(request, guild: discord.Guild):
    try:
        key = request.headers.get("Authorization")
        logger.info(str(key))
        if str(key) != auth0["DASH"]["key"]:
            return jsonify({'error': "Invalid API KEY"}), 401

        if bool(config["WEB"]["api_online"]):
            suggestion_data = load_data("json/suggestion.json")

            if str(guild.id) in suggestion_data:
                server_channels = {str(channel.id): str(channel.name) for channel in
                                   guild.text_channels if
                                   int(channel.id) not in suggestion_data[str(guild.id)]["channels"]}
                server_channels["0"] = "Please select"
                channels = {}
                channels_to_rem = {str(channel.id): str(channel.name) for channel in
                                   guild.text_channels if int(channel.id) in suggestion_data[str(guild.id)]["channels"]}
                channels_to_rem["0"] = "Please select"
                for channel in guild.text_channels:
                    if int(channel.id) in suggestion_data[str(guild.id)]["channels"]:
                        channels[str(channel.id)] = str(channel.name)

                return {
                    "active-switch": 1,
                    "channels_add-label": "Add channels",
                    "channels_add-drop": server_channels,
                    "channels_add-activedrop": None,
                    "channels_rem-label": "Remove channels",
                    "channels_rem-drop": channels_to_rem,
                    "channels_rem-activedrop": None,
                    "channels-table": channels
                }
            else:
                server_channels = {str(channel.id): str(channel.name) for channel in
                                   guild.text_channels}
                server_channels["0"] = "Please select"
                channels = {}
                channels_to_rem = {"0": "Please select"}

                return {
                    "active-switch": 0,
                    "channels_add-label": "Add channels",
                    "channels_add-drop": server_channels,
                    "channels_add-activedrop": None,
                    "channels_rem-label": "Remove channels",
                    "channels_rem-drop": channels_to_rem,
                    "channels_rem-activedrop": None,
                    "channels-table": channels
                }


        else:
            return {
                "notify-warn": "Unfortunately, our backend server is currently unavailable. Please try again later!"}
    except Exception as e:
        return {"notify-warn": f"An unknown error has occurred! Check that all settings are correct.\n{str(e)}"}


async def load_ticket_settings(request, guild: discord.Guild):
    try:
        key = request.headers.get("Authorization")
        logger.info(str(key))
        if str(key) != auth0["DASH"]["key"]:
            return jsonify({'error': "Invalid API KEY"}), 401

        if bool(config["WEB"]["api_online"]):
            server_channels = {str(channel.id): str(channel.name) for channel in
                               guild.text_channels}
            server_categorys = {str(category.id): str(category.name) for category in
                                guild.categories}
            server_roles = {str(role.id): str(role.name) for role in guild.roles if
                            role != guild.default_role}
            ticketdata = load_data("json/ticketdata.json")
            news_channels = load_data("json/newschannel.json")

            if str(guild.id) in ticketdata:
                category = guild.get_channel(int(ticketdata[str(guild.id)]["categoryid"]))
                baxi_new_channel = guild.get_channel(int(news_channels[str(guild.id)]["channelid"]))
                role = guild.get_role(int(ticketdata[str(guild.id)]["roleid"]))
                return {"active-switch": 1,
                        "channels-label": "Channel",
                        "channels-drop": server_channels,
                        "channels-activedrop": {
                            str(baxi_new_channel.id): str(baxi_new_channel.name)},
                        "category-label": "Category",
                        "category-drop": server_categorys,
                        "category-activedrop": {str(category.id): str(category.name)},
                        "role-label": "Staff role",
                        "role-activedrop": {str(role.id): str(role.name)},
                        "role-drop": server_roles}
            else:
                return {"active-switch": 0,
                        "channels-label": "Channel",
                        "channels-drop": server_channels,
                        "channels-activedrop": None,
                        "category-label": "Category",
                        "category-drop": server_categorys,
                        "category-activedrop": None,
                        "role-label": "Staff role",
                        "role-activedrop": None,
                        "role-drop": server_roles}

        else:
            return {
                "notify-warn": "Unfortunately, our backend server is currently unavailable. Please try again later!"}
    except Exception as e:
        return {"notify-warn": f"An unknown error has occurred! Check that all settings are correct.\n{str(e)}"}


async def load_log_settings(request, guild: discord.Guild):
    try:
        log_channels = load_data("json/log_channels.json")
        key = request.headers.get("Authorization")
        logger.info(str(key))
        if str(key) != auth0["DASH"]["key"]:
            return jsonify({'error': "Invalid API KEY"}), 401

        if bool(config["WEB"]["api_online"]):
            server_channels = {str(channel.id): str(channel.name) for channel in
                               guild.text_channels}

            if str(guild.id) in log_channels:
                channel = guild.get_channel(log_channels[str(guild.id)]["channel_id"])
                return {"active-switch": 1,
                        "channels-label": "Channel",
                        "channels-drop": server_channels,
                        "channels-activedrop": {str(channel.id): str(channel.name)}}
            else:
                return {"active-switch": 0,
                        "channels-label": "Channel",
                        "channels-drop": server_channels,
                        "channels-activedrop": None}
        else:
            return {
                "notify-warn": "Unfortunately, our backend server is currently unavailable. Please try again later!"}
    except Exception as e:
        return {"notify-warn": f"An unknown error has occurred! Check that all settings are correct.\n{str(e)}"}


async def load_autoroles_guild(request, guild: discord.Guild):
    try:
        auto_roles = load_data("json/auto_roles.json")
        key = request.headers.get("Authorization")
        logger.info(str(key))
        if str(key) != auth0["DASH"]["key"]:
            return jsonify({'error': "Invalid API KEY"}), 401

        if bool(config["WEB"]["api_online"]):

            if str(guild.id) in auto_roles:
                server_roles = {str(role.id): str(role.name) for role in guild.roles if
                                int(role.id) not in auto_roles[str(guild.id)]["roles"] and role != guild.default_role}
                server_roles["0"] = "Please select"
                roles = {}
                roles_to_rem = {str(role.id): str(role.name) for role in guild.roles if
                                int(role.id) in auto_roles[str(guild.id)]["roles"] and role != guild.default_role}
                roles_to_rem["0"] = "Please select"

                for role in guild.roles:
                    if int(role.id) in auto_roles[str(guild.id)]["roles"]:
                        roles[str(role.id)] = str(role.name)
                return {"active-switch": 1,
                        "roles-label": "Auto roles",
                        "roles-table": roles,
                        "roles_to_add-label": "Add role",
                        "roles_to_add-drop": server_roles,
                        "roles_to_remove-label": "Remove role",
                        "roles_to_remove-drop": roles_to_rem
                        }
            else:
                server_roles = {str(role.id): str(role.name) for role in guild.roles if
                                role != guild.default_role}
                server_roles["0"] = "Please select"
                roles = {}
                roles_to_rem = {"0": "Please select"}
                return {"active-switch": 0,
                        "roles-label": "Auto roles",
                        "roles-table": roles,
                        "roles_to_add-label": "Add role",
                        "roles_to_add-drop": server_roles,
                        "roles_to_remove-label": "Remove role",
                        "roles_to_remove-drop": roles_to_rem
                        }

        else:
            return {
                "notify-warn": "Unfortunately, our backend server is currently unavailable. Please try again later!"}
    except Exception as e:
        return {"notify-warn": f"An unknown error has occurred! Check that all settings are correct.\n{str(e)}"}


async def load_send_channels(request, guild: discord.Guild):
    try:
        key = request.headers.get("Authorization")
        logger.info(str(key))
        if str(key) != auth0["DASH"]["key"]:
            return jsonify({'error': "Invalid API KEY"}), 401
        if bool(config["WEB"]["api_online"]):
            server_channels = {str(channel.id): str(channel.name) for channel in
                               guild.text_channels}
            news_channels = load_data("json/newschannel.json")
            baxi_new_channel = guild.get_channel(int(news_channels[str(guild.id)]["channelid"]))

            return {"channels-label": "Channel",
                    "channels-drop": server_channels,
                    "channels-activedrop": {str(baxi_new_channel.id): str(baxi_new_channel.name)},
                    "message-label": "Message",
                    "message-input": None
                    }
    except Exception as e:
        return {"notify-warn": f"An unknown error has occurred! Check that all settings are correct.\n{str(e)}"}

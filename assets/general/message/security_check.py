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
import re

from assets.general.message.globalchat import get_globalchat
from assets.general.message.logging import save_log_entry_logged_server
from cara_api import CaraAPI
from reds_simple_logger import Logger

from assets.dc.embed.buttons import *
from assets.general.routine_events import *

config = configparser.ConfigParser()
config.read("config/runtime.conf")
auth0 = configparser.ConfigParser()
auth0.read("config/auth0.conf")

logger = Logger()
caraAPI = CaraAPI(auth0["CARA"]["key"])

embedColor = discord.Color.from_rgb(int(config["BOT"]["embed_color_red"]), int(config["BOT"]["embed_color_green"]),
                                    int(config["BOT"]["embed_color_blue"]))  # FF5733


async def check_message_sec(message: discord.Message, bot):
    message_content = message.content
    CHATFILTER_nsfw_server = False
    nsfw_content_words = load_data("filter/nsfw_words.json")
    timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    settings_chatfilter = load_data("json/chatfilter.json")
    settings_counting = load_data("json/countgame_data.json")
    settings_guessing = load_data("json/guessing.json")
    privacy_image = load_data("json/privacy_image.json")

    chatfilter_server_index = next(
        (index for (index, d) in enumerate(settings_chatfilter) if d["guildid"] == message.guild.id), 1)

    filter_word_list = load_data("filter/word_list.json")
    filter_allowed_word_list = load_data("filter/allowed_words.json")
    filter_allowed_symbols_list = load_data("filter/allowed_symbols.json")

    try:
        chatfilter_block_nonAscci = settings_chatfilter.get("block_ascci")
    except:
        chatfilter_block_nonAscci = True

    for symbol in filter_allowed_symbols_list:
        message_content = message_content.replace(symbol, "")

    if (str(message.guild.id) in settings_counting and settings_counting[str(message.guild.id)][
        "channel_id"] == message.channel.id) or (
            str(message.guild.id) in settings_guessing and int(message.channel.id) ==
            settings_guessing[str(message.guild.id)]["channel_id"]):
        message_content = re.sub(r'\d+', '', message_content)

    if len(message.attachments) > 0:
        if message.guild.id not in privacy_image:
            logger.info("Saving " + str(len(message.attachments)) + " attachments to static/general_imgs")
            for attachement in message.attachments:
                filename = await save_general_image(attachement)
                message_content = str(
                    message_content) + "https://baxi-backend.pyropixle.com/_images_/" + filename + "\n"
                logger.info("https://baxi-backend.pyropixle.com/_images_/" + filename + "\n")
        else:
            logger.info("Server has enabled advanced privacy, images not saved!")

    invite_pattern = re.compile(r'(https?://)?(www\.)?(discord\.(gg|io|me|li|com)|discordapp\.com/invite)/(\w+)',
                                re.IGNORECASE)
    for match in invite_pattern.findall(message.content):
        invite_code = match[-1]
        try:
            invite = await bot.fetch_invite(invite_code)
            server_name = invite.guild.name
            for word in server_name.split():
                if word.lower() in nsfw_content_words:
                    CHATFILTER_nsfw_server = True
        except discord.errors.NotFound:
            CHATFILTER_nsfw_server = False
        except discord.errors.HTTPException:
            CHATFILTER_nsfw_server = False
        except Exception:
            CHATFILTER_nsfw_server = False

    if not (message_content is None or message_content == "") and (
            int(message.channel.id) not in settings_chatfilter[chatfilter_server_index]["bypass_channels"]):
        try:
            # noinspection RegExpSimplifiable
            message_length = len(re.sub(r'http[s]?://\S+', '', message.content))
            if message_length > 100:
                logger.info(f"LONG message - {message_length} chars")
                levenshtein_wert = 2
            else:
                logger.info(f"SHORT message - {message_length} chars")
                levenshtein_wert = 1
            chatfilter_request = caraAPI.chatfilter(message=message_content,
                                                    levenshtein=levenshtein_wert,
                                                    FilteredWords=filter_word_list,
                                                    GoodWords=filter_allowed_word_list,
                                                    GuildID=message.guild.id,
                                                    ChannelID=message.channel.id,
                                                    AuthorID=message.author.id,
                                                    MessageID=message.id,
                                                    GuildName=message.guild.name,
                                                    ChannelName=message.channel.name,
                                                    AuthorName=message.author.name,
                                                    OnlyASCII=chatfilter_block_nonAscci,
                                                    log=False)

            response = {"response": chatfilter_request.result,
                        "reason": chatfilter_request.reason,
                        "pair": chatfilter_request.levenshteinPair,
                        "timestamp": timestamp,
                        "nsfw_server": CHATFILTER_nsfw_server}


        except:
            response = {"response": 0,
                        "reason": None,
                        "pair": None,
                        "timestamp": timestamp,
                        "nsfw_server": CHATFILTER_nsfw_server}


    else:
        response = {"response": 0,
                    "reason": None,
                    "pair": None,
                    "timestamp": timestamp,
                    "nsfw_server": CHATFILTER_nsfw_server}
    return response


async def check_user_sec(user: discord.User):
    try:
        bypass = load_data("json/spamdb_bypass.json")
        user_check_request = caraAPI.get_user(user_id=str(user.id))
        if user.id not in bypass:
            isSpammer = user_check_request.isSpammer
        else:
            isSpammer = False
        isSpammer_reason = user_check_request.reason
        response = {"isSpammer": isSpammer,
                    "reason": isSpammer_reason}
    except:
        response = {"isSpammer": None,
                    "reason": None}

    return response


async def del_message(message: discord.Message, message_api, user_api):
    language = load_language_model(message.guild.id)
    logger.info("Message marked as spam!")
    chatfiltler_requestID: int = random.randint(1000000, 9999999)
    chatfilterrequest = load_data("json/chatfilterrequest.json")
    log_channels = load_data("json/log_channels.json")
    chatfilter_list = load_data("json/chatfilter.json")

    if message_api["response"] != 0:
        chatfilter_response_reason = message_api["reason"]
    else:
        chatfilter_response_reason = language["security_chatfilter_nsfw_link_reason"]

    embed = discord.Embed(title=language["security_title"],
                          description=f"{language['security_chatfilter_introduction']} {message.author.mention}\n"
                                      f"> **{language['security_chatfilter_reason_tag']}** `{chatfilter_response_reason}`\n"
                                      f"> **{language['security_chatfilter_request_tag']}** `{chatfiltler_requestID}`\n"
                                      f"> **Info:** [security.pyropixle.com](https://security.pyropixle.com/chatfilterinfo?requestid={chatfiltler_requestID})",
                          # noqa
                          color=discord.Color.red()).set_thumbnail(url=icons_url + "warn.png").set_footer(
        text=language["security_chatfilter_footer"])

    logger.working("Saving data to json/chatfilterrequest.json...")

    chatfilterrequest[chatfiltler_requestID] = {
        "response": message_api["response"],
        "user": message.author.name,
        "userid": message.author.id,
        "channelid": message.channel.id,
        "channel": message.channel.name,
        "message": message.content,
        "timestamp": message_api["timestamp"],
        "reason": chatfilter_response_reason,
        "requestid": chatfiltler_requestID,
        "server": message.guild.name,
        "serverid": message.guild.id,
        "userisspammer": user_api["isSpammer"],
        "isspammerreason": user_api["reason"],
        "levenshteinPair": message_api["pair"]
    }

    save_data("json/chatfilterrequest.json", chatfilterrequest)
    logger.info("Data saved!")

    await save_log_entry_logged_server(guild=message.guild, message=message,
                                       chatfilter_response=message_api["response"])

    if not get_globalchat(message.guild.id, message.channel.id):
        filter_server_ids = [item["guildid"] for item in chatfilter_list]
        if message.guild.id in filter_server_ids:
            if message.guild.id in log_channels:
                await message.guild.get_channel(int(log_channels[str(message.guild.id)]["channel_id"])).send(
                    embed=embed)

            def check(message_in):
                return message_in.id == message.id

            await message.channel.purge(limit=5, check=check,
                                        reason=f"Baxi Security - Chatfilter - {chatfiltler_requestID}")
            await message.channel.send(embed=embed)
            logger.success("Message processed! (Chatfilter action)")
            return
    else:
        await message.channel.send(embed=embed)

        def check(message_in):
            return message_in.id == message.id

        await message.channel.purge(limit=5, check=check,
                                    reason=f"Baxi Security - Chatfilter - {chatfiltler_requestID}")
        logger.success("Message processed! (Chatfilter action)")
        return

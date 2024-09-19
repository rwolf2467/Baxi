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

import discord


class GuidelinesButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(style=discord.ButtonStyle.url,
                                        label="Guidelines", url="https://pyropixle.com/gtc/"))


class DiscordButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(style=discord.ButtonStyle.url,
                                        label="Discord", url="https://link.pyropixle.com/discord/"))


class InviteButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(style=discord.ButtonStyle.url,
                                        label="Add me", url="https://link.pyropixle.com/baxi/"))


class InviteUndWebButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(style=discord.ButtonStyle.url,
                                        label="Add me", url="https://link.pyropixle.com/baxi/"))
        self.add_item(discord.ui.Button(style=discord.ButtonStyle.url,
                                        label="Website", url="https://pyropixle.com/"))


class InviteUndWebUndDiscordButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(style=discord.ButtonStyle.url,
                                        label="Add me", url="https://link.pyropixle.com/baxi/"))
        self.add_item(discord.ui.Button(style=discord.ButtonStyle.url,
                                        label="Website", url="https://pyropixle.com/"))
        self.add_item(discord.ui.Button(style=discord.ButtonStyle.url,
                                        label="Discord", url="https://link.pyropixle.com/discord/"))
        self.add_item(discord.ui.Button(style=discord.ButtonStyle.url,
                                        label="Privacy", url="https://pyropixle.com/privacy/"))
        self.add_item(discord.ui.Button(style=discord.ButtonStyle.url,
                                        label="GTC", url="https://pyropixle.com/gtc/"))


# noinspection SpellCheckingInspection
class InviteUndWebUndDiscordundDocsButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(style=discord.ButtonStyle.url,
                                        label="Add me", url="https://link.pyropixle.com/baxi/"))
        self.add_item(discord.ui.Button(style=discord.ButtonStyle.url,
                                        label="Website", url="https://pyropixle.com/"))
        self.add_item(discord.ui.Button(style=discord.ButtonStyle.url,
                                        label="Discord", url="https://link.pyropixle.com/discord/"))
        self.add_item(discord.ui.Button(style=discord.ButtonStyle.url,
                                        label="Docs", url="https://docs.pyropixle.com/"))
        self.add_item(discord.ui.Button(style=discord.ButtonStyle.url,
                                        label="Privacy", url="https://pyropixle.com/privacy/"))
        self.add_item(discord.ui.Button(style=discord.ButtonStyle.url,
                                        label="GTC", url="https://pyropixle.com/gtc/"))


class VerifyButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    # noinspection PyUnresolvedReferences
    @discord.ui.button(custom_id="verifybutton", style=discord.ButtonStyle.green, emoji="<:verify:1244723476825243718>")
    async def verifybutton(self, interaction: Interaction, button: discord.ui.Button):  # noqa
        language = load_language_model(str(interaction.guild.id))
        try:
            verifylist = load_data("json/verify.json")
            embed_success = discord.Embed(title="Verification", description=language["verify_success"],
                                          color=discord.Color.green())

            if int(verifylist[str(interaction.guild.id)]["task"]) == 2:
                try:
                    code = generate_random_string(5)
                    logger.info(f"Generated verification code: {code}")
                    if str(interaction.guild.id) in verifylist:
                        try:
                            role = interaction.guild.get_role(int(verifylist[str(interaction.guild.id)]["role_id"]))
                            logger.info(f"Role fetched: {role}")
                        except Exception as e:
                            logger.error(f"Role fetch error: {str(e)}")
                            await interaction.edit_original_response(content=None,
                                                                     embed=discord.Embed(title="Verifikation",
                                                                                         description=language[
                                                                                             "verify_role_missing_error"],
                                                                                         color=discord.Color.red()).set_thumbnail(
                                                                         url=icons_url + "warn.png"))
                            return

                        if role not in interaction.user.roles:
                            verify_uid = interaction.user.id
                            verify_gid = interaction.guild.id

                            class VerifyModal(discord.ui.Modal):
                                code_entered = discord.ui.TextInput(label=f"{language['verify_task']}",
                                                                    placeholder=f"{code}",
                                                                    style=discord.TextStyle.short, required=True,
                                                                    min_length=5, max_length=5)

                                # noinspection PyUnresolvedReferences
                                async def on_submit(self, interaction_2: discord.Interaction):
                                    try:
                                        logger.info(f"Received verification code from user: {self.code_entered.value}")
                                        if str(self.code_entered.value) == str(code):
                                            verifylist_2 = load_data("json/verify.json")
                                            role_2 = interaction_2.guild.get_role(
                                                verifylist_2[str(verify_gid)]["role_id"])
                                            user = await interaction_2.guild.fetch_member(verify_uid)
                                            await user.add_roles(role_2,
                                                                 reason="Baxi Security - Successful verification")
                                            await interaction_2.response.send_message(embed=embed_success,
                                                                                      ephemeral=True)
                                        else:
                                            await interaction_2.response.send_message("Invalid code", ephemeral=True)
                                    except Exception as e_2:
                                        await interaction_2.response.send_message("ERROR: " + str(e_2))
                                        logger.error(f"Verification code error: {str(e_2)}")

                            modal = VerifyModal(title="Verifikation")
                            try:
                                await interaction.response.send_modal(modal)
                                logger.success("Modal sent successfully")
                            except Exception as e:
                                logger.error(f"Error sending modal: {str(e)}")
                        else:
                            await interaction.response.send_message(content=None,
                                                                    embed=discord.Embed(title="Verifikation",
                                                                                        description=language[
                                                                                            "verify_already-verified_error"],
                                                                                        color=discord.Color.red()),
                                                                    ephemeral=True)
                except Exception as e:
                    await interaction.response.send_message("ERROR: " + str(e) + "\n https://docs.pyropixle.com")
                    logger.error(f"Verification process error: {str(e)}")



            elif int(verifylist[str(interaction.guild.id)]["task"]) == 1:
                try:
                    await interaction.response.send_message(language["wait"], ephemeral=True)  # noqa
                    if str(interaction.guild.id) in verifylist:
                        try:
                            role = interaction.guild.get_role(verifylist[str(interaction.guild.id)]["role_id"])
                        except:  # noqa
                            await interaction.edit_original_response(content=None,
                                                                     embed=discord.Embed(title="Verifikation",
                                                                                         description=language[
                                                                                             "verify_role_missing_error"],
                                                                                         color=discord.Color.red()).set_thumbnail(
                                                                         url=icons_url + "warn.png"))
                            return
                        if role not in interaction.user.roles:
                            await interaction.user.add_roles(role)
                            await interaction.edit_original_response(content=None, embed=embed_success)
                        else:
                            await interaction.edit_original_response(content=None,
                                                                     embed=discord.Embed(title="Verifikation",
                                                                                         description=language[
                                                                                             "verify_already-verified_error"],
                                                                                         color=discord.Color.red()))
                except:  # noqa
                    await interaction.edit_original_response(
                        content=language["unknown_error"])

        except Exception as e:
            await interaction.response.send_message("ERROR, SERVER NOT IN DATABASE!", delete_after=5)
            logger.error(f"General error: {str(e)}")


class BugReportOptions(discord.ui.View):  # noqa
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(label="Github",
                                        style=discord.ButtonStyle.url,
                                        url="https://github.com/rwolf2467/Baxi/issues"))

    @discord.ui.button(label="InApp Formular", custom_id="report_form_inapp", style=discord.ButtonStyle.gray)
    async def report_form_inapp_btn(self, interaction: discord.Interaction, Button: discord.ui.Button):  # noqa
        await interaction.response.send_modal(BUGREPORT())  # noqa
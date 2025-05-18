import discord

from Bot.Modules.Data.collect import create_or_update_message_details
from Bot.Data.cortemundial import Profiles


class dataCommands:
    def __init__(self, console, client):
        self.console = console
        self.client = client

    async def collect(self, interaction: discord.Interaction):
        if interaction.user.id == 1047943536374464583:
            await interaction.response.defer(ephemeral=True)
            guild = interaction.guild
            if not guild:
                await interaction.followup.send("This command must be used in a server.")
                return

            total_channels = len(guild.text_channels)
            processed_channels = 0
            total_messages = 0
            blocked_list = [607697321366388739]
            lore_list = ["rp", "eventos", "nações", "nações-secundárias", "🔹seoul🔹", "jornal-mundial", "corte-mundial", "🔹rp🔹", "🔹eventos🔹", "🔹notícias🔹"]

            for channel in guild.text_channels:
                if not(any(match in channel.name.lower() for match in lore_list) and channel.id not in blocked_list):
                    self.console.log(f"Skipping {channel.name}.")
                    continue
                if not channel.permissions_for(guild.me).read_message_history:
                    self.console.log(f"Skipping {channel.name} (no permissions)")
                    continue

                try:
                    self.console.log(f"Processing {channel.name}...")
                    messages = []
                    async for msg in channel.history(limit=None, oldest_first=True):
                        messages.append(msg)
                    message_count = 0

                    for msg in messages:
                        # Validate core message properties
                        if not all([
                            msg.id,
                            msg.channel.id,
                            msg.guild and msg.guild.id,
                            msg.author,
                            msg.created_at
                        ]):
                            self.console.log(f"Skipping malformed message in {channel.name}")
                            continue

                        try:
                            author = msg.author
                            if author.bot: # skip bot messages
                                continue

                            # Create or update user profile with validation
                            user_profile, created = Profiles.get_or_create(
                                userid=str(author.id),
                                defaults={
                                    'username': author.name,
                                    'discriminator': author.discriminator,
                                    'avatar_url': str(author.avatar.url) if author.avatar else '',
                                    'joined_at': author.created_at,
                                    'is_bot': author.bot
                                }
                            )

                            # Validate database entry
                            if not user_profile:
                                raise ValueError("Failed to create user profile")

                            # Prepare message data with fallbacks
                            message_details = {
                                'user': user_profile,
                                'user_id': str(author.id),
                                'message_text': msg.content or '[No Content]',
                                'timestamp': msg.created_at,
                                'guild_id': str(msg.guild.id),
                                'message_id': str(msg.id),
                                'channel_id': str(channel.id),
                            }

                            # Validate IDs before insertion
                            for key in ['guild_id', 'message_id', 'channel_id', 'user_id']:
                                if not message_details[key]:
                                    raise ValueError(f"Missing {key} in message details")

                            create_or_update_message_details(message_details)
                            message_count += 1

                        except Exception as user_error:
                            self.console.log(f"Message {msg.id} error: {str(user_error)}")
                            continue

                    total_messages += message_count
                    processed_channels += 1
                    self.console.log(f"Processed {message_count} messages in {channel.name}")

                except discord.Forbidden:
                    self.console.log(f"Missing permissions in {channel.name}")
                except Exception as e:
                    self.console.log(f"Channel {channel.name} error: {str(e)}")

            report = (
                f"**Data Collection Complete**\n"
                f"• Channels processed: {processed_channels}/{total_channels}\n"
                f"• Total messages collected: {total_messages}"
            )
            await interaction.followup.send(report)
        else:
            await interaction.response.send_message("You are not authorized to use this command.", ephemeral=True)

    async def collect_to_text(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        channel = interaction.channel
        guild = interaction.guild
        if not guild or not channel:
            await interaction.followup.send("This command must be used in a server text channel.")
            return

        if not channel.permissions_for(guild.me).read_message_history:
            await interaction.followup.send("I don't have permission to read the message history in this channel.")
            return

        log_lines = []
        total_messages = 0

        try:
            self.console.log(f"Collecting messages from #{channel.name}...")

            async for msg in channel.history(limit=None, oldest_first=True):
                if msg.author.bot:
                    continue  # Skip bots

                timestamp = msg.created_at.strftime('%Y-%m-%d %H:%M')
                username = f"{msg.author.name}#{msg.author.discriminator}"
                content = msg.content or '[No Content]'
                line = f"[{timestamp}] {username}: {content}"
                log_lines.append(line)
                total_messages += 1

        except Exception as e:
            self.console.log(f"Error reading channel {channel.name}: {e}")
            await interaction.followup.send(f"Failed to collect messages: {str(e)}")
            return

        # Save to file
        date_str = datetime.utcnow().strftime("%Y-%m-%d_%H-%M")
        filename = f"{guild.name}_{channel.name}_chatlog_{date_str}.txt"
        os.makedirs("chatlogs", exist_ok=True)
        filepath = os.path.join("chatlogs", filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("\n".join(log_lines))

        report = (
            f"**Chat Log Collection Complete**\n"
            f"• Channel: #{channel.name}\n"
            f"• Total user messages collected: {total_messages}\n"
            f"• Log file saved as: `{filename}`"
        )
        await interaction.followup.send(report)
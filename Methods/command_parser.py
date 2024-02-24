async def execute_by_code(interaction, top, code: str):

    # Gift maker command
    if code == "gift_command":
        await top.Commands().gift_command(interaction)
    if code == "talk_command":
        await top.Commands().talk_command(interaction)
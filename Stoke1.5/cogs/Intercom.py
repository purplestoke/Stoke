import nextcord
from nextcord.ext import commands
from API_Tokens import purplestoke 

class Intercom(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def intercom(self, ctx, *, msg):
        #VARS 
        mem = ctx.author
        discord = mem.id 

        if discord != purplestoke:
            await ctx.send("You are not my dad!")
            return
        fail = []
        for guild in self.client.guilds:
            for chan in guild.text_channels:
                if chan.name == 'intercom':
                    try:
                        await chan.send(msg)
                    except nextcord.Forbidden:
                        fail.append(f"Failed to send in {guild.name} due to permissions")
                    except Exception as e:
                        fail.append(f"Failed to send in {guild.name} due to {e}")
                    break
        if fail:
            await ctx.send("\n".join(fail))
        else:
            await ctx.send("Msg sent to all guilds!")

def setup(client):
    client.add_cog(Intercom(client))

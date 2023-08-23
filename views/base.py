import discord


class DashboardBase(discord.ui.View):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class PersistentDashboardBase(DashboardBase):

    def __init__(self, *args, **kwargs):
        super().__init__(timeout=None, *args, **kwargs, )


class DashboardEmbedBase(discord.Embed):

    def __init__(self, *args, **kwargs):
        super().__init__(title="Default Embed Title", description="Default Embed Description", *args, **kwargs)

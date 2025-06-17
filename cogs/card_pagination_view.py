import math

import discord.ui
from db.mongo import get_card_by_id, get_user_by_user_id, get_card_quantity_by_user_id_card_id
import discord

class CardPaginationView(discord.ui.View):
    curr_page = 1
    sep = 9

    async def send_message(self, interaction: discord.Interaction):
        try:
            await self.update_message(interaction, self.cards[:self.sep])
        except Exception as e:
            print(e)

    def update_button(self):
        if self.curr_page <= 1:
            self.prev_button.disabled = True
        else:
            self.prev_button.disabled = False

        if self.curr_page >= int(len(self.cards) / self.sep) + 1:
            self.next_button.disabled = True
        else:
            self.next_button.disabled = False

    async def update_message(self, interaction: discord.Interaction, cards_paged):
        self.update_button()
        await self.message.edit(content="", embed=self.make_cards_embed(cards_paged, get_user_by_user_id(interaction.user.id)), view=self)
        await interaction.response.defer()

    def make_cards_embed(self, cards, user):
        embed = discord.Embed(title=f"{self.user_name}'s cards")
        for card in cards:
            card_quantity = get_card_quantity_by_user_id_card_id(user["user_id"], card["_id"])
            embed.add_field(name=f"{card['class']} - {card['title']} - {card_quantity}", value=card['desc'],
                                inline=True)

        if len(cards) % 3 == 1:
            embed.add_field(name=" ", value=" ", inline=True)
        if len(cards) % 3 == 2:
            embed.add_field(name=" ", value=" ", inline=True)
            embed.add_field(name=" ", value=" ", inline=True)

        return embed

    @discord.ui.button(label="prev", style=discord.ButtonStyle.primary)
    async def prev_button(self, interaction: discord.Interaction, button:discord.ui.Button):
        try:
            self.curr_page -= 1
            until_item = self.curr_page * self.sep
            from_item = until_item - self.sep
            cards_paged = self.cards[from_item:until_item]
            await self.update_message(interaction, cards_paged)
        except Exception as e:
            print(e)

    @discord.ui.button(label="next", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button:discord.ui.Button):
        try:
            self.curr_page += 1
            until_item = self.curr_page * self.sep
            from_item = until_item - self.sep
            cards_paged = self.cards[from_item:until_item]
            await self.update_message(interaction, cards_paged)
        except Exception as e:
            print(e)

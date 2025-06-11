import discord.utils
from discord.ext import commands, tasks
import feedparser
from db.mongo import update_channel_data, youtube_channels_collection, discord_servers_collection

class YoutubeTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_youtube_videos_update.start()

    @tasks.loop(minutes=5)
    async def check_youtube_videos_update(self):
        print(f"refresh in 5 mins for videos")

        for channel_data in youtube_channels_collection.find():
            channel_id = channel_data["channel_id"]
            last_video_id = channel_data.get("last_video_id", "")

            rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
            print(rss_url)
            feed = feedparser.parse(rss_url)

            if not feed.entries:
                continue

            latest_entry = feed.entries[0]
            latest_video_id = latest_entry.yt_videoid
            print(latest_video_id)

            if last_video_id == "":
                update_channel_data(channel_id, latest_video_id, "last_video_id")
                print("No new video")
            elif last_video_id != latest_video_id:
                update_channel_data(channel_id, latest_video_id, "last_video_id")
                print("New video uploaded!")
                await self.send_notification(latest_video_id)
            else:
                print("No new video")

    async def send_notification(self, latest_video_id: str):
        for server_data in discord_servers_collection.find():
            target_youtube_message_id = server_data["target_youtube_message_id"]
            print(target_youtube_message_id)
            channel = self.bot.get_channel(target_youtube_message_id)
            await channel.send(f"New video uploaded!\nhttps://www.youtube.com/watch?v={latest_video_id}")


async def setup(bot):
    await bot.add_cog(YoutubeTracker(bot))

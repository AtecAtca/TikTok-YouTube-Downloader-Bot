from pyrogram import Client

# Create a new Client instance
API_ID=
API_HASH=''

app = Client("test", API_ID, API_HASH )


async def main():
    async with app:
        
        # Send a message, Markdown is enabled by default
        await app.send_message("me", "Hi there! I'm using **Pyrogram**")
        

app.run(main())



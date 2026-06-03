import pastey


async def async_main() -> None:
    async with pastey.Client() as client:
        await client.delete_paste("my_paste_id", "abcdefGHIJKL")
        # or have/get a Paste from another method first:
        paste = await client.create_paste(files=[...])

        # `paste.safety_token` is potentially None, but since we created the paste we definitely have it, so we can ignore:
        await client.delete_paste(paste.id, paste.safety_token)  # pyright: ignore[reportArgumentType] # we have the safety token definitely.

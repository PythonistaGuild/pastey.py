import asyncio

import pastey


async def async_main() -> str:
    async with pastey.Client() as client:
        file_1 = pastey.File(content="File 1 goes here", name="file_1.txt", language="Plain Text")
        file_2 = pastey.File(content="print('hello world!\n')", name="file_2.py", language="Python")
        paste = await client.create_paste(files=[file_1, file_2])

        return paste.url


asyncio.run(async_main())


def main() -> str:
    with pastey.SyncClient() as client:
        file_1 = pastey.File(content="File 1 goes here", name="file_1.txt", language="Plain Text")
        file_2 = pastey.File(content="print('hello world!\n')", name="file_2.py", language="Python")
        paste = client.create_paste(files=[file_1, file_2])

        return paste.url


main()

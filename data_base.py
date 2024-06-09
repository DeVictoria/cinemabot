import aiosqlite


class DateBase:

    def __init__(self) -> None:
        self.is_created = False

    async def create_base(self) -> None:
        self.connection = await aiosqlite.connect('search_history.db')
        await self.connection.execute('''
                           CREATE TABLE IF NOT EXISTS search_history (
                               user_id INTEGER,
                               search_film TEXT)''')
        await self.connection.execute('''
                       CREATE TABLE IF NOT EXISTS stats (
                           user_id INTEGER,
                           search_film TEXT,
                           count_search INTEGER)''')

        await self.connection.commit()
        await self.connection.close()

        self.is_created = True

    async def add_film(self, user_id: int, name: str) -> None:
        if not self.is_created:
            await self.create_base()

        self.connection = await aiosqlite.connect('search_history.db')
        await self.connection.execute("INSERT INTO search_history (user_id, search_film) VALUES (?, ?)",
                                      (user_id, name))

        cursor = await self.connection.execute("SELECT 1 FROM stats WHERE (user_id, search_film)=(?, ?)",
                                               (user_id, name))
        existing_movie = await cursor.fetchone()
        if not existing_movie:
            await self.connection.execute("INSERT INTO stats (user_id, search_film) VALUES (?, ?)", (user_id, name))
        await self.connection.execute(
            "UPDATE stats SET count_search = COALESCE(count_search, 0) + 1 WHERE user_id=? AND search_film=?",
            (user_id, name))

        await self.connection.commit()
        await self.connection.close()

    async def get_search_history(self, user_id: int):  # type: ignore
        if not self.is_created:
            await self.create_base()
        self.connection = await aiosqlite.connect('search_history.db')
        cursor = await self.connection.execute("SELECT * FROM search_history WHERE user_id=?", (user_id,))
        await self.connection.commit()
        return await cursor.fetchall()

    async def get_stats(self, user_id: int):  # type: ignore
        if not self.is_created:
            await self.create_base()
        self.connection = await aiosqlite.connect('search_history.db')
        cursor = await self.connection.execute("SELECT search_film, count_search FROM stats WHERE user_id=?",
                                               (user_id,))
        await self.connection.commit()
        return await cursor.fetchall()

    async def close(self) -> None:
        await self.connection.close()

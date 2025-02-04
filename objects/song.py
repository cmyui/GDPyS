# The main purpose of this file is to contain
# the main song object.
from .glob import glob
from web.client import post_request
from helpers.common import is_numeric
from utils.gdform import parse_to_dict, gd_dict_str
from logger import error, debug

class Song:
    """The object representation of the GDPyS and Geometry Dash songs."""

    def __init__(self):
        """Sets the placeholder variables. Please
        use the classmethods instead."""

        self.id: int = -1
        self.title: str = ""
        self.author_id: int = 0
        self.author_name: str = ""
        self.size: float = 0.0 # 2dp float.
        self.author_yt: str = ""
        self.url: str = ""
    
    @property
    def full_name(self) -> str:
        """Returns the name of the song in the format Author Name - Song Name"""

        return f"{self.author_name} - {self.title}"
    
    @classmethod
    async def from_sql(cls, song_id: int):
        """Fetches the song data directly from the MySQL database and sets the
        object data based off it.
        
        Args:
            song_id (int): The Newgrounds ID of the song to be fetched.
        
        Returns:
            Instance of `Song` if found.
            None if not found.
        """

        self = cls()
        # Simple MySQL query.
        song_db = await glob.sql.fetchone(
            "SELECT id, title, author_id, author_name,"
            "size, author_yt, download FROM songs WHERE "
            "id = %s LIMIT 1",
            (song_id,)
        )

        if song_db is None:
            return
        
        # Set data.
        (
            self.id,
            self.title,
            self.author_id,
            self.author_name,
            self.size,
            self.author_yt,
            self.url
        ) = song_db

        return self

    @classmethod
    async def from_boomlings(cls, song_id: int):
        """Fetches the song data for the song with the Newgrounds ID of
        `song_id` from the Boomlings private API.
        
        Note:
            This is by far the slowest way of fetching from the servers as it
                has to make a http request to another server.
        
        Args:
            song_id (int): The Newgrounds ID of the
                song to fetch.
        
        Returns:
            Instance of `Song` if found.
            None if not found.
        """

        self = cls()

        # First we sent a post request to Boomlings to grab the data.
        boomlings_data = await post_request(
            "http://boomlings.com/database/getGJSongInfo.php",
            {
                "secret": "Wmfd2893gb7",
                "songID": song_id
            }
        )

        # Check if the resp is valid.
        if is_numeric(boomlings_data) or not boomlings_data:
            error(f"Boomlings Private Song API sent an invalid response for the song ID of {song_id}")
            debug("Boomlings Reply: " + boomlings_data)
            return
        
        # Looks right! Parse it.
        parsed_resp = parse_to_dict(boomlings_data)

        # Set object data from parsed.
        self.id = int(parsed_resp[1])
        self.title = parsed_resp[2]
        self.author_id = int(parsed_resp[3])
        self.author_name = parsed_resp[4]
        self.size = float(parsed_resp[5])
        self.author_yt = parsed_resp[7]
        self.url = parsed_resp[10]
        return self
    
    @classmethod
    async def from_id(cls, song_id: int):
        """Fetches the song object, searching for `song_id`.
        
        Note:
            This classmethod searches through multiple sources, in the order
                of cache, sql, boomlings (ordered by speed).

        Args:
            song_id (int): The Newgrounds ID of the song to fetch.
        
        Returns:
            Instance of `Song` if found.
            None if not found.
        """

        if not song_id: return Song() # Empty because else causes errors lol.

        # First we check if its already cached.
        if s := glob.song_cache.get(song_id):
            # Already cached, this one is easy.
            return s
        
        # No I guess, we have to take the longer methods.
        if s := await cls.from_sql(song_id):
            # Found in db. Automatically cache it for speed later.
            glob.song_cache.cache(s.id, s)
            return s
        
        # We should try the literally longest possible way (300ms+)
        if s := await cls.from_boomlings(song_id):
            # Found it in boomlings. Cache it as well as add to db.
            await s.insert()
            glob.song_cache.cache(s.id, s)
            return s
        
        # Song doesn't exist to our knowledge.
        return
    
    async def insert(self):
        """Inserts the song data from the object into the MySQL database."""

        # Check if we want to assign it a new ID.
        if self.id == -1:
            # This gets converted to auto increment
            self.id = None 

        # Nothing special here... We just execute
        # the MySQL query directly and fetch the
        # last row id.
        self.id = await glob.sql.execute(
            "INSERT INTO songs (id, title, author_id,"
            "author_name, size, author_yt, download) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s)",
            (
                self.id,
                self.title,
                self.author_id,
                self.author_name,
                self.size,
                self.author_yt,
                self.url
            )
        )
    
    def __str__(self) -> str:
        """Returns a string representation of the song."""

        # Just return full name.
        return self.full_name
    
    def resp(self) -> str:
        """"A Geometry Dash HTTP response styled song object."""

        return gd_dict_str(
            {
                1: self.id,
                2: self.title,
                3: self.author_id,
                4: self.author_name,
                5: self.size,
                7: self.author_yt,
                10: self.url
            },
            "~|~"
        )

import asyncio, psycopg
from library_manager.exceptions import *

async def test_db(conn: psycopg.AsyncConnection):
    async with conn.cursor() as cur:
        await cur.execute("INSERT INTO artist (artistName) VALUES (%s)", ("Test",))
        
        await cur.execute("SELECT * FROM artist")
        print(await cur.fetchone())
        await conn.commit()

#################################################
#           Artist Table Queries                #
#################################################

async def getArtistUUID(conn: psycopg.AsyncConnection, artistName: str):
    async with conn.cursor() as cur:
        await cur.execute("SELECT artistid FROM artist WHERE artistname = %s", (artistName,))
        UUID = await cur.fetchone()
        return str(UUID[0]) if UUID else None

async def addArtist(conn:psycopg.AsyncConnection, artistName: str):
    async with conn.cursor() as cur:
        if await getArtistUUID(conn, artistName) is None:
            await cur.execute("INSERT INTO artist (artistName) VALUES (%s)", (artistName,))
            await conn.commit()
            return await getArtistUUID(conn, artistName)
        else:
            return await getArtistUUID(conn, artistName)

async def removeArtist(conn:psycopg.AsyncConnection, artistName: str):
    async with conn.cursor() as cur:
        UUID = await getArtistUUID(conn, artistName)
        if UUID is not None:
            await cur.execute("DELETE FROM artist WHERE artistid = %s", (str(UUID[0]),))
            await conn.commit()
            return await getArtistUUID(conn, artistName)
        else:
            return ArtistNotFoundError(artistName)

async def modifyArtist(conn:psycopg.AsyncConnection, artistID: str, newArtistName: str ):
    async with conn.cursor() as cur:
        oldname = await cur.execute("SELECT artistName FROM artist WHERE artistid = %s", (artistID,)) 
        if oldname is not None:
            await cur.execute("UPDATE artist SET artistname = %s WHERE artistid = %s", (newArtistName, artistID))
        else:
            raise ArtistNotFoundError(artistID)

#################################################
#            Track Table Queries                #
#################################################

#################################################
#           Medium Table Queries                #
#################################################

async def getMediumUUID(conn:psycopg.AsyncConnection, mediumName: str):
    async with conn.cursor() as cur:
        await cur.execute("SELECT mediumid FROM medium WHERE mediumname = %s", (mediumName,))
        UUID = await cur.fetchone()
        return str(UUID[0]) if UUID else None

async def addMedium(conn:psycopg.AsyncConnection, mediumName: str):
    async with conn.cursor() as cur:
        if await getMediumUUID(conn, mediumName) is None:
            await cur.execute("INSERT INTO medium (mediumName) VALUES (%s)", (mediumName,))
            await conn.commit()
            return await getMediumUUID(conn, mediumName)
        else:
            return await getMediumUUID(conn, mediumName)
         
async def removeMedium(conn:psycopg.AsyncConnection, mediumName: str):
    async with conn.cursor() as cur:
        UUID = await getMediumUUID(conn, mediumName)
        if UUID is not None:
            await cur.execute("DELETE FROM medium WHERE mediumid = %s", (str(UUID[0]),))
            await conn.commit()
            return await getMediumUUID(conn, mediumName)
        else:
            raise MediumNotFoundError(mediumName)

async def modifyMedium(conn:psycopg.AsyncConnection, mediumID: str, newMediumName: str ):
    async with conn.cursor() as cur:
        oldname = await cur.execute("SELECT mediumName FROM medium WHERE mediumid = %s", (mediumID,)) 
        if oldname is not None:
            await cur.execute("UPDATE medium SET mediumname = %s WHERE mediumid = %s", (newMediumName, mediumID))
        else:
            raise MediumNotFoundError(mediumID)

#################################################
#           Album Table Queries                #
#################################################

#################################################
#           Review Table Queries                #
#################################################


async def addReview(conn:psycopg.AsyncConnection, review: str, userID: str, draft: bool, albumid: str):
    if verifyUserUUID(conn,userID) is None:
        raise UserNotFoundError(userID)
    async with conn.cursor() as cur:
        await cur.execute("INSERT INTO review (userid, review, draft) VALUES (%s, %s, %s)", (userID, review, draft))
        await cur.commit()

        #add to review_album here
        return 1



#################################################
#             User Table Queries                #
#################################################

async def getUserUUID(conn:psycopg.AsyncConnection, userEmail: str):
    async with conn.cursor() as cur:
        await cur.execute("SELECT userid FROM user WHERE email = %s", (userEmail,))
        UUID = await cur.fetchone()
        return str(UUID[0]) if UUID else None

async def verifyUserUUID(conn:psycopg.AsyncConnection, userID: str):
    async with conn.cursor() as cur:
        await cur.execute("SELECT userid FROM user WHERE userid = %s", (userID,))
        return await cur.fetchone() # Will return None if no results

async def addUser(conn:psycopg.AsyncConnection, firstName: str, lastName: str, email: str):
    async with conn.cursor() as cur:
        if await getUserUUID(conn,email) is None:
            await cur.execute("INSERT INTO user (firstname, lastname, email) VALUES (%s,%s,%s)", (firstName,lastName,email,))
            await conn.commit()
            return await getUserUUID(conn,email)
        else:
            raise UserAlreadyExistsError(email)

async def deleteUser(conn:psycopg.AsyncConnection, userID: str):
    if await verifyUserUUID(conn, userID) is None:
        raise UserNotFoundError(userID)
    else:
        async with conn.cursor() as cur:
            await cur.execute("DELETE FROM user WHERE userid = %s", (userID,))
            await conn.commit()
            return await verifyUserUUID(conn,userID)

async def getUserRole(conn:psycopg.AsyncConnection, userID: str):
    if await verifyUserUUID(conn, userID) is None:
        raise UserNotFoundError(userID)
    else:
        async with conn.cursor() as cur:
            await cur.execute("SELECT role FROM user WHERE userid = %s", (userID,))
            role = await cur.fetchone()
            return str(role[0]) if role else None

async def setUserRole(conn:psycopg.AsyncConnection, userID: str, userRole: str):
    if userRole not in ["member", "staff", "eboard"]:
        raise RoleNotFound(userRole)
    elif await verifyUserUUID(conn, userID) is None:
        raise UserNotFoundError(userID)
    else:
        async with conn.cursor() as cur:
            await cur.execute("UPDATE user SET role = %s WHERE userID = %s", (userRole, userID))
            await conn.commit()
            return await getUserRole(conn,userID)

async def modifyEmail(conn:psycopg.AsyncConnection, userID: str, newEmail: str):
    if await verifyUserUUID(conn, userID) is None:
        raise UserNotFoundError(userID)
    else:
        async with conn.cursor() as cur:
            await cur.execute("UPDATE user SET email = %s WHERE userid = %s", (newEmail, userID))
            await conn.commit()
            return await verifyUserUUID(conn,userID) #TODO: return something useful if needed

async def modifyFirstName(conn:psycopg.AsyncConnection, userID: str, newName: str):
    if await verifyUserUUID(conn, userID) is None:
        raise UserNotFoundError(userID)
    else:
        async with conn.cursor() as cur:
            await cur.execute("UPDATE user SET firstname = %s WHERE userid = %s", (newName, userID))
            await conn.commit()
            return await verifyUserUUID(conn,userID) #TODO: return something useful if needed

async def modifyLastName(conn:psycopg.AsyncConnection, userID: str, newName: str):
    if await verifyUserUUID(conn, userID) is None:
        raise UserNotFoundError(userID)
    else:
        async with conn.cursor() as cur:
            await cur.execute("UPDATE user SET lastname = %s WHERE userid = %s", (newName, userID))
            await conn.commit()
            return await verifyUserUUID(conn,userID) #TODO: return something useful if needed

async def getFirstName(conn:psycopg.AsyncConnection, userID:str):
    if await verifyUserUUID(conn,userID) is None:
        raise UserNotFoundError(userID)
    else:
        async with conn.cursor() as cur:
            await cur.execute("SELECT firstname FROM user WHERE userid = %s",(userID,))
            name = await cur.fetchone()
            return str(name[0]) if name else None
        
async def getLastName(conn:psycopg.AsyncConnection, userID:str):
    if await verifyUserUUID(conn,userID) is None:
        raise UserNotFoundError(userID)
    else:
        async with conn.cursor() as cur:
            await cur.execute("SELECT lastname FROM user WHERE userid = %s",(userID,))
            name = await cur.fetchone()
            return str(name[0]) if name else None

async def getUserInitials(conn:psycopg.AsyncConnection, userID:str):
    if await verifyUserUUID(conn,userID) is None:
        raise UserNotFoundError(userID)
    else:
        async with conn.cursor() as cur:
            await cur.execute("SELECT firstname, lastname FROM user WHERE userid = %s",(userID,))
            name = await cur.fetchone()
            if name is None:
                return None
            fn = name[0]
            ln = name[1]
            initials = fn[0]+ln[0]
            return initials 


#################################################
#          Album_Medium Table Queries           #
#################################################

#################################################
#          Album_Artist Table Queries           #
#################################################

#################################################
#          Album_Track Table Queries           #
#################################################

#################################################
#          Artist_Track Table Queries           #
#################################################



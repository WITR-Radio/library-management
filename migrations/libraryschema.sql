CREATE DATABASE library;
\c library;

CREATE TABLE users (
    userID uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    firstName varchar(300) NOT NULL,
    lastName varchar(300) NOT NULL,
    email varchar(50) NOT NULL,
    role varchar(10) NOT NULL DEFAULT 'member'
);

CREATE TABLE review (
    reviewID uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    review text NOT NULL,
    userID uuid NOT NULL,
    reviewDate timestamptz NOT NULL DEFAULT now(),
    hidden bool NOT NULL DEFAULT False,
    draft bool NOT NULL DEFAULT False,
    CONSTRAINT USERS_USERID_FK FOREIGN KEY (userID) REFERENCES users(userID)
);

CREATE TABLE album (
    albumID uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    albumName varchar(255) NOT NULL,
    albumShort varchar(5) NOT NULL,
    genre varchar(25) NOT NULL,
    picture text,
    releaseDate timestamptz
);

CREATE TABLE medium (
    mediumID uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    mediumName varchar(25) NOT NULL
);

CREATE TABLE artist (
    artistID uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    artistName varchar(255) NOT NULL UNIQUE
);

CREATE TABLE track (
    trackID uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    trackName varchar(255) NOT NULL,
    fccClean bool NOT NULL DEFAULT False
);

CREATE TABLE artist_track (
    artistID uuid REFERENCES artist(artistID),
    trackID uuid REFERENCES track(trackID),
    PRIMARY KEY (artistID, trackID)
);

CREATE TABLE album_artist (
    artistID uuid REFERENCES artist(artistID),
    albumID uuid REFERENCES album(albumID),
    PRIMARY KEY (artistID, albumID)
);


-- Removed because each review cannot have multiple albums they apply to however each album can have multiple reviews
-- Getting reviews will query review table to see where album id matches
-- CREATE TABLE review_album (
--     reviewID uuid REFERENCES review(reviewID),
--     albumID uuid REFERENCES album(albumID),
--     PRIMARY KEY (reviewID, albumID)
-- );

CREATE TABLE album_medium (
    album_UPC varchar(20),
    albumID uuid REFERENCES album(albumID),
    mediumID uuid REFERENCES medium(mediumID),
    PRIMARY KEY (mediumID, albumID)
);

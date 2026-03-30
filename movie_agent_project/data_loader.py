import weaviate
from weaviate.classes.config import Configure, Property, DataType, ReferenceProperty
import os
from dotenv import load_dotenv

def main():
    load_dotenv()
    
    # 1. Connect to Weaviate Cloud
    print("Connecting to Weaviate Cloud...")
    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=os.getenv("WEAVIATE_URL"),
        auth_credentials=weaviate.auth.AuthApiKey(os.getenv("WEAVIATE_API_KEY")),
        headers={
            "X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY")
        }
    )

    try:
        # 2. Cleanup existing collections (for clean run)
        if client.collections.exists("Review"):
            client.collections.delete("Review")
            print("Deleted existing Review collection.")
        if client.collections.exists("Movie"):
            client.collections.delete("Movie")
            print("Deleted existing Movie collection.")

        # 3. Create Movie Collection
        print("Creating Movie collection...")
        movie_collection = client.collections.create(
            name="Movie",
            vectorizer_config=Configure.Vectorizer.text2vec_openai(),
            generative_config=Configure.Generative.openai(model="gpt-4o"),
            properties=[
                Property(name="title", data_type=DataType.TEXT),
                Property(name="director", data_type=DataType.TEXT),
                Property(name="overview", data_type=DataType.TEXT),
                Property(name="release_year", data_type=DataType.INT),
                Property(name="genre", data_type=DataType.TEXT),
                Property(name="rating", data_type=DataType.NUMBER),
                # This property will be populated later by the Transformation Agent
                Property(name="marketing_pitch", data_type=DataType.TEXT) 
            ]
        )

        # 4. Create Review Collection with Cross-Reference
        print("Creating Review collection...")
        review_collection = client.collections.create(
            name="Review",
            vectorizer_config=Configure.Vectorizer.text2vec_openai(),
            generative_config=Configure.Generative.openai(model="gpt-4o"),
            properties=[
                Property(name="review_text", data_type=DataType.TEXT),
                Property(name="sentiment", data_type=DataType.TEXT)
            ],
            references=[
                ReferenceProperty(name="hasMovie", target_collection="Movie")
            ]
        )

        # 5. Populate Sample Data
        print("Populating data...")
        movies_data = [
            {
                "title": "Inception",
                "director": "Christopher Nolan",
                "overview": "A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O. Explores the deepest depths of the subconscious mind.",
                "release_year": 2010,
                "genre": "Sci-Fi",
                "rating": 8.8
            },
            {
                "title": "Interstellar",
                "director": "Christopher Nolan",
                "overview": "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival as Earth's resources diminish. A visually stunning masterpiece grounded in profound astrophysical concepts like relativity.",
                "release_year": 2014,
                "genre": "Sci-Fi",
                "rating": 8.6
            },
            {
                "title": "The Dark Knight",
                "director": "Christopher Nolan",
                "overview": "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.",
                "release_year": 2008,
                "genre": "Action",
                "rating": 9.0
            },
            {
                "title": "Parasite",
                "director": "Bong Joon Ho",
                "overview": "Greed and class discrimination threaten the newly formed symbiotic relationship between the wealthy Park family and the destitute Kim clan. A gripping look at social disparity.",
                "release_year": 2019,
                "genre": "Thriller",
                "rating": 8.5
            },
            {
                "title": "Knives Out",
                "director": "Rian Johnson",
                "overview": "A detective investigates the death of a patriarch of an eccentric, combative family. A playful, modern take on the Agatha Christie-style whodunit.",
                "release_year": 2019,
                "genre": "Mystery",
                "rating": 7.9
            },
            {
                "title": "The Matrix",
                "director": "Lana Wachowski, Lilly Wachowski",
                "overview": "A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers. A foundational cyberpunk film.",
                "release_year": 1999,
                "genre": "Sci-Fi",
                "rating": 8.7
            },
            {
                "title": "Pulp Fiction",
                "director": "Quentin Tarantino",
                "overview": "The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption.",
                "release_year": 1994,
                "genre": "Crime",
                "rating": 8.9
            },
            {
                "title": "Forrest Gump",
                "director": "Robert Zemeckis",
                "overview": "The presidencies of Kennedy and Johnson, the Vietnam War, the Watergate scandal and other historical events unfold from the perspective of an Alabama man with an IQ of 75, whose only desire is to be reunited with his childhood sweetheart.",
                "release_year": 1994,
                "genre": "Drama",
                "rating": 8.8
            },
            {
                "title": "The Lord of the Rings: The Return of the King",
                "director": "Peter Jackson",
                "overview": "Gandalf and Aragorn lead the World of Men against Sauron's army to draw his gaze from Frodo and Sam as they approach Mount Doom with the One Ring. An epic high-fantasy conclusion.",
                "release_year": 2003,
                "genre": "Fantasy",
                "rating": 9.0
            },
            {
                "title": "Spirited Away",
                "director": "Hayao Miyazaki",
                "overview": "During her family's move to the suburbs, a sullen 10-year-old girl wanders into a world ruled by gods, witches, and spirits, and where humans are changed into beasts.",
                "release_year": 2001,
                "genre": "Animation",
                "rating": 8.6
            },
            {
                "title": "Gladiator",
                "director": "Ridley Scott",
                "overview": "A former Roman General sets out to exact vengeance against the corrupt emperor who murdered his family and sent him into slavery. Action packed historical epic.",
                "release_year": 2000,
                "genre": "Action",
                "rating": 8.5
            },
            {
                "title": "The Godfather",
                "director": "Francis Ford Coppola",
                "overview": "The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son. Deeply explores Italian-American mafia culture.",
                "release_year": 1972,
                "genre": "Crime",
                "rating": 9.2
            },
            {
                "title": "Avatar",
                "director": "James Cameron",
                "overview": "A paraplegic Marine dispatched to the moon Pandora on a unique mission becomes torn between following his orders and protecting the world he feels is his home.",
                "release_year": 2009,
                "genre": "Sci-Fi",
                "rating": 7.9
            },
            {
                "title": "Mad Max: Fury Road",
                "director": "George Miller",
                "overview": "In a post-apocalyptic wasteland, a woman rebels against a tyrannical ruler in search for her homeland with the aid of a group of female prisoners, a psychotic worshiper, and a drifter named Max.",
                "release_year": 2015,
                "genre": "Action",
                "rating": 8.1
            },
            {
                "title": "Schindler's List",
                "director": "Steven Spielberg",
                "overview": "In German-occupied Poland during World War II, industrialist Oskar Schindler gradually becomes concerned for his Jewish workforce after witnessing their persecution by the Nazis.",
                "release_year": 1993,
                "genre": "Historical",
                "rating": 9.0
            },
            {
                "title": "The Grand Budapest Hotel",
                "director": "Wes Anderson",
                "overview": "A writer encounters the owner of an aging high-class hotel, who tells him of his early years serving as a lobby boy in the hotel's glorious years under an exceptional concierge. Famous for its symmetrical visual style and whimsical storytelling.",
                "release_year": 2014,
                "genre": "Comedy",
                "rating": 8.1
            },
            {
                "title": "A Quiet Place",
                "director": "John Krasinski",
                "overview": "In a post-apocalyptic world, a family is forced to live in silence while hiding from monsters with ultra-sensitive hearing. Known for its tense, incredibly scary moments without jump scares.",
                "release_year": 2018,
                "genre": "Horror",
                "rating": 7.5
            },
            {
                "title": "Jurassic Park",
                "director": "Steven Spielberg",
                "overview": "A pragmatic paleontologist visiting an almost complete theme park is tasked with protecting a couple of kids after a power failure causes the park's cloned dinosaurs to run loose. Prehistoric thrill ride.",
                "release_year": 1993,
                "genre": "Adventure",
                "rating": 8.2
            },
            {
                "title": "Spider-Man: Into the Spider-Verse",
                "director": "Bob Persichetti, Peter Ramsey, Rodney Rothman",
                "overview": "Teen Miles Morales becomes the Spider-Man of his universe, and must join with five spider-powered individuals from other dimensions to stop a threat for all realities.",
                "release_year": 2018,
                "genre": "Animation",
                "rating": 8.4
            },
            {
                "title": "Good Will Hunting",
                "director": "Gus Van Sant",
                "overview": "Will Hunting, a janitor at M.I.T., has a gift for mathematics, but needs help from a psychologist to find direction in his life.",
                "release_year": 1997,
                "genre": "Drama",
                "rating": 8.3
            }
        ]

        reviews_data = [
            {"movie_title": "Inception", "review_text": "Mind-bending and visually spectacular. Nolan at his finest.", "sentiment": "Positive"},
            {"movie_title": "Interstellar", "review_text": "An emotional journey that transcends space and time.", "sentiment": "Positive"},
            {"movie_title": "The Dark Knight", "review_text": "Heath Ledger's performance is legendary. A masterpiece.", "sentiment": "Positive"},
            {"movie_title": "Parasite", "review_text": "Brilliant social commentary wrapped in a suspenseful plot.", "sentiment": "Positive"},
            {"movie_title": "Knives Out", "review_text": "A fun, modern take on the classic whodunit. Very entertaining.", "sentiment": "Positive"},
            {"movie_title": "Inception", "review_text": "Too confusing for its own good. Left me with a headache.", "sentiment": "Negative"},
            {"movie_title": "The Matrix", "review_text": "Pioneered special effects and changed action cinema forever.", "sentiment": "Positive"},
            {"movie_title": "Forrest Gump", "review_text": "Tom Hanks delivers a heartwarming performance that remains timeless.", "sentiment": "Positive"},
            {"movie_title": "Mad Max: Fury Road", "review_text": "Non-stop action and jaw-dropping practical effects. A cinematic triumph.", "sentiment": "Positive"},
            {"movie_title": "A Quiet Place", "review_text": "A brilliant concept executed perfectly. Tension is incredibly high and scary from start to finish.", "sentiment": "Positive"},
            {"movie_title": "The Grand Budapest Hotel", "review_text": "Wes Anderson creates a beautifully crafted, slightly eccentric world that is a joy to visit.", "sentiment": "Positive"}
        ]

        # Insert movies and keep track of their UUIDs
        movie_uuids = {}
        for md in movies_data:
            uuid = movie_collection.data.insert(properties=md)
            movie_uuids[md["title"]] = uuid
            print(f"Inserted Movie: {md['title']}")

        # Insert reviews and link them to the movie
        for rd in reviews_data:
            movie_title = rd.pop("movie_title")
            review_uuid = review_collection.data.insert(properties=rd)
            
            # Cross-reference
            if movie_title in movie_uuids:
                review_collection.data.reference_add(
                    from_uuid=review_uuid,
                    from_property="hasMovie",
                    to=movie_uuids[movie_title]
                )
            print(f"Inserted Review for: {movie_title}")

        print("Data initialization complete! You can now run the query agent or transformation agent.")

    finally:
        client.close()

if __name__ == "__main__":
    main()

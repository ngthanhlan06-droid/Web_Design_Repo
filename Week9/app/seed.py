from sqlmodel import Session, select
from app.database import engine, SQLModel
from app.models import Hero, Team, Mission

def seed_data():
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        existing_team = session.exec(select(Team)).first()
        if existing_team:
            print("Database already seeded. Skipping.")
            return

        print("Seeding database with sample data...")

        # 1. Tạo các Team
        avengers = Team(name="Avengers", headquarters="New York")
        x_men = Team(name="X-Men", headquarters="Westchester")
        session.add(avengers)
        session.add(x_men)

        # 2. Tạo các Mission
        mission_sokovia = Mission(title="Battle of Sokovia")
        mission_wakanda = Mission(title="Battle of Wakanda")
        session.add(mission_sokovia)
        session.add(mission_wakanda)

        # 3. Tạo các Hero và gán vào Team + Mission thông qua Relationship
        hero1 = Hero(
            name="Tony", 
            secret_name="Iron Man", 
            age=45, 
            team=avengers, 
            missions=[mission_sokovia]
        )
        hero2 = Hero(
            name="Natasha", 
            secret_name="Black Widow", 
            age=35, 
            team=avengers, 
            missions=[mission_sokovia, mission_wakanda]
        )
        hero3 = Hero(
            name="Logan", 
            secret_name="Wolverine", 
            age=150, 
            team=x_men, 
            missions=[]
        )
        hero4 = Hero(
            name="Peter", 
            secret_name="Spider-Man", 
            age=16, 
            team=None, 
            missions=[]
        )
        hero5 = Hero(
            name="Steve", 
            secret_name="Captain America", 
            age=100, 
            team=avengers, 
            missions=[mission_wakanda]
        )

        session.add_all([hero1, hero2, hero3, hero4, hero5])
        session.commit()
        print("Seeding complete!")

if __name__ == "__main__":
    seed_data()
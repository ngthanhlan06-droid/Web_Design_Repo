from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query, Response, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import SQLModel, select

from app.database import engine, SessionDep
from app.models import (
    Hero, Team, Mission, HeroMissionLink,
    HeroCreate, HeroPublic, HeroUpdate,
    TeamCreate, TeamPublic,
    MissionCreate, MissionPublic
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/teams", response_model=TeamPublic, status_code=201)
def create_team(team_in: TeamCreate, session: SessionDep):
    team = Team.model_validate(team_in)
    session.add(team)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="Team name already exists")
    session.refresh(team)
    return team

@app.get("/teams", response_model=list[TeamPublic])
def list_teams(session: SessionDep):
    return session.exec(select(Team)).all()

@app.get("/teams/{team_id}/heroes", response_model=list[HeroPublic])
def list_team_heroes(team_id: int, session: SessionDep):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team.heroes

@app.post("/missions", response_model=MissionPublic, status_code=201)
def create_mission(mission_in: MissionCreate, session: SessionDep):
    mission = Mission.model_validate(mission_in)
    session.add(mission)
    session.commit()
    session.refresh(mission)
    return mission

@app.post("/heroes/{hero_id}/missions/{mission_id}", status_code=204)
def assign_hero_mission(hero_id: int, mission_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    mission = session.get(Mission, mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    if mission not in hero.missions:
        hero.missions.append(mission)
        session.add(hero)
        session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.get("/heroes/{hero_id}/missions", response_model=list[MissionPublic])
def list_hero_missions(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero.missions

@app.post("/heroes", response_model=HeroPublic, status_code=201)
def create_hero(hero_in: HeroCreate, session: SessionDep):
    if hero_in.team_id is not None:
        team = session.get(Team, hero_in.team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")

    hero = Hero.model_validate(hero_in)
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero

@app.get("/heroes", response_model=list[HeroPublic])
def list_heroes(
    session: SessionDep,
    offset: int = 0,
    limit: int = Query(default=10, le=100),
    min_age: int | None = None,
    team_id: int | None = None,
    name: str | None = None
):
    query = select(Hero)
    if min_age is not None:
        query = query.where(Hero.age >= min_age)
    if team_id is not None:
        query = query.where(Hero.team_id == team_id)
    if name is not None:
        query = query.where(Hero.name.ilike(f"%{name}%"))

    heroes = session.exec(query.order_by(Hero.id).offset(offset).limit(limit)).all()
    return heroes

@app.get("/heroes/{hero_id}", response_model=HeroPublic)
def read_hero(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero

@app.patch("/heroes/{hero_id}", response_model=HeroPublic)
def update_hero(hero_id: int, hero_in: HeroUpdate, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")

    hero_data = hero_in.model_dump(exclude_unset=True)
    if "team_id" in hero_data and hero_data["team_id"] is not None:
        team = session.get(Team, hero_data["team_id"])
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")

    hero.sqlmodel_update(hero_data)
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero

@app.delete("/heroes/{hero_id}", status_code=204)
def delete_hero(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    session.delete(hero)
    session.commit()
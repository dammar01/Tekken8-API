from bs4 import BeautifulSoup
from .model import Movetable
import requests, re


def convert_moveset(move: str):
    move = move.replace("WS", "ws")
    return move


async def find_move(character_name: str, notation: str):
    raw_data = await get_movetable(Movetable(character_name=character_name))
    move = ""
    for part in notation.split(" "):
        if re.search(r"\d", part):
            move = part
            break
    move = convert_moveset(move)
    filtered_result = [
        item
        for item in raw_data
        if item["moveset"] == f"{character_name.capitalize()}-{move}"
    ]
    if filtered_result:
        return filtered_result
    return {"error": "No matching moveset found."}


async def get_movetable(data: Movetable):
    url = f"https://wavu.wiki/w/index.php?title=Special%3ACargoQuery&tables=Move&fields=CONCAT%28id%2C%27%27%29%3DMove%2Cstartup%3DStartup%2Ctarget%3DHit+Level%2Cdamage%3DDamage%2Cblock%3DOn+Block%2CCONCAT%28hit%2C%27%27%29%3DOn+Hit%2CCONCAT%28ch%2C%27%27%29%3DOn+CH%2Ccrush%3DStates%2Cnotes%3DNotes&where=Move._pageName%3D%27{data.character_name.capitalize()}+movelist%27&join_on=&group_by=&having=&order_by%5B0%5D=&order_by_options%5B0%5D=ASC&limit=1000&offset=0&format=table"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")

        def get_data(classname: str):
            raw = soup.find_all(class_=classname)
            result = [data.get_text(strip=True) for data in raw]
            return result

        raw = {
            "moveset": get_data("field_Move"),
            "startup": get_data("field_Startup"),
            "hit_properties": get_data("field_Hit_Level"),
            "damage": get_data("field_Damage"),
            "on_block": get_data("field_On_Block"),
            "on_hit": get_data("field_On_Hit"),
            "on_CH": get_data("field_On_CH"),
            "states": get_data("field_States"),
            "notes": get_data("field_Notes"),
        }
        result = [
            {
                "moveset": raw["moveset"][i],
                "startup": raw["startup"][i],
                "hit_properties": raw["hit_properties"][i],
                "damage": raw["damage"][i],
                "on_block": raw["on_block"][i],
                "on_hit": raw["on_hit"][i],
                "on_CH": raw["on_CH"][i],
                "states": raw["states"][i],
                "notes": raw["notes"][i],
            }
            for i in range(len(raw["moveset"]))
            if raw["moveset"][i] != "Move"
        ]
        if data.notation is not None:
            filtered_result = [
                item
                for item in result
                if item["moveset"]
                == f"{data.character_name.capitalize()}-{data.notation}"
            ]
            return (
                filtered_result[0]
                if filtered_result[0]
                else {"error": "No matching moveset found."}
            )
        return result
    else:
        return {"error": "error while getting frame data"}
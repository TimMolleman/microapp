import datetime as dt
from operator import itemgetter
import uuid
from typing import Dict, List, Union


def add_raw_numbers(raw_items: List[Dict[str, int]]) -> int:
    return sum(map(itemgetter('number'), raw_items))


def add_random_id_and_date(item: Dict[str, Union[str, int]]) -> Dict[str, Union[str, int]]:
    item['id'] = f'{item["name"]}_{str(uuid.uuid4())}'
    item['datetime'] = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return item

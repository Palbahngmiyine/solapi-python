import json
from src.lib import message

if __name__ == '__main__':
    res = message.post('/messages/v4/groups', data={})
    print(json.dumps(json.loads(res.text), indent=2, ensure_ascii=False))

# Usage

#### In `src` directory

`poetry install`

`poetry run python api/api.py`

### API Endpoints

API endpoints can be reached via curl or other API clients

### Example

```sh
$ curl http://127.0.0.1:5000/

[
    {
        "id": 1,
        "state": "..."
    },
    ...
]
```

| Verb | Endpoint | Description | Expected Format |
|---|---|---|---|
|`GET`|`/`| Returns List of existing "Worlds" | |
|`POST`|`/`| Creates a new "World" and returns processed results | `text/plain` text matrix of world to process |
| `GET` | `/{id}` | Returns details of "World" by ID | |
| `PUT` | `/{id}` | Adds additional rows to existing "World" |  `text/plain` text matrix of rows to add to existing "World" |
| `DELETE` | `/{id}` | Deletes "World" by ID | |

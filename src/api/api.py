import sqlite3, logging, re, time

from flask import Flask, g, request
from flask_restful import abort, Api, fields, marshal_with, Resource

from processor import process_gravity, to_text

logger = logging.getLogger('API')

# Database Configuration
DATABASE = '/mnt/d/development/bright.md/sql/brightmd.db'


# App Configuration
app = Flask(__name__)

# API
api = Api(app)


####################
# Database Helpers #
####################

def get_db():
    def to_dict(cursor, row):
        return dict((cursor.description[idx][0], value) for idx, value in enumerate(row))


    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)

    db.row_factory = to_dict

    return db


def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('../schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def query_db(query, args=()):
    t = time.process_time()

    cur = get_db().execute(query, args)
    r = cur.fetchall()
    cur.close()

    logger.info(f'query time: {time.process_time() - t}')

    return r


@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


####################
#      Helpers     #
####################
def get_or_404(id):
    try:
        res = query_db('select * from worlds where id = ?', [id])

        if len(res) == 0:
            raise Exception('404')

        return res
    except:
        abort(404, message=f"World ID {id} doesn't exist.")


####################
#       API        #
####################

# DAO

world_resource_fields = {
    'id': fields.Integer,
    'state': fields.Raw,
    'processed': fields.Raw,
}


class WorldDao(object):
    def __init__(self, id, state):
        self.id = id
        self.state = state


# World List
class WorldList(Resource):
    """
        Returns a list of existing "Worlds"

        @return Response
    """
    @marshal_with(world_resource_fields, envelope='data')
    def get(self):
        res = query_db('select * from worlds')

        for x, r in enumerate(res):
            p, _ = process_gravity(r['state'])
            res[x]['processed'] = to_text(p)

        print(res)

        return res, 200

    """
        Creates and processes a new "World"

        @body text/plain
        @return Response
    """
    def post(self, *args, **kwargs):
        data = request.get_data(as_text=True)
        print(data)

        if not all(x in ".: T\r\n" for x in data):
            return {'message': "invalid characters found"}, 400

        res, time = process_gravity(data)

        try:
            query_db("insert into worlds (state) values (?)", [
                data
            ])
            get_db().commit()


            return to_text(res), 200, {'Content-Type': 'plain/text'}

        except Exception as e:
            return abort(500, message=str(e))


# Single World Processing
class World(Resource):
    """
        Returns details of an existing "World", or a 404 if not found

        @arg id:integer
        @return Response
    """
    @marshal_with(world_resource_fields, envelope='data')
    def get(self, id):
        res = get_or_404(id)[0]

        return res, 200

    """
        Adds a new row to an existing "World"

        @arg id:integer
        @body text/plain
        @return: Response
    """
    def put(self, id, *args, **kwargs):
        res = get_or_404(id)[0]
        data = request.get_data(as_text=True)

        res, time = process_gravity(f'{data}\n{res["state"]}')

        try:
            query_db("update worlds set state = ?", [to_text(res)])
            get_db().commit()

            return to_text(res), 200, {'Content-Type': 'plain/text'}

        except Exception as e:
            return abort(500, message=str(e))

    """
        Deletes an existing "World"

        @arg id:integer
        @return: Response
    """
    def delete(self, id):
        get_or_404(id)

        try:
            query_db('delete from worlds where id = ?', [id])
            get_db().commit()

            return None, 200
        except Exception as e:
            return {'message': str(e)}, 500


api.add_resource(WorldList, '/')
api.add_resource(World, '/<int:id>')

if __name__ == '__main__':
    app.run(debug=True)

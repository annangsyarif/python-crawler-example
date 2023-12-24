from flask import Flask, jsonify, request
import json

from pipelines import CrawlingPipeline
from script.PostgreSql import PostgreSQLHandler

class FlaskApp:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.config['DEBUG'] = True

        with open("requirements/config.json") as f:
            self.config = json.load(f)

        self.postgres = PostgreSQLHandler(
            self.config["postgres"]["host"],
            self.config["postgres"]["port"],
            self.config["postgres"]["database"],
            self.config["postgres"]["user"],
            self.config["postgres"]["password"]
        )

        self.postgres.create_connection()

        self.app.add_url_rule('/get_data', 'get_data', self.get_data, methods=['GET'])
        self.app.add_url_rule('/update_data', 'update_data', self.run_pipelines, methods=['POST'])

    def get_data(self):
        data = self.postgres.read_data(
            "select * from pricerecommendation"
        )

        if data is None:
            data = {"result": "empty data"}
        else:
            data = data.to_dict(orient='records')


        return jsonify({'data': data})

    def run_pipelines(self):
        pipeline_ = CrawlingPipeline()
        pipeline_.run()
        result = {'status': 'success', 'message': 'Update Successfully'}
        return jsonify(result)

    def run(self):
        self.app.run(host='0.0.0.0', port=1234)

if __name__ == '__main__':
    app = FlaskApp()
    app.run()
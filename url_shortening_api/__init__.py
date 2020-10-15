from flask import Flask, current_app, session
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.ext.automap import automap_base
from flask import request,render_template, Response,redirect, url_for,jsonify
from flask_cors import CORS
import logging



db = SQLAlchemy()
Base = automap_base()


logger = logging.getLogger('URL_SHORTENING_API')
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler('./logs/url_shortening_api.log')
fh.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)

logger.addHandler(fh)

def create_app():
	app = Flask(__name__,  instance_relative_config=False)
	CORS(app)
	app.config.from_object('config.Config')
	#app.config['PROPAGATE_EXCEPTIONS'] = True
	app.url_map.strict_slashes = False

	with app.app_context():

		# from adda_api.models.user import user

		db.init_app(app)
		Base.prepare(db.engine, reflect=True)

		from url_shortening_api.routes import api_bp
		app.register_blueprint(api_bp, url_prefix='')

		# from adda_api.configuration.uploads_config import UploadsConfig
		# uc = UploadsConfig()
		# app.config["upload_imageDetails"], app.config["upload_media_path"], app.config["ACCEPTED_FILE_EXTENSION"] = uc.get_config()

		return app